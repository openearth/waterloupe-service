import configparser
from pathlib import Path

import sqlalchemy

service_path = Path(__file__).resolve().parent


def read_config(file_name="configuration.txt") -> tuple:
    """
    Reads the configuration file
      Returns:
          List with configuration
    """
    cf_file = service_path / file_name
    cf = configparser.RawConfigParser()
    cf.read(cf_file)

    # POSTGIS
    host = cf.get("PostGIS", "host")
    user = cf.get("PostGIS", "user")
    password = cf.get("PostGIS", "pass")
    db = cf.get("PostGIS", "db")
    port = cf.get("PostGIS", "port")

    return (host, user, password, db, port)


def establish_db_connection():
    host, user, password, db, port = read_config()
    engine = sqlalchemy.create_engine(
        f"postgresql://{user}:{password}@{host}:{port}/{db}"
    )
    connection = engine.connect()

    return engine, connection
