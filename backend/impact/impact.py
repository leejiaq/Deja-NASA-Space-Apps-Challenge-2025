import math

R_earth = 6371000.0  # Earth's radius in m
G = 9.81  # Gravity of Earth in m/s^2
RHO_W = 1025.0  # Seawater density in kg/m^3
JpMT = 4184e15  # 1 megaton of TNT in joules


# Utils
def deg2rad(deg):
    return deg * math.pi / 180


def joules2megatons(joules):
    return joules / JpMT


"""
    NOTES ABOUT VARIABLE USAGE
    
    L0: Asteroid diameter
    Ui: Asteroid density
    v0: Asteroid velocity before entering Earth's atmosphere
    v: Asteroid velocity during and after entering Earth's atmosphere
    T: Impact angle
    r: Distance from impact point (1-20000 km)
    Uj: Target surface
"""

# -------------------- 1. KINETIC ENERGY ------------------------------


def k_energy(L0, Ui, v0):
    """
    Returns the kinetic energy of an impactor with a given diameter, density, and speed.

    Eq 1: E = (1/12) * pi * Ui * L0^3 * V0^2
    """
    return (math.pi / 12.0) * Ui * (L0**3) * (v0**2)


# -----------2. ATMOSPHERIC ENTRY (SIMPLIFIED)-------------------------


def v_at_altitude(v0, L0, Ui, T, z, C_D=1.0, p0=1.2250, H=8000):
    """
    Returns the velocity of an impactor at a given altitude.

    Eq 2: v = v0 * exp(-(3 * C_D * H * p0)/(4*Ui*L0 sin T) * e^(-z/H))
    where e^(-z/H) is the exponential decay of the atmospheric density
    with height. This is a simple model of the atmosphere.
    """

    T_rad = deg2rad(T)
    if math.sin(T_rad) == 0:
        return v0
    return v0 * math.exp(
        -(3 * C_D * H * p0) / (4 * Ui * L0 * math.sin(T_rad)) * math.exp(-z / H)
    )


def breakup_strength(Ui):
    """
    Returns the breakup strength of an impactor with a given pressure
    under atmospheric pressure

    The empirical formula is given as:
    Eq 3: log10 Yi = 2.107 + 0.0624Ui
    """
    return 10 ** (2.107 + 0.0624 * Ui)


# ----------------- 3. CRATER AND MELT -------------------------------


def transient_crater_diameter(L0, Ui, Uj, v, T, target_is_water=False):
    """
    Returns the diameter of the crater created immediately after an impact.

    Eq 4: D_tc = C * (Ui/Uj)^(1/3) * L^0.78 * v^0.44 * g^-0.22 * sin(T)^(1/3)
    where C = 1.161 for rock and 1.365 for water
    """
    C = 1.365 if target_is_water else 1.161
    T_rad = deg2rad(T)
    return (
        C
        * (Ui / Uj) ** (1 / 3.0)
        * L0**0.78
        * v**0.44
        * G**-0.22
        * math.sin(T_rad) ** (1 / 3.0)
    )


def final_crater_diameter(D_tc):
    """
    Returns final diameter crater:
    Eq 5ab:
        if simple (D_tc < 2560m): D_fc = 1.2 * D_tc
        if complex (D_tc >= 2560m): D_fc = 1.17 * D_tc^1.13 * D_c^-0.13, where D_c = 3200m
    """

    if D_tc < 2560:
        return 1.2 * D_tc
    else:
        return 1.17 * D_tc**1.13 * 3200**-0.13


def complex_crater_depth(D_fr):
    """
    Returns crater depth for complex craters:
    Eq 6: d_fr = 0.294 * D_fr^0.301
    """

    return 0.294 * D_fr**0.301


def melt_vol(E, T):
    """
    Returns melt volume.
    Eq 7: V_m = 8.9e-12 * E * sin(T)
    """

    return 8.9e-12 * E * math.sin(deg2rad(T))
