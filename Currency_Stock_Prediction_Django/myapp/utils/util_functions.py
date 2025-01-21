from typing import Optional, List, Union
from decimal import Decimal, ROUND_DOWN


def normalize_decimal( value: Union[str, float, Decimal]) -> Decimal:
    if isinstance(value, float):
        value = str(value)
    return Decimal(value).quantize(Decimal('0.00000000'), rounding=ROUND_DOWN)