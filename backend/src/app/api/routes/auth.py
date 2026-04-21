from fastapi import APIRouter


router = APIRouter()


@router.get("/whoami")
def whoami() -> dict[str, str]:
    return {
        "user_id": "demo-user",
        "status": "placeholder",
    }
