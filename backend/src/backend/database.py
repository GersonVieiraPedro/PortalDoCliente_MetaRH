from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from .settings import Settings

engine = create_engine(Settings().DATABASE_URL)

def AtivarSession():
    """Cria uma nova sessão do banco de dados."""
    with Session(engine) as session:
        yield session

