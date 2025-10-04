import math

R_earth = 6371000.0  # Earth's radius in m
G = 9.81  # Gravity of Earth in m/s^2
RHO_W = 1025.0  # Seawater density in kg/m^3
JpkT = 4184e12  # 1 megaton of TNT in joules


# Utils
def deg2rad(deg):
    return deg * math.pi / 180


def joules2ktons(joules):
    return joules / JpkT


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
    Eq 3: log10 Yi = 2.107 + 0.0624Ui^1/2
    """
    return 10 ** (2.107 + 0.0624 * Ui ** (1 / 2.0))


def altitude_of_breakup(L0, v0, Ui, T, C_D=1.0, H=8000):
    """
    Returns altitude at which the impactor will break up.

    Combination of two formulas
    Eq 4:
        a. z* = -H(ln(Yi/U0*v0^2) + 1.308 + 0.314If - 1.303 sqrt(1 - If))
        where If:
        b. If = 4.07 (C_D*H*Yi)/(Ui*L0*v0^2*sin(T))

        if If >= 1, 4a is not used. if If < 1, 4a is used
    """

    Yi = breakup_strength(Ui)
    If = 4.07 * (C_D * H * Yi) / (Ui * L0 * v0**2 * math.sin(deg2rad(T)))
    if If >= 1:
        return 0
    return -H * (math.log(Yi / v0**2) + 1.308 + 0.314 * If - 1.303 * math.sqrt(1 - If))


# --------------------- 3. CRATER -----------------------------------


def transient_crater_diameter(L0, Ui, Uj, v, T, target_is_water=False):
    """
    Returns the diameter of the crater created immediately after an impact.

    Eq 5a: D_tc = C * (Ui/Uj)^(1/3) * L^0.78 * v^0.44 * g^-0.22 * sin(T)^(1/3)
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


def transient_crater_depth(D_tc):
    """
    Returns the depth of the crater created immediately after an impact.
    Eq. 5b: d_tc = D_tc / 2sqrt2
    """

    return D_tc / (2 * math.sqrt(2))


def final_crater_diameter(D_tc):
    """
    Returns final diameter crater:
    Eq 6ab:
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
    Eq 7: d_fr = 0.294 * D_fr^0.301
    """

    return 0.294 * D_fr**0.301


def simple_crater_depth(D_fr):
    """
    Returns crater depth for simple craters:
    Eq 8: d_fr = 0.20 * D_fr
    """

    return 0.20 * D_fr


# ------------ 4. THERMAL RADIATION -------------------------------


def fireball_radius(E):
    """
    Returns fireball radius.
    Eq 9: R_f = 0.002 * E^(1/3) (approx)
    """

    return 0.002 * E ** (1 / 3)


def thermal_exposure(E, r, K=3e-3):
    """
    Returns thermal exposure for a person standing r km from the impact site.
    Eq 10: θ = K * E / (2 pi r^2)
    K is luminous efficiency
    Result in J/m^2
    """

    if r == 0:
        return float("inf")
    return K * E / (2 * math.pi * r**2)


# ------------------ 5. EARTHQUAKE ------------------------------


def seismic_magnitude(E):
    """
    Returns seismic magnitude for a given impact energy
    Eq 11: M = 0.67 * log10(E) - 5.87
    """

    if E == 0:
        return -999
    return 0.67 * math.log10(E) - 5.87


def effective_magnitude(M, r):
    """
    Returns effective magnitude at a distance
    depending on the distance:
    Eq 12
        a: M_eff = M - 0.0238r (r < 60km)
        b: M_eff = 0.0048r - 1.1644 (60km <= r < 700km)
        c: M_eff = M - 1.66log(r/R_earth) - 6.399 (700km <= r)
    """

    if r < 60:
        return M - 0.0238 * r
    if 60 <= r < 700:
        return 0.0048 * r - 1.1644
    return M - 1.66 * math.log(r / R_earth) - 6.399


# ---------------- 6. EJECTA ----------------------------------


def ejecta_thickness(D_tc, r):
    """
    Returns ejecta thickness
    Eq 13: t_e = D_tc^4 / (112 * r^3)
    """
    if r == 0:
        return float("inf")
    return D_tc**4 / (112 * r**3)


def mean_ejecta_size(D_fr, r, alpha=2.65):
    """
    Returns mean ejecta size
    Eq 14a: D_e = dc(D_fr / (2 * r))^alpha
    where dc is defined as:
    Eq 14b: dc = 2400(D_fr/2)^-1.62
    """

    return 2400 * D_fr**-1.62 * (D_fr / (2 * r)) ** alpha


# ------------------- 7. AIRBLAST  -------------------------


def scaled_dist(r, E):
    """
    Returns scaled distance for airblast
    Eq 15: r1 = r / E_kT^(1/3)
    E_kT is kinetic energy in kT of TNT
    """

    E_kT = joules2ktons(E)
    return r / E_kT ** (1 / 3)


def surface_blast(r1, px=7500, rx=290):
    """
    Returns the peak overpressure from a crater impact or a Mach reflection region airburst
    Eq 16: p(r1) = px*rx/4r1 (1 + 3(rx/r1)^1.3)
    """

    return px * rx / (4 * r1) * (1 + 3 * (rx / r1) ** 1.3)


def airblast(r1, zb):
    """
    Returns the peak overpressure from a regular reflection region airburst
    Eq 17a: p = p0 * e^(-beta*r1)
    where:
    Eq 17b: p0 = 3.14 * 10^11 * zb^-2.6
    Eq 17c: beta = 34.87*zb^-1.73
    """

    p0 = 3.14e11 * zb**-2.6
    beta = 34.87 * zb**-1.73
    return p0 * math.exp(-beta * r1)


def peak_vel(p, P0=1.01325, c0=343):
    """
    returns the peak wind velocity given a peak overpressure
    Eq 18: u = 5p/7P0 * c0/(1 + 6p/7P0)^0.5
    """
    return 5 * p / 7 * P0 * c0 / (1 + 6 * p / 7 * P0) ** 0.5


# ----------------- 8. TSUNAMI (TBC) ---------------------

# ------------------- MAIN -----------------------------
