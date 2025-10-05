from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.first_choice import router as first_choice_router
from app.routers.second_choice import router as second_choice_router
from app.routers.reservation import router as reservation_router


app = FastAPI(title="nespe-db-reservation API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(first_choice_router)
app.include_router(second_choice_router)
app.include_router(reservation_router)


@app.get("/api/v1/health")
def health_check():
    return {"status": "ok"}
