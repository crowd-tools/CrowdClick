import json
import typing

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from eth_typing import Address, ChecksumAddress
from web3 import Web3
from web3.contract import Contract
from web3.types import ENS

from . import contract, models

if typing.TYPE_CHECKING:  # pragma: no cover
    from crowdclick.settings.defaults import web3_config_namedtuple


class Web3Provider(typing.NamedTuple):
    web3: Web3
    contract: Contract
    chain_id: int
    public_key: typing.Union[Address, ChecksumAddress, ENS]
    private_key: str
    default_gas_fee: int

    def create_reward(self, task: models.Task, reward: models.Reward) -> str:
        checksummed_sender = Web3.toChecksumAddress(reward.sender.username)
        checksummed_receiver = Web3.toChecksumAddress(reward.receiver.username)
        w3_transaction = self.contract.functions.forwardRewards(
            checksummed_receiver,  # To
            checksummed_sender,  # From
            task.website_link  # task's website url
        ).buildTransaction({
            'chainId': self.chain_id,
            'gas': self.default_gas_fee,
            'gasPrice': self.web3.toWei('1', 'gwei'),
            'nonce': self.web3.eth.getTransactionCount(self.public_key)
        })
        txn_signed = self.web3.eth.account.sign_transaction(w3_transaction, private_key=self.private_key)
        tx_hash_hex = self.web3.eth.sendRawTransaction(txn_signed.rawTransaction)  # tx_hash
        tx_hash = tx_hash_hex.hex()
        return tx_hash

    def check_balance(self):
        ...


class Web3ProviderStorage(dict):
    def __missing__(self, key):
        config: web3_config_namedtuple = settings.WEB3_CONFIG[key]

        if key not in settings.WEB3_CONFIG:  # pragma: no cover
            raise ImproperlyConfigured(f"Requested Web3 provider {key} but \
            is missing in settings.WEB3_CONFIG")
        if settings.TEST:
            provider = Web3(Web3.EthereumTesterProvider())
        else:  # pragma: no cover
            provider = Web3(Web3.HTTPProvider(config.endpoint))

        contract_spec = json.loads(contract.abi)
        contract_abi = contract_spec["abi"]
        contract_instance = provider.eth.contract(abi=contract_abi, address=config.contract_address)
        w3_provider = Web3Provider(
            web3=provider,
            contract=contract_instance,
            chain_id=config.chain_id,
            public_key=config.public_key,
            private_key=config.private_key,
            default_gas_fee=config.default_gas_fee
        )
        self[key] = w3_provider
        return w3_provider
