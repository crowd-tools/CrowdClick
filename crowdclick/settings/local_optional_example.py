from crowdclick.settings import Web3Config

WEB3_CONFIG = {
    'mumbai': Web3Config(
        endpoint='https://rpc-mumbai.matic.today',
        contract_address='0xdeadc0dedeadc0dedeadc0dedeadc0dedeadc0de',
        chain_id=1,
        public_key='0x9c76e3A23A87f624aAdEff7ca5e74103476eD11C',
        private_key='a' * 64,
        default_gas_fee=100000,
    ),
    # 'goerli', ...
}
