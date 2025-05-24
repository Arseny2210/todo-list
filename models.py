from sqlmodel import SQLModel, Field, create_engine, Session,select

class Task(SQLModel, table = True): 
	id: int | None = Field(default = None, primary_key = True)
	name: str
	done: bool = False
	important: bool = False

sqlite_url = "sqlite:///tasks.db"

engine = create_engine(sqlite_url, echo = False)

def init_db(): 
	SQLModel.metadata.create_all(engine)

def get_session(): 
	return Session(engine)