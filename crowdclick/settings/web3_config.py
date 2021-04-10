# Dataclass for Web3 config
import typing
from dataclasses import dataclass

from eth_typing import Address, ChecksumAddress
from web3.types import ENS as Ens


@dataclass
class Web3Config:
    endpoint: str = 'https://rpc-mumbai.matic.today'
    contract_address: str = '0xdeadc0dedeadc0dedeadc0dedeadc0dedeadc0de'
    chain_id: int = 1
    public_key: typing.Union[Address, ChecksumAddress, Ens, str] = '0x9c76e3A23A87f624aAdEff7ca5e74103476eD11C'
    private_key: str = 'a' * 64
    default_gas_fee: int = 100000
