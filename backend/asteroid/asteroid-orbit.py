from astropy import units as u
from astropy.time import Time
from astropy.coordinates import solar_system_ephemeris, get_body_barycentric_posvel
from astropy.coordinates import CartesianRepresentation
from poliastro.bodies import Sun
from poliastro.twobody import Orbit
import sqlite3

conn = sqlite3.connect("asteroid.db")
c = conn.cursor()

# Random asteroid
c.execute(
    "SELECT spkid, fullname, a, e, i, om, w, ma FROM asteroids WHERE pha = 1 ORDER BY RANDOM() LIMIT 1"
)
row = c.fetchone()
conn.close()

spkid, name, a, e, i, om, w, ma = row
print(f"Asteroid {name} ({spkid})")

orbit = Orbit.from_classical(
    Sun, a * u.AU, e, i * u.deg, om * u.deg, w * u.deg, ma * u.deg
)
print(orbit)
