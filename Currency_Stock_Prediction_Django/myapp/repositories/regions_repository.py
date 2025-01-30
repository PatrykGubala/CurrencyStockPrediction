from typing import Optional, List
from myapp.models import Region

class RegionsRepository:
    def get_region_by_name(self, region_name: str) -> Optional[Region]:
        return Region.objects.filter(region_name=region_name).first()

    def get_region_by_id(self, region_id: int) -> Optional[Region]:
        try:
            return Region.objects.get(id=region_id)
        except Region.DoesNotExist:
            return None


    def get_all_regions(self) -> List[Region]:
        return list(Region.objects.all())


    def add_region(self, region_name: str) -> Region:
        region = Region(region_name=region_name)
        region.save()
        return region


    def update_region(self, region_id: int, new_name: str) -> Optional[Region]:
        region = self.get_region_by_id(region_id)
        if not region:
            return None
        region.region_name = new_name
        region.save()
        return region


    def delete_region(self, region_id: int) -> bool:
        region = self.get_region_by_id(region_id)
        if not region:
            return False
        region.delete()
        return True
