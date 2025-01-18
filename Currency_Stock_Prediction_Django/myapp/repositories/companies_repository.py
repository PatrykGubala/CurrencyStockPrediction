from typing import List, Optional
from myapp.models import Company

class CompanyRepository:
    def get_all_companies(self) -> List[Company]:
        return list(Company.objects.all())

    def get_company_by_id(self, company_id: int) -> Optional[Company]:
        return Company.objects.filter(pk=company_id).first()

    def get_company_by_symbol(self, company_symbol: str) -> Optional[Company]:
        return Company.objects.filter(company_symbol__iexact=company_symbol).first()

    def add_company(self, company_symbol: str, company_name: str, logo_url: str = None) -> Company:
        if company_name and len(company_name) > 100:
            company_name = company_name[:100]
        company = Company(company_symbol=company_symbol, company_name=company_name, logo_url=logo_url)
        company.save()
        return company

    def delete_company(self, company_id: int) -> bool:
        company = Company.objects.filter(pk=company_id).first()
        if company:
            company.delete()
            return True
        return False