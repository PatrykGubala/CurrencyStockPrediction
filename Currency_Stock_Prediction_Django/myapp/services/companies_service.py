from typing import List
from myapp.repositories.companies_repository import CompanyRepository

class CompaniesService:
    def __init__(self):
        self.repository = CompanyRepository()

    def get_all_companies(self) -> List[dict]:
        companies = self.repository.get_all_companies()
        return [
            {
                "id": company.id,
                "symbol": company.company_symbol,
                "name": company.company_name,
                "logo_url": company.logo_url,
                "country_id": company.country.id if company.country else None
            }
            for company in companies
        ]

    def create_company(self, company_symbol: str, company_name: str, logo_url: str = None) -> dict:
        created_company = self.repository.add_company(company_symbol, company_name, logo_url=logo_url)
        return {
            "id": created_company.id,
            "symbol": created_company.company_symbol,
            "name": created_company.company_name,
            "logo_url": created_company.logo_url,
            "country_id": created_company.country.id if created_company.country else None
        }

    def delete_company(self, company_id: int) -> bool:
        return self.repository.delete_company(company_id)
