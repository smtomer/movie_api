import os
import sqlalchemy as sq
import dotenv

def database_connection_url():
    dotenv.load_dotenv()
    DB_USER: str = os.environ.get("POSTGRES_USER")
    DB_PASSWD = os.environ.get("POSTGRES_PASSWORD")
    DB_SERVER: str = os.environ.get("POSTGRES_SERVER")
    DB_PORT: str = os.environ.get("POSTGRES_PORT")
    DB_NAME: str = os.environ.get("POSTGRES_DB")
    return f"postgresql://{DB_USER}:{DB_PASSWD}@{DB_SERVER}:{DB_PORT}/{DB_NAME}"

engine = sq.create_engine(database_connection_url())

conn = engine.connect()

metadata_obj = sq.MetaData()
movies = sq.Table("Movies", metadata_obj, autoload_with=engine)
characters = sq.Table("Characters", metadata_obj, autoload_with=engine)
conversations = sq.Table("Conversations", metadata_obj, autoload_with=engine)
lines = sq.Table("Lines", metadata_obj, autoload_with=engine)