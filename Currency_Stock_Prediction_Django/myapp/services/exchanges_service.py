from typing import List
from myapp.repositories.exchanges_repository import ExchangeRepository

class ExchangesService:
    def __init__(self):
        self.repository = ExchangeRepository()

    def get_all_exchanges(self) -> List[dict]:
        exchanges = self.repository.get_all_exchanges()
        return [
            {
                "id": exchange.id,
                "name": exchange.name,
                "country_id": exchange.country.id if exchange.country else None
            }
            for exchange in exchanges
        ]

    def create_exchange(self, name: str) -> dict:
        created_exchange = self.repository.add_exchange(name)
        return {
            "id": created_exchange.id,
            "name": created_exchange.name,
            "country_id": created_exchange.country.id if created_exchange.country else None
        }

    def delete_exchange(self, exchange_id: int) -> bool:
        return self.repository.delete_exchange(exchange_id)
