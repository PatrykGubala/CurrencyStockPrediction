from typing import List, Optional, TypedDict

class CurrencyDTO(TypedDict):
    id: int
    code: str
    name: str
    symbol: Optional[str]

class RegionDTO(TypedDict):
    id: int
    region_name: str

class CountryDTO(TypedDict):
    id: int
    country_code: str
    country_name: str
    regions: List[RegionDTO]
    currencies: List[CurrencyDTO]

class CurrencyPairDTO(TypedDict):
    id: int
    base_currency: CurrencyDTO
    target_currency: CurrencyDTO