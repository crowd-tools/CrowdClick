# Dataclass for Web3 config
import typing
from dataclasses import dataclass

from eth_typing import Address, ChecksumAddress
from web3.types import ENS as Ens


@dataclass
class Web3Config:
    endpoints: set = ('https://rpc-mumbai.matic.today', )
    escrow_address: typing.Union[Address, str] = '0xdeadc0dedeadc0dedeadc0dedeadc0dedeadc0de'
    oracle_address: typing.Union[Address, str] = '0xdeadc0dedeadc0dedeadc0dedeadc0dedeadc0de'
    currency: str = 'MATIC'
    chain_id: int = 1
    public_key: typing.Union[Address, ChecksumAddress, Ens, str] = '0x9c76e3A23A87f624aAdEff7ca5e74103476eD11C'
    private_key: str = 'a' * 64
    default_gas_fee: int = 100000
