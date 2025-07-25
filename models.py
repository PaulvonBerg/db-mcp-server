# models.py

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any

"""
Pydantic models for a comprehensive Deutsche Bahn and mobility services API.
These models ensure that data from various sources (Timetables, RIS::Stations,
Parking, Facilities, and Shared Mobility) is correctly structured and validated.
"""

# --- Custom Validators ---

def _ensure_list_on_fieldset(fieldset):
    @field_validator(fieldset, mode='before')
    def _ensure_list(cls, v):
        if isinstance(v, dict):
            return [v]
        if v is None:
            return []
        return v
    return _ensure_list

# ======================================================================================
# Shared Models
# ======================================================================================

class Coordinate2D(BaseModel):
    latitude: float
    longitude: float

# ======================================================================================
# Timetables API Models (XML-based)
# ======================================================================================

class TripLabel(BaseModel):
    """A compound data type that contains common data items that characterize a Trip."""
    category: str = Field(..., alias="@c", description="Trip category, e.g., 'ICE' or 'RE'.")
    trip_number: str = Field(..., alias="@n", description="Trip/train number, e.g., '4523'.")
    owner: str = Field(..., alias="@o", description="A unique short-form to map a trip to a specific EVU.")

class Message(BaseModel):
    """A message that is associated with an event, a stop, or a trip."""
    id: str = Field(..., alias="@id", description="Message ID.")
    timestamp: str = Field(..., alias="@ts", description="Timestamp in 'YYMMddHHmm' format.")
    type: str = Field(..., alias="@t", description="Message type (e.g., 'h' for HIM).")
    internal_text: Optional[str] = Field(None, alias="@int")
    external_text: Optional[str] = Field(None, alias="@ext")
    category: Optional[str] = Field(None, alias="@cat")
    priority: Optional[str] = Field(None, alias="@pr")

class Event(BaseModel):
    """An event (arrival or departure) that is part of a stop."""
    _ensure_messages_is_list = _ensure_list_on_fieldset('messages')

    planned_time: Optional[str] = Field(None, alias="@pt")
    changed_time: Optional[str] = Field(None, alias="@ct")
    planned_platform: Optional[str] = Field(None, alias="@pp")
    changed_platform: Optional[str] = Field(None, alias="@cp")
    planned_path: Optional[str] = Field(None, alias="@ppth")
    changed_path: Optional[str] = Field(None, alias="@cpth")
    status: Optional[str] = Field(None, alias="@ps")
    changed_status: Optional[str] = Field(None, alias="@cs")
    line: Optional[str] = Field(None, alias="@l")
    messages: List[Message] = Field([], alias="m")

class TimetableStop(BaseModel):
    """A stop is a part of a Timetable."""
    _ensure_messages_is_list = _ensure_list_on_fieldset('messages')

    id: str = Field(..., alias="@id")
    trip_label: Optional[TripLabel] = Field(None, alias="tl")
    arrival: Optional[Event] = Field(None, alias="ar")
    departure: Optional[Event] = Field(None, alias="dp")
    messages: List[Message] = Field([], alias="m")

class Timetable(BaseModel):
    """A timetable is made of a set of TimetableStops."""
    _ensure_stops_is_list = _ensure_list_on_fieldset('stops')
    _ensure_messages_is_list = _ensure_list_on_fieldset('messages')

    station: str = Field(..., alias="@station")
    eva_number: int = Field(..., alias="@eva")
    stops: List[TimetableStop] = Field([], alias="s")
    messages: List[Message] = Field([], alias="m")

class TimetableStationData(BaseModel):
    """Represents station data from the Timetables API search."""
    eva_number: int
    ds100: str
    name: str
    platforms: str
    meta_stations: str

class TimetableStationSearchResponse(BaseModel):
    """Wrapper for multiple StationData objects from a Timetables API search."""
    _ensure_stations_is_list = _ensure_list_on_fieldset('stations')
    stations: List[TimetableStationData] = Field([], alias="station")

# ======================================================================================
# Station Data API (StaDa) Models
# ======================================================================================

class Address(BaseModel):
    """Represents a physical address."""
    street: Optional[str] = None
    houseNumber: Optional[str] = None
    postalCode: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None

class GeographicPoint(BaseModel):
    """Represents a GEOJSON point."""
    type: str
    coordinates: List[float]

class EvaNumber(BaseModel):
    """Represents an EVA number for a station."""
    number: int
    isMain: bool
    geographicCoordinates: Optional[GeographicPoint] = None


class StaDaStation(BaseModel):
    """Represents a single station from the Station Data v2 (StaDa) API."""
    number: int
    name: str
    mailingAddress: Address
    evaNumbers: List[EvaNumber]
    category: int
    hasParking: bool
    hasBicycleParking: bool
    hasLocalPublicTransport: bool
    hasPublicFacilities: bool
    hasLockerSystem: bool
    hasTaxiRank: bool
    hasTravelNecessities: bool
    hasSteplessAccess: Optional[str] = None
    hasMobilityService: Optional[str] = None
    hasWiFi: Optional[bool] = None
    hasTravelCenter: Optional[bool] = None
    hasRailwayMission: Optional[bool] = None
    hasDBLounge: Optional[bool] = None
    hasLostAndFound: Optional[bool] = None
    hasCarRental: Optional[bool] = None

class StationByPosition(BaseModel):
    """A simplified station model for geolocation searches."""
    name: str
    id: str
    lat: float
    lon: float
    distance_km: float

class SZentrale(BaseModel):
    """Represents a 3-S-Zentrale (service center) from the StaDa API."""
    number: int
    name: str
    publicPhoneNumber: Optional[str] = None
    publicFaxNumber: Optional[str] = None
    internalPhoneNumber: Optional[str] = None
    internalFaxNumber: Optional[str] = None
    email: Optional[str] = None
    address: Optional[Address] = None

class SZentraleQuery(BaseModel):
    """Wrapper for a list of SZentrale objects, including query metadata."""
    total: int
    limit: int
    offset: int
    result: List[SZentrale]

# ======================================================================================
# Parking Information API Models (DB Bahnpark)
# ======================================================================================

class ParkingAddress(BaseModel):
    city: Optional[str] = None
    streetAndNumber: Optional[str] = None
    zip: Optional[str] = None
    location: Optional[Coordinate2D] = None

class ParkingType(BaseModel):
    """Parking facility type information."""
    name: str
    nameEn: Optional[str] = None
    abbreviation: Optional[str] = None

class ParkingStation(BaseModel):
    """Station information for parking facility."""
    stationId: Dict[str, str]
    name: str
    distance: str

class ParkingCapacity(BaseModel):
    """Capacity information for parking facility."""
    type: str
    total: str

class ParkingFacility(BaseModel):
    """Represents a single parking facility."""
    id: str
    name: List[Dict[str, str]]
    address: ParkingAddress
    url: Optional[str] = None
    hasPrognosis: Optional[bool] = None
    type: Optional[ParkingType] = None
    station: Optional[ParkingStation] = None
    capacity: Optional[List[ParkingCapacity]] = None

class ParkingSearchResponse(BaseModel):
    embedded: List[ParkingFacility] = Field(..., alias="_embedded")

class Prognosis(BaseModel):
    """Represents a prognosis for a parking facility."""
    occupancy: Dict[str, Any]
    quality: int
    qualityMessage: str


# ======================================================================================
# Facility Status API Models (FaSta)
# ======================================================================================

class Facility(BaseModel):
    """Represents a single facility like an elevator or escalator."""
    equipmentnumber: int
    type: str
    description: Optional[str] = None
    state: str
    stateExplanation: Optional[str] = None
    geocoordX: Optional[float] = None  # Longitude (WGS84)
    geocoordY: Optional[float] = None  # Latitude (WGS84) 
    stationnumber: Optional[int] = None
    operatorname: Optional[str] = None

class FacilityStationResponse(BaseModel):
    """Response for a station's facilities."""
    stationnumber: int
    name: str
    facilities: List[Facility] = []

# ======================================================================================
# CallaBike TOMP API Models
# ======================================================================================

class TompStation(BaseModel):
    """Information about a single station from the TOMP API."""
    station_id: str
    name: str
    lat: float
    lon: float
    capacity: int



