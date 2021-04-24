from crowdclick.settings import Web3Config

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache'
    }
}

WEB3_CONFIG = {
    'goerli': Web3Config(
        endpoint='https://goerli.infura.io/v3/' + 'a' * 32,
        escrow_address='0x5f9A718D919463443A74A67Deb1aF056790C0ca0',
        oracle_address='0x2020b5644C4Ce52411E57cfD9D899a766Fc1E103',
        currency='ETH',
        chain_id=1,
        public_key='0x9c76e3A23A87f624aAdEff7ca5e74103476eD11C',
        private_key='a' * 64,
        default_gas_fee=2000000,
    ),
    # 'goerli', ...
}
ETH2USD_URL = 'https://extenral_services_has_to_be_mocked/?fsym={from_symbol}&tsyms={to_symbol}'
