from typing import Optional, List
from bson import ObjectId

from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    GetCoreSchemaHandler,
    field_validator,
    field_serializer,
)
from pydantic_core import core_schema
from pydantic import field_serializer


class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, source, handler: GetCoreSchemaHandler):
        return core_schema.no_info_after_validator_function(
            cls._validate,
            core_schema.union_schema([
                core_schema.is_instance_schema(ObjectId),
                core_schema.str_schema(),
            ]),
        )

    @classmethod
    def _validate(cls, v):
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str) and ObjectId.is_valid(v):
            return ObjectId(v)
        raise ValueError("Invalid ObjectId")


class CarModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    brand: str
    make: str
    year: int = Field(..., gt=1900, lt=2025)
    cm3: int = Field(..., gt=0, lt=5000)
    km: int = Field(..., gt=0, lt=500_000)
    price: int = Field(..., gt=0, lt=500_000_000)
    user_id: str = Field(...)
    picture_url: Optional[str] = None

    @field_serializer("id")
    def _ser_id(self, v):
        return str(v) if v is not None else None

    @field_validator("brand", "make", mode="before")
    @classmethod
    def normalize_text(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return str(v).strip().title()

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "brand": "Ford",
                "make": "Fiesta",
                "year": 2019,
                "cm3": 1500,
                "km": 120_000,
                "price": 50_000,
                "picture_url": "https://res.cloudinary.com/demo/image/upload/v1234567890/fiesta.jpg",
            }
        },
    )


class UpdateCarModel(BaseModel):
    brand: Optional[str] = None
    make: Optional[str] = None
    year: Optional[int] = Field(default=None, gt=1900, lt=2025)
    cm3: Optional[int] = Field(default=None, gt=0, lt=5000)
    km: Optional[int] = Field(default=None, gt=0, lt=500_000)
    price: Optional[int] = Field(default=None, gt=0, lt=500_000_000)
    picture_url: Optional[str] = None

    @field_validator("brand", "make", mode="before")
    @classmethod
    def normalize_text(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return str(v).strip().title()

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )


class CarCollection(BaseModel):
    cars: List[CarModel]

class UserModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    username: str = Field(..., min_length=3, max_length=15)
    password: str = Field(...)

    @field_serializer("id")
    def _ser_id(self, v):
        return str(v) if v is not None else None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )


class LoginModel(BaseModel):
    username: str = Field(...)
    password: str = Field(...)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )


class CurrentUserModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    username: str = Field(..., min_length=3, max_length=15)

    @field_serializer("id")
    def _ser_id(self, v):
        return str(v) if v is not None else None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )