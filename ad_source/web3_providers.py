import decimal
import json
import logging
import typing
from dataclasses import dataclass
from typing import (
    Any,
    Dict,
    Optional,
    Sequence,
    cast,
)

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from djmoney.contrib.exchange.models import get_rate
from ens import ENS
from eth_typing import Address, ChecksumAddress
from requests import ReadTimeout
from web3 import Web3
from web3._utils.empty import (
    empty,
)
from web3.contract import Contract
from web3.providers import (
    BaseProvider,
)
from web3.types import (  # noqa: F401
    Middleware,
    MiddlewareOnion,
    Wei,
)

from . import contracts, models

if typing.TYPE_CHECKING:  # pragma: no cover
    from crowdclick.settings import Web3Config


logger = logging.getLogger(__name__)


class Web3Client(Web3):
    def __init__(
        self,
        provider: Optional[BaseProvider] = None,
        middlewares: Optional[Sequence[Any]] = None,
        modules: Optional[Dict[str, Sequence[Any]]] = None,
        ens: ENS = cast(ENS, empty)
    ) -> None:
        super(Web3Client, self).__init__(provider, middlewares, modules, ens)
        self.host_url = getattr(self.provider, 'endpoint_uri', self.__class__.__name__)

    def __str__(self):
        return f'Web3 (host={self.host_url})'

    def __repr__(self):
        return self.__str__()


@dataclass
class Web3Provider:
    web3: {Web3, }
    contracts: {Contract, }
    admin_contracts: {Contract, }
    currency: str
    chain_id: int
    public_key: typing.Union[Address, ChecksumAddress, ENS]
    private_key: str
    default_gas_fee: int

    def create_reward(self, task: models.Task, reward: models.Reward) -> str:
        checksum_sender = Web3.toChecksumAddress(reward.sender.username)
        checksum_receiver = Web3.toChecksumAddress(reward.receiver.username)
        for web3, contract in zip(self.web3, self.contracts):
            try:
                estimated_gas = contract.functions.forwardRewards(
                    checksum_receiver,  # To
                    checksum_sender,  # From
                    str(task.uuid or '')  # task's uuid
                ).estimateGas({'from': self.public_key})
                w3_transaction = contract.functions.forwardRewards(
                    checksum_receiver,  # To
                    checksum_sender,  # From
                    str(task.uuid or '')  # task's uuid
                ).buildTransaction({
                    'chainId': self.chain_id,
                    'gas': estimated_gas,
                    'nonce': web3.eth.get_transaction_count(self.public_key)
                })
                txn_signed = web3.eth.account.sign_transaction(w3_transaction, private_key=self.private_key)
                tx_hash_hex = web3.eth.sendRawTransaction(txn_signed.rawTransaction)  # tx_hash
                tx_hash = tx_hash_hex.hex()
                return tx_hash
            except (TypeError, ValueError, ReadTimeout):
                logger.error(f'ERROR in `create_reward` - {web3}')
        raise StopIteration()

    def check_balance(self, task: models.Task) -> typing.Tuple[bool, typing.Union[int, decimal.Decimal]]:
        checksum_address = Web3.toChecksumAddress(task.user.username)
        for web3, contract in zip(self.web3, self.contracts):
            try:
                response = contract.functions.lookupTask(
                    str(task.uuid or ''),
                    checksum_address,
                ).call()
                task_budget, task_reward, current_budget, url, is_active, *_ = response
                current_budget_eth = web3.fromWei(current_budget, 'ether')
                current_budget_usd = get_rate(source=self.currency, target='USD') * current_budget_eth
                return is_active, current_budget_usd
            except (TypeError, ValueError, ReadTimeout):
                logger.error(f'ERROR in `check_balance` - {web3}')
        raise StopIteration()

    def push_underlying_usd_price(self):
        rate = get_rate(source=self.currency, target='USD')
        for web3, admin_contract in zip(self.web3, self.admin_contracts):
            try:
                value_uint = web3.toWei(rate, 'ether')
                estimated_gas = admin_contract.functions.adminPushUnderlyingUSDPrice(
                    value_uint
                ).estimateGas({'from': self.public_key})
                w3_transaction = admin_contract.functions.adminPushUnderlyingUSDPrice(value_uint).buildTransaction({
                    'chainId': self.chain_id,
                    'gas': estimated_gas,
                    'nonce': web3.eth.get_transaction_count(self.public_key)
                })
                txn_signed = web3.eth.account.sign_transaction(w3_transaction, private_key=self.private_key)
                tx_hash_hex = web3.eth.sendRawTransaction(txn_signed.rawTransaction)  # tx_hash
                tx_hash = tx_hash_hex.hex()
                result = admin_contract.functions.getUnderlyingUsdPriceFeed().call()
                return value_uint, result, tx_hash
            except TypeError:
                logger.error(f'ERROR in `check_balance` - {web3}')
        raise StopIteration()


class Web3ProviderStorage(dict):
    def __missing__(self, key):
        config: Web3Config = settings.WEB3_CONFIG[key]

        if key not in settings.WEB3_CONFIG:  # pragma: no cover
            raise ImproperlyConfigured(f"Requested Web3 provider {key} but \
            is missing in settings.WEB3_CONFIG")
        if settings.TEST:
            providers = {Web3Client(Web3.EthereumTesterProvider()), }
        else:  # pragma: no cover
            providers = {Web3Client(Web3.HTTPProvider(endpoint)) for endpoint in config.endpoints}

        if not providers:
            raise ImproperlyConfigured(f"No providers for config {key}")

        escrow_contract_abi = json.loads(contracts.escrow_contract_abi)
        oracle_contract_abi = json.loads(contracts.oracle_contract_abi)
        contract_instances = {provider.eth.contract(abi=escrow_contract_abi, address=config.escrow_address)
                              for provider in providers}
        admin_contract_instances = {provider.eth.contract(abi=oracle_contract_abi, address=config.oracle_address)
                                    for provider in providers}
        w3_provider = Web3Provider(
            web3=providers,
            contracts=contract_instances,
            admin_contracts=admin_contract_instances,
            currency=config.currency,
            chain_id=config.chain_id,
            public_key=config.public_key,
            private_key=config.private_key,
            default_gas_fee=config.default_gas_fee
        )
        self[key] = w3_provider
        return w3_provider


web3_storage = Web3ProviderStorage()
