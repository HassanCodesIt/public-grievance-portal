from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from .config import settings
import socket
import urllib.parse
import urllib.request
import json

is_sqlite = settings.DATABASE_URL.startswith("sqlite")

engine_kwargs = {"pool_pre_ping": True}
if is_sqlite:
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs["pool_size"] = 10
    engine_kwargs["max_overflow"] = 20
    # Resilient DNS resolution fallback for local networks with restrictive DNS
    try:
        parsed = urllib.parse.urlparse(settings.DATABASE_URL)
        if parsed.hostname:
            try:
                socket.gethostbyname(parsed.hostname)
            except Exception:
                req = urllib.request.Request(
                    f"https://dns.google/resolve?name={parsed.hostname}&type=A",
                    headers={"User-Agent": "Mozilla/5.0"}
                )
                data = json.loads(urllib.request.urlopen(req, timeout=3).read())
                ips = [ans["data"] for ans in data.get("Answer", []) if ans.get("type") == 1]
                if ips:
                    engine_kwargs["connect_args"] = {"hostaddr": ips[0]}
    except Exception:
        pass

engine = create_engine(settings.DATABASE_URL, **engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

