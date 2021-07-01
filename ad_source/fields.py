from djmoney.models.fields import MoneyField as DefaultMoneyField


class MoneyField(DefaultMoneyField):
    """ Stores value in tokens (ETH, BTC, ...), represents in USD """
    pass
