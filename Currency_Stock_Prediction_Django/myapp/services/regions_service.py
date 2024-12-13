from typing import List, Optional
from myapp.repositories.regions_repository import RegionsRepository

class RegionsService:
    def __init__(self):
        self.regions_repo = RegionsRepository()
    def get_all_regions_dto(self) -> List[dict]:
        regions = self.regions_repo.get_all_regions()
        return [{"id": r.id, "region_name": r.region_name} for r in regions]
    def get_region_by_id_dto(self, region_id: int) -> Optional[dict]:
        r = self.regions_repo.get_region_by_id(region_id)
        if not r:
            return None
        return {"id": r.id, "region_name": r.region_name}
    def get_region_by_name_dto(self, region_name: str) -> Optional[dict]:
        r = self.regions_repo.get_region_by_name(region_name)
        if not r:
            return None
        return {"id": r.id, "region_name": r.region_name}
    def add_region(self, region_name: str) -> dict:
        existing_region = self.regions_repo.get_region_by_name(region_name)
        if not existing_region:
            region = self.regions_repo.add_region(region_name)
        else:
            region = existing_region
        return {"id": region.id, "region_name": region.region_name}
    def update_region(self, region_id: int, new_name: str) -> Optional[dict]:
        region = self.regions_repo.update_region(region_id, new_name)
        if not region:
            return None
        return {"id": region.id, "region_name": region.region_name}
    def delete_region(self, region_id: int) -> bool:
        return self.regions_repo.delete_region(region_id)
