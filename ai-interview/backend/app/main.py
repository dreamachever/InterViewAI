from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy import inspect, text

from app.api.routes import auth, health, interviews, users
from app.core.config import get_settings
from app.core.database import Base, engine
from app import models  # noqa: F401


settings = get_settings()
app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    ensure_user_id_column()


app.include_router(health.router, prefix=settings.api_prefix)
app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(users.router, prefix=settings.api_prefix)
app.include_router(interviews.router, prefix=settings.api_prefix)


def ensure_user_id_column() -> None:
    inspector = inspect(engine)
    if "interviews" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("interviews")}
    if "user_id" in columns:
        return
    with engine.begin() as connection:
        connection.execute(text("ALTER TABLE interviews ADD COLUMN user_id VARCHAR"))
        connection.execute(text("CREATE INDEX IF NOT EXISTS ix_interviews_user_id ON interviews (user_id)"))
