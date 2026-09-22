from app.database import metadata, engine

metadata.create_all(engine)
