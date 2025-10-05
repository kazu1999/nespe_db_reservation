from fastapi import APIRouter
from typing import Optional

from reservation_fetcher import (
    get_reservation_date as get_reservation_date_public,
    get_reservation_history as get_reservation_history_public,
    get_reservation_status as get_reservation_status_public,
    get_upcoming_reservations as get_upcoming_reservations_public,
    get_reservation_summary as get_reservation_summary_public,
)
from reservation_fetcher_password import (
    get_reservation_date as get_reservation_date_auth,
    get_reservation_history as get_reservation_history_auth,
    get_reservation_status as get_reservation_status_auth,
    get_upcoming_reservations as get_upcoming_reservations_auth,
    get_reservation_summary as get_reservation_summary_auth,
)

router = APIRouter(prefix="/api/v1", tags=["reservation"])


@router.get("/public/reservation/date")
def reservation_date_public(room_number: str, building_id: str):
    return get_reservation_date_public(room_number, building_id)


@router.get("/public/reservation/history")
def reservation_history_public(room_number: str, building_id: str, limit: int = 50):
    return get_reservation_history_public(room_number, building_id, limit)


@router.get("/public/reservation/status")
def reservation_status_public(room_number: str, building_id: str):
    return get_reservation_status_public(room_number, building_id)


@router.get("/public/reservation/upcoming")
def reservation_upcoming_public(room_number: str, building_id: str, days_ahead: int = 30):
    return get_upcoming_reservations_public(room_number, building_id, days_ahead)


@router.get("/public/reservation/summary")
def reservation_summary_public(room_number: str, building_id: str):
    return get_reservation_summary_public(room_number, building_id)


@router.get("/auth/reservation/date")
def reservation_date_auth(room_number: str, password: str, building_id: str):
    return get_reservation_date_auth(room_number, password, building_id)


@router.get("/auth/reservation/history")
def reservation_history_auth(room_number: str, password: str, building_id: str, limit: int = 50):
    return get_reservation_history_auth(room_number, password, building_id, limit)


@router.get("/auth/reservation/status")
def reservation_status_auth(room_number: str, password: str, building_id: str):
    return get_reservation_status_auth(room_number, password, building_id)


@router.get("/auth/reservation/upcoming")
def reservation_upcoming_auth(room_number: str, password: str, building_id: str, days_ahead: int = 30):
    return get_upcoming_reservations_auth(room_number, password, building_id, days_ahead)


@router.get("/auth/reservation/summary")
def reservation_summary_auth(room_number: str, password: str, building_id: str):
    return get_reservation_summary_auth(room_number, password, building_id)
