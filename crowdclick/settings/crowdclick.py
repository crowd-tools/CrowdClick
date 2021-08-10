"""
settings that is specific to CrowdClick
"""
from crowdclick.settings.web3_config import Web3Config


ACCOUNT_OWNER_PUBLIC_KEY = env('ACCOUNT_OWNER_PUBLIC_KEY')

# Web3
AUTH_NONCE_CHOICES = '0123456789abcdef'
AUTH_NONCE_LENGTH = 32
LOGIN_REDIRECT_URL = '/'

WEB3_CONFIG = {
    key: Web3Config(value) for key, value in env.dict('WEB3_CONFIG').items()
}

WEB3_RETRY_COUNTDOWN = env.int('WEB3_RETRY_COUNTDOWN')
WEB3_RETRY = env.int('WEB3_RETRY')
