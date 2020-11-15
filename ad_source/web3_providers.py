import json
import typing

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from eth_typing import Address, ChecksumAddress
from web3 import Web3
from web3.contract import Contract
from web3.types import ENS

from . import contract


class Web3Provider(typing.NamedTuple):
    web3: Web3
    contract: Contract
    public_key: typing.Union[Address, ChecksumAddress, ENS]
    private_key: str


class Web3ProviderStorage(dict):
    def __missing__(self, key):
        config: settings.web3_config_namedtuple = settings.WEB3_CONFIG[key]

        if key not in settings.WEB3_CONFIG:
            raise ImproperlyConfigured(f"Requested Web3 provider {key} but \
            is missing in settings.WEB3_CONFIG")
        if settings.TEST:
            provider = Web3(Web3.EthereumTesterProvider())
        else:
            provider = Web3(Web3.HTTPProvider(config.endpoint))

        contract_spec = json.loads(contract.abi)
        contract_abi = contract_spec["abi"]
        contract_instance = provider.eth.contract(abi=contract_abi, address=config.contract_address)
        w3_provider = Web3Provider(
            web3=provider,
            contract=contract_instance,
            public_key=config.public_key,
            private_key=config.private_key,
        )
        self[key] = w3_provider
        return w3_provider
