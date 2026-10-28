from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import DATABASE_URL

connect_args = {"check_same_thread": False, "timeout": 60} if "sqlite" in DATABASE_URL else {}

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
        cursor.execute("PRAGMA busy_timeout=60000")
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

            db_res = conn.execute(text("PRAGMA table_info(daybook_records)")).fetchall()
            db_cols = [r[1] for r in db_res]
            if "validation_status" not in db_cols:
                conn.execute(text("ALTER TABLE daybook_records ADD COLUMN validation_status VARCHAR(100)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_db_val_status ON daybook_records (validation_status)"))
                conn.commit()
    except Exception as e:
        print(f"DB auto-migration check note: {e}")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

