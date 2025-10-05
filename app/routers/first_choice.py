from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional

from first_choice_updater import update_first_choice as update_first_choice_public
from first_choice_updater import get_available_slots as get_available_slots_public
from first_choice_updater_password import update_first_choice as update_first_choice_auth


router = APIRouter(prefix="/api/v1", tags=["first_choice"])


class FirstChoiceUpdatePublicReq(BaseModel):
    room_number: str = Field(...)
    building_id: str = Field(...)
    new_datetime: str = Field(..., description="YYYY-MM-DD HH:MM")


class FirstChoiceUpdateAuthReq(BaseModel):
    room_number: str = Field(...)
    password: str = Field(...)
    building_id: str = Field(...)
    new_datetime: str = Field(..., description="YYYY-MM-DD HH:MM")


@router.post("/public/first-choice/update")
def first_choice_update_public(req: FirstChoiceUpdatePublicReq):
    return update_first_choice_public(req.room_number, req.building_id, req.new_datetime)


@router.get("/public/first-choice/slots")
def first_choice_slots(building_id: str, date: str):
    return get_available_slots_public(building_id, date)


@router.post("/auth/first-choice/update")
def first_choice_update_auth(req: FirstChoiceUpdateAuthReq):
    return update_first_choice_auth(req.room_number, req.password, req.building_id, req.new_datetime)
