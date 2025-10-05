from astropy import units as u
from astropy.time import Time
from poliastro.bodies import Sun, Earth
from poliastro.twobody import Orbit
from asteroid.asteroid_load import update_db
import random
import sqlite3
from dotenv import load_dotenv
import datetime
import requests
import os
import numpy as np
import plotly.graph_objects as go


def get_nearest_earth_orbit():
    load_dotenv()

    # API KEY IS PLACED UNDER .env IN CURRENT FOLDER

    API_KEY = os.getenv("NASA_API_KEY")

    time_begin = (datetime.datetime.now() + datetime.timedelta(days=0)).strftime(
        "%Y-%m-%d"
    )
    time_end = (datetime.datetime.now() + datetime.timedelta(days=7)).strftime(
        "%Y-%m-%d"
    )

    response = requests.get(
        f"https://api.nasa.gov/neo/rest/v1/feed?start_date={time_begin}&api_key={API_KEY}"
    )
    data = response.json()

    ids = []
    for data_item in data["near_earth_objects"].values():
        for item in data_item:
            ids.append(item["id"])
    return ids


def get_orbit_earth_asteroid(id):
    DB_PATH = os.path.join(os.path.dirname(__file__), "asteroid.db")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Random asteroid
    c.execute(
        "SELECT spkid, fullname, a, e, i, om, w, ma FROM asteroids WHERE spkid = ?",
        (id,),
    )
    row = c.fetchone()

    if row is None:
        update_db()
        c.execute(
            "SELECT spkid, fullname, a, e, i, om, w, ma FROM asteroids WHERE spkid = ?",
            (id,),
        )
        row = c.fetchone()
        if row is None:
            print("Asteroid not found")
            return

    conn.close()

    spkid, name, a, e, i, om, w, ma = row

    print(f"Asteroid {name} ({spkid})")

    earth_orbit = Orbit.from_body_ephem(Earth, Time.now())

    orbit = Orbit.from_classical(
        Sun, a * u.AU, e * u.one, i * u.deg, om * u.deg, w * u.deg, ma * u.deg
    )
    print(orbit)

    return orbit, earth_orbit


def propagate(earth_orbit, asteroid_orbit, steps=1000):
    times = np.linspace(0, 365, steps) * u.day

    earth_pos = []
    asteroid_pos = []

    for t in times:
        dt = t - 0 * u.day
        earth_future = earth_orbit.propagate(dt)
        asteroid_future = asteroid_orbit.propagate(dt)

        earth_pos.append(earth_future.r)
        asteroid_pos.append(asteroid_future.r)

    earth_pos = np.array(earth_pos)
    asteroid_pos = np.array(asteroid_pos)

    return earth_pos, asteroid_pos


def propagate_impulse(
    earth_orbit, asteroid_orbit, delta_v_vector, t_maneuver, steps=1000
):
    times = np.linspace(0, 365, steps) * u.day

    earth_pos = []
    asteroid_pos = []

    new_orbit = apply_delta_v(asteroid_orbit, delta_v_vector, t_maneuver)
    for t in times:
        dt = t - 0 * u.day

        dt_days = dt.to(u.day)

        if dt_days <= t_maneuver:
            asteroid_future = asteroid_orbit.propagate(dt_days)
        else:
            asteroid_future = new_orbit.propagate(dt_days - t_maneuver)

        earth_future = earth_orbit.propagate(dt)

        earth_pos.append(earth_future.r)
        asteroid_pos.append(asteroid_future.r)

    earth_pos = np.array(earth_pos)
    asteroid_pos = np.array(asteroid_pos)

    return earth_pos, asteroid_pos


def apply_delta_v(asteroid_orbit, delta_v_vector, t_maneuver):
    dt = t_maneuver
    orbit_at_t = asteroid_orbit.propagate(dt)

    r, v = orbit_at_t.rv()
    v = v.to(u.km / u.s)
    v += delta_v_vector

    new_orbit = Orbit.from_vectors(Sun, r, v)

    return new_orbit


def plot(earth_pos, asteroid_pos, earth_pos_orbit, asteroid_pos_orbit, steps=1000):
    initial_data = [
        # Sun marker
        go.Scatter3d(
            x=[0],
            y=[0],
            z=[0],
            mode="markers",
            marker=dict(size=5, color="yellow"),
            name="Sun",
        ),
        go.Scatter3d(
            x=earth_pos[:, 0],
            y=earth_pos[:, 1],
            z=earth_pos[:, 2],
            mode="lines",
            line=dict(color="blue", width=2),
            name="Earth Orbit",
        ),
        go.Scatter3d(
            x=asteroid_pos_orbit[:, 0],
            y=asteroid_pos_orbit[:, 1],
            z=asteroid_pos_orbit[:, 2],
            mode="lines",
            line=dict(color="red", width=2, dash="dash"),
            name="Asteroid Orbit Old",
        ),
        go.Scatter3d(
            x=asteroid_pos[:, 0],
            y=asteroid_pos[:, 1],
            z=asteroid_pos[:, 2],
            mode="lines",
            line=dict(color="red", width=2),
            name="Asteroid Orbit New",
        ),
        go.Scatter3d(
            x=[earth_pos[0, 0]],
            y=[earth_pos[0, 1]],
            z=[earth_pos[0, 2]],
            mode="markers",
            marker=dict(size=3, color="blue"),
            name="Earth",
        ),
        go.Scatter3d(
            x=[asteroid_pos[0, 0]],
            y=[asteroid_pos[0, 1]],
            z=[asteroid_pos[0, 2]],
            mode="markers",
            marker=dict(size=2, color="red"),
            name="Asteroid",
        ),
    ]

    frames = []
    for k in range(steps):
        frames.append(
            go.Frame(
                data=[
                    go.Scatter3d(
                        x=earth_pos[: k + 1, 0],
                        y=earth_pos[: k + 1, 1],
                        z=earth_pos[: k + 1, 2],
                    ),
                    go.Scatter3d(
                        x=asteroid_pos[: k + 1, 0],
                        y=asteroid_pos[: k + 1, 1],
                        z=asteroid_pos[: k + 1, 2],
                    ),
                ],
                traces=[4, 5],
            ),
        )

    fig = go.Figure(
        data=initial_data,
        layout=go.Layout(
            scene=dict(
                xaxis=dict(visible=False, showbackground=False),
                yaxis=dict(visible=False, showbackground=False),
                zaxis=dict(visible=False, showbackground=False),
                aspectmode="data",
                camera=dict(eye=dict(x=0, y=0, z=2.5)),
            ),
            title="Asteroid orbit",
            updatemenus=[
                dict(
                    type="buttons",
                    buttons=[
                        dict(
                            label="Play",
                            method="animate",
                            args=[
                                None,
                                {
                                    "frame": {"duration": 30, "redraw": True},
                                    "fromcurrent": True,
                                    "transition": {"duration": 0},
                                },
                            ],
                        ),
                        dict(
                            label="Pause",
                            method="animate",
                            args=[
                                [None],
                                {"frame": {"duration": 0}, "mode": "immediate"},
                            ],
                        ),
                    ],
                )
            ],
        ),
        frames=frames,
    )
    fig.show()


def main():
    steps = 730
    ids = get_nearest_earth_orbit()
    id = random.choice(ids)
    impulse = np.array([0.1, 0.0, 0.0]) * u.km / u.s
    impulse_time = 30 * u.day
    asteroid_orbit, earth_orbit = get_orbit_earth_asteroid(id)
    earth_pos_orbit, asteroid_pos_orbit = propagate(earth_orbit, asteroid_orbit, steps)
    earth_pos, asteroid_pos = propagate_impulse(
        earth_orbit, asteroid_orbit, impulse, impulse_time, steps
    )

    print(asteroid_pos_orbit[-5:])
    print("\n")
    print(asteroid_pos[-5:])
    plot(earth_pos, asteroid_pos, earth_pos_orbit, asteroid_pos_orbit, steps)


if __name__ == "__main__":
    main()
