from astropy import units as u
from astropy.time import Time
from astropy.coordinates import solar_system_ephemeris, get_body_barycentric_posvel
from astropy.coordinates import CartesianRepresentation
from poliastro.bodies import Sun, Earth
from poliastro.twobody import Orbit
import sqlite3
import numpy as np
import plotly.graph_objects as go


def get_orbit_earth_asteroid():
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

    earth_orbit = Orbit.from_body_ephem(Earth, Time.now())

    orbit = Orbit.from_classical(
        Sun, a * u.AU, e, i * u.deg, om * u.deg, w * u.deg, ma * u.deg
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

        earth_pos.append(earth_future.position)
        asteroid_pos.append(asteroid_future.position)

    earch_pos = np.array(earth_pos)
    asteroid_pos = np.array(asteroid_pos)

    return earch_pos, asteroid_pos


def plot(earth_pos, asteroid_pos, earth_orbit, asteroid_orbit, steps=1000):
    frames = []
    for k in range(steps):
        frames.append(
            go.Frame(
                data=[
                    go.Scatter3d(
                        x=[0],
                        y=[0],
                        z=[0],
                        mode="markers",
                        marker=dict(size=5, color="yellow"),
                    ),
                    go.Scatter3d(
                        x=earth_pos[: k + 1, 0],
                        y=earth_pos[: k + 1, 1],
                        z=earth_pos[: k + 1, 2],
                        mode="lines+markers",
                        lines=dict(color="blue", width=2),
                        name="Earth",
                    ),
                    go.Scatter3d(
                        x=asteroid_pos[: k + 1, 0],
                        y=asteroid_pos[: k + 1, 1],
                        z=asteroid_pos[: k + 1, 2],
                        mode="lines+markers",
                        lines=dict(color="red", width=2),
                        name="Asteroid",
                    ),
                ]
            )
        )

    fig = go.Figure(
        data=[
            go.Scatter3d(
                x=[0], y=[0], z=[0], mode="markers", marker=dict(size=5, color="yellow")
            ),
            go.Scatter3d(
                x=earth_pos[0, 0],
                y=earth_pos[0, 1],
                z=earth_pos[0, 2],
                mode="lines+markers",
                lines=dict(color="blue", width=2),
                name="Earth",
            ),
            go.Scatter3d(
                x=asteroid_pos[0, 0],
                y=asteroid_pos[0, 1],
                z=asteroid_pos[0, 2],
                mode="lines+markers",
                lines=dict(color="red", width=2),
                name="Asteroid",
            ),
        ],
        layout=go.Layout(
            scene=dict(
                xaxis_title="X [AU]", yaxis_title="Y [AU]", zaxis_title="Z [AU]"
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
                                    "frame": {"duration": 50, "redraw": True},
                                    "fromcurrent": True,
                                    "transition": {"duration": 0},
                                },
                            ],
                        )
                    ],
                )
            ],
        ),
        frames=frames,
    )
    fig.show()


def main():
    steps = 1000
    asteroid_orbit, earth_orbit = get_orbit_earth_asteroid()
    earth_pos, asteroid_pos = propagate(earth_orbit, asteroid_orbit, steps)
    plot(earth_pos, asteroid_pos, earth_orbit, asteroid_orbit, steps)


if __name__ == "__main__":
    main()
