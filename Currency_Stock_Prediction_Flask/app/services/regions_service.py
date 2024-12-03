from typing import List, Optional
from app.repositories.regions_repository import RegionsRepository
from app.models.dtos import RegionDTO
from app.utils.logger import setup_logger

class RegionsService:
    def __init__(self):
        self.regions_repo = RegionsRepository()
        self.logger = setup_logger(__name__)

    def get_all_regions_dto(self) -> List[RegionDTO]:
        regions = self.regions_repo.get_all_regions()
        regions_dto = []
        for region in regions:
            region_dict: RegionDTO = {
                "id": region.id,
                "region_name": region.region_name
            }
            regions_dto.append(region_dict)
        return regions_dto

    def get_region_by_id_dto(self, region_id: int) -> Optional[RegionDTO]:
        region = self.regions_repo.get_region_by_id(region_id)
        if not region:
            return None
        region_dto: RegionDTO = {
            "id": region.id,
            "region_name": region.region_name
        }
        return region_dto

    def get_region_by_name_dto(self, region_name: str) -> Optional[RegionDTO]:
        region = self.regions_repo.get_region_by_name(region_name)
        if not region:
            return None
        region_dto: RegionDTO = {
            "id": region.id,
            "region_name": region.region_name
        }
        return region_dto

    def add_region(self, region_name: str) -> RegionDTO:
        try:
            self.logger.info(f"Adding region: {region_name}")
            existing_region = self.regions_repo.get_region_by_name(region_name)
            if not existing_region:
                region = self.regions_repo.add_region(region_name)
                self.logger.info(f"Region {region_name} added successfully.")
            else:
                region = existing_region
                self.logger.info(f"Region {region_name} already exists.")
            region_dto: RegionDTO = {
                "id": region.id,
                "region_name": region.region_name
            }
            return region_dto
        except Exception as e:
            self.logger.error(f"Error adding region {region_name}: {e}")
            raise

    def update_region(self, region_id: int, new_name: str) -> Optional[RegionDTO]:
        try:
            self.logger.info(f"Updating region ID {region_id} to new name: {new_name}")
            region = self.regions_repo.update_region(region_id, new_name)
            if not region:
                self.logger.warning(f"Region with ID {region_id} not found.")
                return None
            region_dto: RegionDTO = {
                "id": region.id,
                "region_name": region.region_name
            }
            return region_dto
        except Exception as e:
            self.logger.error(f"Error updating region ID {region_id}: {e}")
            raise

    def delete_region(self, region_id: int) -> bool:
        try:
            self.logger.info(f"Deleting region ID {region_id}")
            result = self.regions_repo.delete_region(region_id)
            if result:
                self.logger.info(f"Region ID {region_id} deleted successfully.")
            else:
                self.logger.warning(f"Region ID {region_id} not found.")
            return result
        except Exception as e:
            self.logger.error(f"Error deleting region ID {region_id}: {e}")
            raise