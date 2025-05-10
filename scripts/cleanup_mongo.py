# scripts/cleanup_mongo.py

import os
import sys

# Make your project root importable
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

# Point at Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "banana_supply_chain.settings")

import django
django.setup()

from django.conf import settings
from pymongo import MongoClient

def get_mongo_config():
    db_conf = settings.DATABASES.get("default", {})
    engine = db_conf.get("ENGINE", "")
    # Only honor the Djongo engine
    if "djongo" not in engine.lower():
        print("⚠️  Default DB engine is not Djongo (found: %r); using fallback Mongo settings" % engine)
        return {
            "host": "localhost",
            "port": 27017,
            "name": "banana_supply_chain_db"
        }

    client_conf = db_conf.get("CLIENT") or {}
    host = client_conf.get("host", "localhost")
    port = client_conf.get("port", 27017)
    raw_name = db_conf.get("NAME", "")
    # If the NAME looks like a filesystem path, just grab the final folder/name
    if os.path.sep in raw_name or ":" in raw_name:
        raw_name = os.path.basename(raw_name)
        raw_name = os.path.splitext(raw_name)[0]
    name = raw_name or "banana_supply_chain_db"

    return {"host": host, "port": port, "name": name}


def main():
    cfg = get_mongo_config()
    print(f"Connecting to MongoDB at {cfg['host']}:{cfg['port']}, database '{cfg['name']}'")
    client = MongoClient(host=cfg["host"], port=cfg["port"])
    db = client[cfg["name"]]

    # Drop your three shipments collections
    for coll in ("shipments_deliveryperson", "shipments_shipment", "shipments_bananaimage"):
        print(f"→ Dropping collection `{coll}`…")
        db.drop_collection(coll)

    # Clean out the django_migrations entries for shipments
    deleted = db.django_migrations.delete_many({"app": "shipments"}).deleted_count
    print(f"→ Removed {deleted} django_migrations entries for app=shipments")

    print("✅  Mongo cleanup complete.")


if __name__ == "__main__":
    main()
