import sys
import os

try:
    from utils.get_project_root import get_project_root
    sys.path.append(get_project_root())
except ModuleNotFoundError:
    # Fallback if import fails
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(os.path.abspath(os.path.join(current_dir, "..")))

from utils.config_loader import ConfigLoader
import psycopg2


def main():
    config = ConfigLoader.load_config()
    db_url = config["database"]["url"]

    print(f"🔗 Connecting to: {db_url}")
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        cur.execute("SELECT NOW();")
        now = cur.fetchone()[0]
        print(f"✅ Connected successfully. Server time: {now}")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")

if __name__ == "__main__":
    main()
