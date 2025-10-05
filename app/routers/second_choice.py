from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from second_choice_updater import (
    update_second_choice as update_second_choice_public,
    get_current_second_choice as get_current_second_choice_public,
    clear_second_choice as clear_second_choice_public,
    get_second_choice_history as get_second_choice_history_public,
)
from second_choice_updater_password import (
    update_second_choice as update_second_choice_auth,
    get_current_second_choice as get_current_second_choice_auth,
    clear_second_choice as clear_second_choice_auth,
    get_second_choice_history as get_second_choice_history_auth,
)


router = APIRouter(prefix="/api/v1", tags=["second_choice"])


class SecondChoiceUpdatePublicReq(BaseModel):
    room_number: str
    building_id: str
    date1: str
    time1: str
    date2: str
    time2: str
    date3: Optional[str] = None
    time3: Optional[str] = None
    waku_pattern_id: Optional[int] = None


class SecondChoiceUpdateAuthReq(BaseModel):
    room_number: str
    password: str
    building_id: str
    date1: str
    time1: str
    date2: str
    time2: str
    date3: Optional[str] = None
    time3: Optional[str] = None
    waku_pattern_id: Optional[int] = None


class RoomBuildingReq(BaseModel):
    room_number: str
    building_id: str


class RoomPasswordBuildingReq(BaseModel):
    room_number: str
    password: str
    building_id: str


@router.post("/public/second-choice/update")
def second_choice_update_public(req: SecondChoiceUpdatePublicReq):
    return update_second_choice_public(
        req.room_number, req.building_id,
        req.date1, req.time1,
        req.date2, req.time2,
        req.date3 or "", req.time3 or "",
        req.waku_pattern_id,
    )


@router.get("/public/second-choice/current")
def second_choice_current_public(room_number: str, building_id: str):
    return get_current_second_choice_public(room_number, building_id)


@router.post("/public/second-choice/clear")
def second_choice_clear_public(req: RoomBuildingReq):
    return clear_second_choice_public(req.room_number, req.building_id)


@router.get("/public/second-choice/history")
def second_choice_history_public(room_number: str, building_id: str, limit: int = 10):
    return get_second_choice_history_public(room_number, building_id, limit)


@router.post("/auth/second-choice/update")
def second_choice_update_auth(req: SecondChoiceUpdateAuthReq):
    return update_second_choice_auth(
        req.room_number, req.password, req.building_id,
        req.date1, req.time1,
        req.date2, req.time2,
        req.date3 or "", req.time3 or "",
        req.waku_pattern_id,
    )


@router.get("/auth/second-choice/current")
def second_choice_current_auth(room_number: str, password: str, building_id: str):
    return get_current_second_choice_auth(room_number, password, building_id)


@router.post("/auth/second-choice/clear")
def second_choice_clear_auth(req: RoomPasswordBuildingReq):
    return clear_second_choice_auth(req.room_number, req.password, req.building_id)


@router.get("/auth/second-choice/history")
def second_choice_history_auth(room_number: str, password: str, building_id: str, limit: int = 10):
    return get_second_choice_history_auth(room_number, password, building_id, limit)
