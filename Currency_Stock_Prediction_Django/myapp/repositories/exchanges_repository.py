from typing import List, Optional
from myapp.models import Exchange, Country


class ExchangeRepository:
    def get_all_exchanges(self) -> List[Exchange]:
        return list(Exchange.objects.all())

    def get_exchange_by_id(self, exchange_id: int) -> Optional[Exchange]:
        return Exchange.objects.filter(pk=exchange_id).first()

    def get_exchange_by_name(self, name: str) -> Optional[Exchange]:
        return Exchange.objects.filter(name__iexact=name).first()

    def add_exchange(self, name: str, country: Optional[Country] = None) -> Exchange:
        exchange = Exchange(name=name, country=country)
        exchange.save()
        return exchange

    def delete_exchange(self, exchange_id: int) -> bool:
        exchange = Exchange.objects.filter(pk=exchange_id).first()
        if exchange:
            exchange.delete()
            return True
        return False
