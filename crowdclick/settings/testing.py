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
        contract_address='0xb312aC99b9207286addf566B5BB08f7552aF0b15',
        chain_id=1,
        public_key='0x9c76e3A23A87f624aAdEff7ca5e74103476eD11C',
        private_key='a' * 64,
        default_gas_fee=2000000,
    ),
    # 'goerli', ...
}
