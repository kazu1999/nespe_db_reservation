from fastapi import APIRouter

from get_building_name import get_building_name as get_building_name_public
from get_building_name_password import get_building_name as get_building_name_auth


router = APIRouter(prefix="/api/v1", tags=["building"])


@router.get("/public/building/name")
def building_name_public(client_cd: str):
    name = get_building_name_public(client_cd)
    return {"result": "ok", "mansion_name": name}


@router.get("/auth/building/name")
def building_name_auth(room_number: str, password: str, building_id: str):
    return get_building_name_auth(room_number, password, building_id)
