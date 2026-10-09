from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import DATABASE_URL

connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True
)

if "sqlite" in DATABASE_URL:
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db():
    from sqlalchemy import text
    from app import models # ensure all models are registered
    Base.metadata.create_all(bind=engine)
    try:
        with engine.connect() as conn:
            result = conn.execute(text("PRAGMA table_info(import_batches)")).fetchall()
            col_names = [r[1] for r in result]
            if "voucher_date_range" not in col_names:
                conn.execute(text("ALTER TABLE import_batches ADD COLUMN voucher_date_range VARCHAR(100)"))
                conn.commit()
    except Exception as e:
        print(f"DB auto-migration check note: {e}")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

