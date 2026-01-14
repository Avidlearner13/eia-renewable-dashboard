"""Data models for renewable energy data."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from .base import BaseModel


class RenewableSource(str, Enum):
    """Renewable energy source types."""

    SOLAR = "SUN"
    WIND = "WND"
    HYDRO = "WAT"
    GEOTHERMAL = "GEO"
    BIOMASS = "BIO"
    NUCLEAR = "NUC"
    OTHER = "OTH"

    @classmethod
    def all_renewable(cls) -> List["RenewableSource"]:
        """Get all renewable sources (excluding nuclear)."""
        return [cls.SOLAR, cls.WIND, cls.HYDRO, cls.GEOTHERMAL, cls.BIOMASS]

    @classmethod
    def get_by_code(cls, code: str) -> Optional["RenewableSource"]:
        """Get source by EIA code."""
        for source in cls:
            if source.value == code:
                return source
        return None


@dataclass
class FuelTypeData(BaseModel):
    """Real-time generation data by fuel type."""

    period: str
    respondent: str
    respondent_name: str
    fuel_type: str
    fuel_type_description: str
    value: float
    units: str = "megawatthours"
    raw_data: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FuelTypeData":
        """Create from API response dictionary."""
        return cls(
            period=data.get("period", ""),
            respondent=data.get("respondent", ""),
            respondent_name=data.get("respondent-name", ""),
            fuel_type=data.get("fueltype", ""),
            fuel_type_description=data.get("type-name", ""),
            value=float(data.get("value", 0) or 0),
            units=data.get("value-units", "megawatthours"),
            raw_data=data,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "period": self.period,
            "respondent": self.respondent,
            "respondent_name": self.respondent_name,
            "fuel_type": self.fuel_type,
            "fuel_type_description": self.fuel_type_description,
            "value": self.value,
            "units": self.units,
        }

    @property
    def is_renewable(self) -> bool:
        """Check if this is a renewable source."""
        renewable_codes = {s.value for s in RenewableSource.all_renewable()}
        return self.fuel_type in renewable_codes


@dataclass
class GeneratorCapacity(BaseModel):
    """Operating generator capacity data."""

    period: str
    state: str
    state_description: str
    sector: str
    sector_description: str
    entity_id: str
    entity_name: str
    plant_id: str
    plant_name: str
    generator_id: str
    technology: str
    energy_source: str
    energy_source_description: str
    prime_mover: str
    nameplate_capacity_mw: float
    net_summer_capacity_mw: float
    net_winter_capacity_mw: float
    status: str
    operating_year: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    raw_data: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GeneratorCapacity":
        """Create from API response dictionary."""
        return cls(
            period=data.get("period", ""),
            state=data.get("stateid", ""),
            state_description=data.get("stateName", ""),
            sector=data.get("sector", ""),
            sector_description=data.get("sectorName", ""),
            entity_id=data.get("entityid", ""),
            entity_name=data.get("entityName", ""),
            plant_id=data.get("plantid", ""),
            plant_name=data.get("plantName", ""),
            generator_id=data.get("generatorid", ""),
            technology=data.get("technology", ""),
            energy_source=data.get("energy_source_code", ""),
            energy_source_description=data.get("energy_source_desc", ""),
            prime_mover=data.get("prime_mover_code", ""),
            nameplate_capacity_mw=float(data.get("nameplate-capacity-mw", 0) or 0),
            net_summer_capacity_mw=float(data.get("net-summer-capacity-mw", 0) or 0),
            net_winter_capacity_mw=float(data.get("net-winter-capacity-mw", 0) or 0),
            operating_year=int(data["operating-year-month"][:4]) if data.get("operating-year-month") else None,
            status=data.get("status", ""),
            latitude=float(data["latitude"]) if data.get("latitude") else None,
            longitude=float(data["longitude"]) if data.get("longitude") else None,
            raw_data=data,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "period": self.period,
            "state": self.state,
            "state_description": self.state_description,
            "plant_name": self.plant_name,
            "technology": self.technology,
            "energy_source": self.energy_source,
            "nameplate_capacity_mw": self.nameplate_capacity_mw,
            "net_summer_capacity_mw": self.net_summer_capacity_mw,
            "operating_year": self.operating_year,
            "latitude": self.latitude,
            "longitude": self.longitude,
        }

    @property
    def is_renewable(self) -> bool:
        """Check if generator uses renewable energy source."""
        renewable_techs = {"Solar", "Wind", "Hydroelectric", "Geothermal", "Biomass", "Wood"}
        return any(tech.lower() in self.technology.lower() for tech in renewable_techs)


@dataclass
class ElectricityGeneration(BaseModel):
    """Monthly/annual electricity generation data."""

    period: str
    location: str
    location_description: str
    sector: str
    sector_description: str
    fuel_type: str
    fuel_type_description: str
    generation_mwh: float
    raw_data: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ElectricityGeneration":
        """Create from API response dictionary."""
        return cls(
            period=data.get("period", ""),
            location=data.get("location", data.get("stateid", "")),
            location_description=data.get("stateDescription", ""),
            sector=data.get("sectorid", ""),
            sector_description=data.get("sectorDescription", ""),
            fuel_type=data.get("fueltypeid", ""),
            fuel_type_description=data.get("fueltypeDescription", ""),
            generation_mwh=float(data.get("generation", 0) or 0),
            raw_data=data,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "period": self.period,
            "location": self.location,
            "fuel_type": self.fuel_type,
            "generation_mwh": self.generation_mwh,
        }


@dataclass
class StateRenewableProfile(BaseModel):
    """State-level renewable energy profile."""

    state: str
    state_name: str
    year: int
    solar_capacity_mw: float = 0
    wind_capacity_mw: float = 0
    hydro_capacity_mw: float = 0
    solar_generation_mwh: float = 0
    wind_generation_mwh: float = 0
    hydro_generation_mwh: float = 0
    total_renewable_capacity_mw: float = 0
    total_renewable_generation_mwh: float = 0
    raw_data: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StateRenewableProfile":
        """Create from dictionary."""
        return cls(
            state=data.get("state", ""),
            state_name=data.get("state_name", ""),
            year=data.get("year", 0),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "state": self.state,
            "state_name": self.state_name,
            "year": self.year,
            "solar_capacity_mw": self.solar_capacity_mw,
            "wind_capacity_mw": self.wind_capacity_mw,
            "total_renewable_capacity_mw": self.total_renewable_capacity_mw,
        }

    @property
    def renewable_percentage(self) -> float:
        """Calculate renewable as percentage of total (if available)."""
        if self.raw_data.get("total_generation"):
            total = float(self.raw_data["total_generation"])
            if total > 0:
                return (self.total_renewable_generation_mwh / total) * 100
        return 0.0
