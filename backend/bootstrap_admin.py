from app.core.db import SessionLocal
from app.core.settings import settings
from app.services.admin_auth import ensure_admin_user


def main() -> None:
    with SessionLocal() as session:
        admin = ensure_admin_user(
            session,
            username=settings.admin_username,
            password=settings.admin_password,
            display_name=settings.admin_display_name,
        )
        session.commit()
        print(f"admin ready: {admin.username}")


if __name__ == "__main__":
    main()
