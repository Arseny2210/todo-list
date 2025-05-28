from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, create_engine, Session, select

class Task(SQLModel, table=True): 
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(..., min_length=1, max_length=255)
    done: bool = False
    important: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

sqlite_url = "sqlite:///tasks.db"
engine = create_engine(sqlite_url, echo=False)

def init_db(): 
    SQLModel.metadata.create_all(engine)

def get_session(): 
    return Session(engine)