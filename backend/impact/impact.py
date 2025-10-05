import math

R_earth = 6371000.0  # Earth's radius in m
G = 9.81  # Gravity of Earth in m/s^2
RHO_W = 1025.0  # Seawater density in kg/m^3
JpkT = 4.184e12  # 1 megaton of TNT in joules


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


def energy_at_altitude(v, v0, E0):
    """
    Returns the intact flight approximation of energy at a given altitude.
    Eq A: E = E0 * (v/v0)^2
    """

    return E0 * (v / v0) ** 2


def breakup_strength(Ui):
    """
    Returns the breakup strength of an impactor with a given pressure

    under atmospheric pressure
    The empirical formula is given as:
    Eq 3: log10 Yi = 2.107 + 0.0624Ui^1/2
    """
    return 10 ** (2.107 + 0.0624 * Ui ** (1 / 2.0))


def altitude_of_breakup(L0, v0, Ui, T, C_D=1.0, H=8000, p0=1.2250):
    """
    Returns altitude at which the impactor will break up.

    Combination of two formulas
    Eq 4:
        a. z* = -H(ln(Yi/p0*v0^2) + 1.308 + 0.314If - 1.303 sqrt(1 - If))
        where If:
        b. If = 4.07 (C_D*H*Yi)/(Ui*L0*v0^2*sin(T))

        if If >= 1, 4a is not used. if If < 1, 4a is used
    """

    Yi = breakup_strength(Ui)
    If = 4.07 * (C_D * H * Yi) / (Ui * L0 * v0**2 * math.sin(deg2rad(T)))
    if If >= 1 or If <= 0:
        return 0
    return -H * (
        math.log(Yi / (p0 * v0**2)) + 1.308 + 0.314 * If - 1.303 * math.sqrt(1 - If)
    )


def complete_breakup_height(L0, z_star, Ui, T, H=8000, C_D=1.0, p0=1.2250, ratio=3):
    """
    Returns the complete breakup height of an impactor
    if the impactor does not break up, returns 0
    Eq 5a: z = z* - 2Hln(1 + l/2H * sqrt(ratio^2 - 1))
    where l is defined as:
    Eq 5b: l = L0*sinT*sqrt(Ui/(C_D*exp(-z*/H))
    """

    T_rad = deg2rad(T)
    l_disp = L0 * math.sin(T_rad) * math.sqrt(Ui / (C_D * math.exp(-z_star / H)))
    z = z_star - 2 * H * math.log(1 + (l_disp / (2 * H)) * math.sqrt(ratio**2 - 1))
    return 0 if z <= 0 else z


def length_at_alt(L0, z_star, Ui, T, z, H=8000, C_D=1.0, p0=1.2250):
    """
    Returns the pancaked length of the impactor IF complete_breakup_height returns -1
    Eq 6a: L(z) = L0 * sqrt(1 + (2H / l)^2 * (exp((z* - z)/2H) -1)^2
    where l is defined as:
    Eq 6b: l = L0*sinT*sqrt(Ui/(C_D*exp(-z*/H))
    """

    T_rad = deg2rad(T)
    l_disp = L0 * math.sin(T_rad) * math.sqrt(Ui / (C_D * math.exp(-z_star / H)))
    return L0 * math.sqrt(
        1 + (2 * H / l_disp) ** 2 * (math.exp((z_star - z) / (2 * H)) - 1) ** 2
    )


def swarm_velocity_at_alt(
    v0, L0, z_star, Ui, T, z, H=8000, C_D=1.0, p0=1.2250, ratio=3
):
    """
    Returns the swarm velocity of the impactor IF complete_breakup_height returns 0
    Eq 7*a: v(z) = v(z*)exp(-3/4 * ((C_D * exp(-z*/H)) / (Ui * L0^3 * sinT)) * int_z^z* (e^((z* - z)/H) * L(z)^2) dz)
    sub z = zb:
    Eq 7*b: v(zb) = v(z*)exp(-3/4 * ((C_D * exp(-z*/H)) / (Ui * L0^3 * sinT)) * (l*L0^2)/24 * alpha(8 * (3+alpha^2) + 3*alpha * l/H * (2 + a^2))
    where l is defined as:
    Eq 7*c: l = L0*sinT*sqrt(Ui/(C_D*exp(-z*/H))
    and alpha is defined as:
    Eq 7*d: alpha = sqrt(ratio^2 - 1)
    """

    vel_at_z_star = v_at_altitude(v0, L0, Ui, T, z_star)

    l_disp = L0 * math.sin(deg2rad(T)) * math.sqrt(Ui / (C_D * math.exp(-z_star / H)))

    alpha = math.sqrt(ratio**2 - 1)

    factor = (
        ((l_disp * L0**2) / 24)
        * alpha
        * (8 * (3 + alpha**2) + 3 * alpha * (l_disp / H) * (2 + alpha**2))
    )

    return vel_at_z_star * math.exp(
        -3
        / 4
        * ((C_D * math.exp(-z_star / H)) / (Ui * L0**3 * math.sin(deg2rad(T))))
        * factor
    )


def swarm_velocity_at_zero(v0, L0, z_star, Ui, T, H=8000, C_D=1.0, p0=1.2250):
    """
    Returns the swarm velocity of the impactor IF complete_breakup_height returns 0
    Eq 7a: v(z) = v(z*)exp(-3/4 * ((C_D * exp(-z*/H)) / (Ui * L0^3 * sinT)) * int_z^z* (e^((z* - z)/H) * L(z)^2) dz)
    sub z = 0
    Eq 7b : v(0) = v(z*)exp(-3/4 * ((C_D * exp(-z*/H)) / (Ui * L0^3 * sinT)) * (H^3 * L0^2)/3l^2 * (3(4 + (l/H)^2) exp(z*/H) + 6exp(2z*/H) - 16exp(3z*/2H) - 3(l/H)^2 - 2))
    where l is defined as:
    Eq: 7c: l = L0*sinT*sqrt(Ui/(C_D*exp(-z*/H))
    """

    vel_at_z_star = v_at_altitude(v0, L0, Ui, T, z_star)

    l_disp = L0 * math.sin(deg2rad(T)) * math.sqrt(Ui / (C_D * math.exp(-z_star / H)))

    factor = (
        (H**3 * L0**2)
        / (3 * l_disp**2)
        * (
            3 * (4 + (l_disp / H) ** 2) * math.exp(z_star / H)
            + 6 * math.exp(2 * z_star / H)
            - 16 * math.exp(3 * z_star / (2 * H))
            - 3 * (l_disp / H) ** 2
            - 2
        )
    )
    exp_arg = (
        -3 / 4 * (C_D * math.exp(-z_star / H)) / (Ui * L0**3 * math.sin(T)) * factor
    )
    vel_at_zero = vel_at_z_star * math.exp(exp_arg)

    return vel_at_zero


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

    return 294 * (D_fr / 1000) ** 0.301


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
    (r is in km, need to change to m)
    """

    if r == 0:
        return float("inf")
    return (K * E) / (2 * math.pi * (r * 1000) ** 2)


# ------------------ 5. EARTHQUAKE ------------------------------


def seismic_magnitude(E):
    """
    Eq 11: M = 0.67 * log10(E) - 5.87
    Returns seismic magnitude for a given impact energy
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
        b: M_eff = M - (0.0048r - 1.1644) (60km <= r < 700km)
        c: M_eff = M - 1.66log10(r/R_earth) - 6.399 (700km <= r)
    """

    if r < 60:
        return M - 0.0238 * r
    if 60 <= r < 700:
        return M - (0.0048 * r - 1.1644)
    return M - 1.66 * math.log10(r * 1000 / R_earth) - 6.399


# ---------------- 6. EJECTA ----------------------------------


def ejecta_thickness(D_tc, r):
    """
    Returns ejecta thickness
    Eq 13: t_e = D_tc^4 / (112 * r^3)
    (r is in km, need to convert to m)
    """
    if r == 0:
        return float("inf")
    return D_tc**4 / (112 * (r * 1000) ** 3)


def mean_ejecta_size(D_fr, r, alpha=2.65):
    """
    Returns mean ejecta size
    Eq 14a: D_e = dc(D_fr / (2 * r))^alpha
    where dc is defined as:
    Eq 14b: dc = 2400(D_fr/2)^-1.62

    """
    if r == 0:
        return float("inf")

    return 2400 * (D_fr / 1000) ** -1.62 * ((D_fr / 1000) / (2 * r)) ** alpha


# ------------------- 7. AIRBLAST  -------------------------


def scaled_dist(r, E):
    """
    Returns scaled distance for airblast to 1kt equivalent
    Eq 15: r1 = r / E_kT^(1/3)
    E_kT is kinetic energy in kT of TNT
    (r in km, so must convert to m)
    """

    E_kT = joules2ktons(E)
    return r * 1000 / E_kT ** (1 / 3)


def surface_blast(r1, px=75000, rx=290):
    """
    Returns the peak overpressure from a crater impact or a Mach reflection region airburst
    Eq 16: p(r1) = px*rx/4r1 (1 + 3(rx/r1)^1.3)
    """

    if r1 == 0:
        return float("inf")
    return ((px * rx) / (4 * r1)) * (1 + 3 * ((rx / r1) ** 1.3))


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


def peak_vel(p, P0=101325, c0=343):
    """
    returns the peak wind velocity given a peak overpressure
    Eq 18: u = 5p/7P0 * c0/(1 + 6p/7P0)^0.5
    """

    factor = (5.0 * p) / (7.0 * P0)
    denom_sqrt = math.sqrt(1.0 + (6.0 * p) / (7.0 * P0))
    return factor * c0 / denom_sqrt


# ----------------- 8. TSUNAMI (TBC) ---------------------


# ------------------- MAIN -----------------------------
def main(L0, Ui, v0, T, Uj):
    E0 = k_energy(L0, Ui, v0)
    zb = 0.0
    v_ground = None
    crater_diamater = None
    crater_depth = None
    fball_radius = 0.0
    M = None
    E = 0.0
    E_ground = None
    E_air = None

    z_star = altitude_of_breakup(L0, v0, Ui, T)
    if z_star != 0:
        zb = complete_breakup_height(L0, z_star, Ui, T)
        if zb != 0:
            v_zb = swarm_velocity_at_alt(v0, L0, z_star, Ui, T, zb)
            E = energy_at_altitude(v0 - v_zb, v0, E0)
            E_air = E
            E_ground = 0.0
        else:
            L = length_at_alt(L0, z_star, Ui, T, 0)
            v_ground = swarm_velocity_at_zero(v0, L0, z_star, Ui, T)
            E_ground = energy_at_altitude(v_ground, v0, E0)
            E_air = E0 - E_ground
            E = max(E_air, E_ground)

            D_tc = transient_crater_diameter(L, Ui, Uj, v_ground, T)
            crater_diamater = final_crater_diameter(D_tc)

            if D_tc < 2560:
                crater_depth = simple_crater_depth(crater_diamater)
            else:
                crater_depth = complex_crater_depth(crater_diamater)
            fball_radius = fireball_radius(E_ground)
            M = seismic_magnitude(E_ground)

    else:
        v_ground = v_at_altitude(v0, L0, Ui, T, 0)
        E = energy_at_altitude(v_ground, v0, E0)
        E_ground = E
        E_air = E0 - E

        D_tc = transient_crater_diameter(L0, Ui, Uj, v_ground, T)
        crater_diamater = final_crater_diameter(D_tc)

        if D_tc < 2560:
            crater_depth = simple_crater_depth(crater_diamater)
        else:
            crater_depth = complex_crater_depth(crater_diamater)
        fball_radius = fireball_radius(E)
        M = seismic_magnitude(E)

    r_effects = dict()

    ricter_to_mmi = {
        0: "-",
        1: "I",
        2: "I-II",
        3: "III-IV",
        4: "IV-V",
        5: "VI-VII",
        6: "VII-VIII",
        7: "IX-X",
        8: "X-XI",
        9: "XII",
    }

    for r in range(0, 20000, 1):
        thermal = thermal_exposure(E, r)
        mmi = None
        if M is not None:
            effective_M = effective_magnitude(M, r)
            mmi = ricter_to_mmi[min(9, math.floor(max(float(0), effective_M)))]

        if zb == 0:
            thickness = ejecta_thickness(D_tc, r)
            mean_size = mean_ejecta_size(crater_diamater, r)
        dist = scaled_dist(r, E)
        rm1 = (550 * scaled_dist(r, E)) / (1.2 * (550 - scaled_dist(r, E)))
        blast = 0.0
        if (E_ground > E_air and dist < rm1) or z_star == 0:
            blast = surface_blast(dist)
        else:
            blast = airblast(dist, zb)

        peak_wind_vel = peak_vel(blast)

        r_effects[r] = {
            "thermal_exposure": thermal,
            "effective_magnitude": effective_M,
            "effective_mmi": mmi,
            "ejecta_thickness": thickness,
            "mean_ejecta_size": mean_size,
            "surface_blast": blast,
            "peak_wind_vel": peak_wind_vel,
        }

    return (
        E0,
        E_ground,
        E_air,
        v_ground,
        crater_diamater,
        crater_depth,
        fball_radius,
        z_star,
        zb,
        r_effects,
    )


if __name__ == "__main__":
    (
        E0,
        E_ground,
        E_air,
        v_ground,
        crater_diamater,
        crater_depth,
        fball_radius,
        z_star,
        zb,
        r_effects,
    ) = main(300, 1600, 18000, 45, 2500)
    print(f"Initial energy: {E0:.4f}J")
    print(f"Energy in ground: {E_ground:.4f}J")
    print(f"Energy in air: {E_air:.4f}J")
    print(f"Final ground velocity: {v_ground:.4f}m/s")
    print(f"Crater diameter: {crater_diamater:.4f}m")
    print(f"Crater depth: {crater_depth:.4f}m")
    print(f"Fireball radius: {fball_radius:.4f}m")
    print(f"Z*: {z_star:.4f}m")
    print(f"Zb: {zb:.4f}m")

    print("At 100km:")
    print(f"Thermal exposure: {r_effects[100]['thermal_exposure']:.4f}J/m^2")
    print(f"Effective magnitude: {r_effects[100]['effective_magnitude']:.4f}")
    print(f"Effective MMI: {r_effects[100]['effective_mmi']}")
    print(f"Ejecta thickness: {r_effects[100]['ejecta_thickness']:.4f}m")
    print(f"Mean ejecta size: {r_effects[100]['mean_ejecta_size']:.4f}m")
    print(f"Surface blast: {r_effects[100]['surface_blast']:.4f}Pa")
    print(f"Peak wind velocity: {r_effects[100]['peak_wind_vel']:.4f}m/s")
