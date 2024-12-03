from typing import List, Optional
from app.models.models import Region
from app.models.database import db

class RegionsRepository:
    def get_region_by_name(self, region_name: str) -> Optional[Region]:
        return Region.query.filter_by(region_name=region_name).first()

    def get_region_by_id(self, region_id: int) -> Optional[Region]:
        return Region.query.get(region_id)

    def get_all_regions(self) -> List[Region]:
        return Region.query.all()

    def add_region(self, region_name: str) -> Region:
        region = Region(region_name=region_name)
        db.session.add(region)
        db.session.commit()
        return region

    def update_region(self, region_id: int, new_name: str) -> Optional[Region]:
        region = self.get_region_by_id(region_id)
        if region:
            region.region_name = new_name
            db.session.commit()
        return region

    def delete_region(self, region_id: int) -> bool:
        region = self.get_region_by_id(region_id)
        if region:
            db.session.delete(region)
            db.session.commit()
            return True
        return False