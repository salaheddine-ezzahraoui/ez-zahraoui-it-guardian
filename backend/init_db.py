from app.database import engine, Base
from app.models import Asset, Incident, MonitoringResult, Event

def init_db():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("All tables created successfully!")

if __name__ == "__main__":
    init_db()
