from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.deps.admin_auth import require_current_admin, require_admin_session_token
from app.core.db import get_db_session
from app.schemas.admin_auth import AdminLoginRequest, AdminProfileResponse, AdminSessionResponse
from app.services.admin_auth import create_admin_session, revoke_admin_session, verify_admin_credentials


router = APIRouter()


@router.post("/login", response_model=AdminSessionResponse)
def login(payload: AdminLoginRequest, db: Session = Depends(get_db_session)) -> AdminSessionResponse:
    admin = verify_admin_credentials(db, username=payload.username, password=payload.password)
    if admin is None:
        raise HTTPException(status_code=401, detail="invalid admin credentials")
    token = create_admin_session(db, admin_user=admin)
    db.commit()
    return AdminSessionResponse(username=admin.username, display_name=admin.display_name, session_token=token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(session_token: str = Depends(require_admin_session_token), db: Session = Depends(get_db_session)) -> Response:
    revoke_admin_session(db, session_token=session_token)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me", response_model=AdminProfileResponse)
def me(admin=Depends(require_current_admin)) -> AdminProfileResponse:
    return AdminProfileResponse(username=admin.username, display_name=admin.display_name)
