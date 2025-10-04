import sqlite3
import requests
import datetime
from tqdm import tqdm


def update_db():
    print("Updating database...")

    with sqlite3.connect("asteroid.db") as conn:
        c = conn.cursor()

        c.execute("""
           CREATE TABLE IF NOT EXISTS asteroids (
               spkid INTEGER PRIMARY KEY,
               fullname TEXT,
               pha BOOLEAN,
               a REAL,
               e REAL,
               i REAL,
               om REAL,
               w REAL,
               ma REAL,
               last_updated TEXT
           )
       """)

        print("Fetching data...")

        url = "https://ssd-api.jpl.nasa.gov/sbdb_query.api?fields=full_name,spkid,neo,pha,e,a,ma,i,om,w&sb-kind=a&sb-group=neo"
        data = requests.get(url).json()["data"]

        print("Data fetched. Now loading...")

        for item in tqdm(data, desc="Loading data"):
            fullname, spkid, _, pha, e, a, ma, i, om, w = item
            spkid = int(spkid)
            fullname = fullname.strip()

            def safe_float(x):
                try:
                    return float(x)
                except (ValueError, TypeError):
                    return None

        for item in tqdm(data, desc="Loading data"):
            fullname, spkid, _, pha, e, a, ma, i, om, w = item

            spkid = int(spkid)

            fullname = fullname.strip().title()

            # Convert numbers safely
            a = safe_float(a)
            e = safe_float(e)
            i = safe_float(i)
            om = safe_float(om)
            w = safe_float(w)
            ma = safe_float(ma)

            if a is None or a <= 0:
                continue
            if e is None or not (0 <= e < 2):
                continue
            if i is None or not (0 <= i <= 180):
                continue

                pha = pha == "Y"

                c.execute(
                    """
                   INSERT OR IGNORE INTO asteroids (spkid, fullname, pha, a, e, i, om, w, ma, last_updated)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
               """,
                    (
                        spkid,
                        fullname,
                        pha,
                        a,
                        e,
                        i,
                        om,
                        w,
                        ma,
                        datetime.datetime.now().isoformat(),
                    ),
                )


if __name__ == "__main__":
    update_db()
