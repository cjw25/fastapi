from fastapi import APIRouter, Request, status, UploadFile, Form, HTTPException, File, Depends
from fastapi.responses import Response
from bson import ObjectId
from pymongo import ReturnDocument

from cloudinary import uploader
import cloudinary

from config import BaseConfig
from models import CarCollection, CarModel, UpdateCarModel
from authentication import AuthHandler

settings = BaseConfig()
router = APIRouter()
CARS_PER_PAGE = 10

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_SECRET_KEY,
)

auth_handler = AuthHandler()

@router.post(
    "/",
    response_description="Add new car with picture",
    response_model=CarModel,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
)
async def add_car_with_picture(
    request: Request,
    brand: str = Form(...),
    make: str = Form(...),
    year: int = Form(...),
    cm3: int = Form(...),
    km: int = Form(...),
    price: int = Form(...),
    picture: UploadFile = File(...),
    user: dict =Depends(auth_handler.auth_wrapper),
):
    cars = request.app.db["cars"]

    try:
        cloudinary_image = cloudinary.uploader.upload(
            picture.file,
            folder="FARM2",
            crop="fill",
            width=800
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cloudinary upload failed: {str(e)}")

    picture_url = cloudinary_image["url"]

    car = CarModel(
        brand=brand,
        make=make,
        year=year,
        cm3=cm3,
        km=km,
        price=price,
        picture_url=picture_url,
        user_id=user["user_id"],
    )

    document = car.model_dump(by_alias=True, exclude=["id"])
    inserted = await cars.insert_one(document)
    saved = await cars.find_one({"_id": inserted.inserted_id})
    return saved


@router.get(
    "/{id}",
    response_description="Get a single car by id",
    response_model=CarModel,
    response_model_by_alias=False,
)
async def get_car(id: str, request: Request):
    cars = request.app.db["cars"]

    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID format")

    car = await cars.find_one({"_id": ObjectId(id)})
    if car is None:
        raise HTTPException(status_code=404, detail="Car not found")

    return car


@router.get(
    "/",
    response_description="List all cars",
    response_model=CarCollection,
    response_model_by_alias=False,
)
async def list_cars(request: Request):
    cars = request.app.db["cars"]
    results = []
    cursor = cars.find()
    async for document in cursor:
        results.append(CarModel(**document))
    return CarCollection(cars=results)