from fastapi import FastAPI
from pydantic import BaseModel
from asteroid.asteroid_orbit import (
    propagate,
    propagate_impulse,
    get_orbit_earth_asteroid,
)
from impact.impact import main as impact_main
import numpy as np
from astropy import units as u
from astropy.time import Time
from poliastro.twobody import Orbit

app = FastAPI(title="Deja", description="Deja API", version="1.0.0")


class ImpactRequest(BaseModel):
    L0: float  # initial size of asteroid in m
    Ui: float  # density of asteroid in kg/m^3
    v0: float  # speed of asteroid in m/s
    T: float  # angle of impact in degrees
    Uj: float  # density of target in kg/m^3


class ImpactResponse(BaseModel):
    E0: float  # initial energy of asteroid in J
    E_ground: float  # energy of asteroid transferred to ground in J
    E_air: float  # energy of asteroid dissipated in the air in J
    v_ground: float  # final speed of asteroid on ground in m/s
    crater_diamater: float  # diameter of crater created in m
    crater_depth: float  # depth of crater created in m
    z_breakup: float  # height at which asteroid begins breaks up in m
    zb: float  # height at which the asteroid completely breaks apart in m
    r_effects: dict  # dictionary of effects at different distances from ground zero

    """
    r_effects includes:

    thermal_exposure: float, Thermal exposure in J/m^2
    effective_magnitude: float, Effective magnitude
    effective_mmi: string, MMI
    ejecta_thickness: float, Ejecta thickness in m
    mean_ejecta_size: float, Mean ejecta size in m
    surface_blast: float, Peak blast overpressure in Pa 
    peak_vel: float, Peak wind velocity in m/s
    """


class OrbitRequest(BaseModel):
    id: int  # SPKID of an small body of interest


class OrbitResponse(BaseModel):
    earth_pos: list  # List of positions of the Earth,
    # each element is in the form of [x, y, z] in km
    asteroid_pos: list  # List of positions of the asteroid,
    # each element is in the form of [x, y, z] in km


class ImpulseRequest(BaseModel):
    id: int  # SPKID of an small body of interest
    v_delta: list  # a velocity vector in a form of [x, y, z] km/s
    t: float  # time of the impulse maneuver in days


class ImpulseResponse(BaseModel):
    earth_pos: list  # List of positions of the Earth,
    # each element is in the form of [x, y, z] in km
    asteroid_pos: list  # List of positions of the asteroid,
    # each element is in the form of [x, y, z] in km


@app.post("/orbit", response_model=OrbitResponse)
async def orbit(data: OrbitRequest):
    orbit, earth_orbit = get_orbit_earth_asteroid(data.id)
    earth_pos, asteroid_pos = propagate(earth_orbit, orbit, 730)
    earth_pos = earth_pos.tolist()
    asteroid_pos = asteroid_pos.tolist()

    return OrbitResponse(earth_pos=earth_pos, asteroid_pos=asteroid_pos)


@app.post("/impulse", response_model=ImpulseResponse)
async def impulse(data: ImpulseRequest):
    orbit, earth_orbit = get_orbit_earth_asteroid(data.id)
    v_delta = np.array(data.v_delta) * u.km / u.s
    t = data.t * u.day
    earth_pos, asteroid_pos = propagate_impulse(earth_orbit, orbit, v_delta, t, 730)
    earth_pos = earth_pos.tolist()
    asteroid_pos = asteroid_pos.tolist()

    return ImpulseResponse(earth_pos=earth_pos, asteroid_pos=asteroid_pos)


@app.post("/impact", response_model=ImpactResponse)
async def impact(data: ImpactRequest):
    (
        E0,
        E_ground,
        E_air,
        v_ground,
        crater_diamater,
        crater_depth,
        z_breakup,
        zb,
        r_effects,
    ) = impact_main(data.L0, data.Ui, data.v0, data.T, data.Uj)
    return ImpactResponse(
        E0=E0,
        E_ground=E_ground,
        E_air=E_air,
        v_ground=v_ground,
        crater_diamater=crater_diamater,
        crater_depth=crater_depth,
        z_breakup=z_breakup,
        zb=zb,
        r_effects=r_effects,
    )
