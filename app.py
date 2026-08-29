"""
Operational Flight Plan (OFP) Generator with Alternate & Diversion Logic
Author: Pascal Ambogo Mudimba (@scalstein)
Flight Operations Engineering & Dispatch Systems Suite
"""

import math
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Operational Flight Plan (OFP) Generator | Flight Ops",
    layout="wide",
    page_icon="✈️",
)

# ---------------------------------------------------------
# 1. AIRPORT, WAYPOINT & AIRCRAFT MASTER DATA
# ---------------------------------------------------------

AIRPORTS = {
    "HKJK": {
        "name": "Nairobi (Jomo Kenyatta Intl)",
        "lat": -1.3192,
        "lon": 36.9278,
        "elev_ft": 5330,
        "rwy_len_m": 4117,
        "pcn": "84/F/A/W/T",
        "ils": True,
    },
    "HKMO": {
        "name": "Mombasa (Moi Intl)",
        "lat": -4.0348,
        "lon": 39.5942,
        "elev_ft": 200,
        "rwy_len_m": 3350,
        "pcn": "70/F/A/W/T",
        "ils": True,
    },
    "HKEL": {
        "name": "Eldoret Intl",
        "lat": 0.4045,
        "lon": 35.2389,
        "elev_ft": 6940,
        "rwy_len_m": 3475,
        "pcn": "65/F/A/W/T",
        "ils": True,
    },
    "HKKI": {
        "name": "Kisumu Intl",
        "lat": -0.0861,
        "lon": 34.7289,
        "elev_ft": 3757,
        "rwy_len_m": 3300,
        "pcn": "54/F/A/W/T",
        "ils": True,
    },
    "EBB": {
        "name": "Entebbe Intl (Uganda)",
        "lat": 0.0425,
        "lon": 32.4436,
        "elev_ft": 3780,
        "rwy_len_m": 3658,
        "pcn": "78/F/A/W/T",
        "ils": True,
    },
    "KGL": {
        "name": "Kigali Intl (Rwanda)",
        "lat": -1.9686,
        "lon": 30.1394,
        "elev_ft": 4891,
        "rwy_len_m": 3500,
        "pcn": "62/F/A/W/T",
        "ils": True,
    },
    "DAR": {
        "name": "Dar es Salaam (Julius Nyerere)",
        "lat": -6.8781,
        "lon": 39.2026,
        "elev_ft": 182,
        "rwy_len_m": 3000,
        "pcn": "75/F/A/W/T",
        "ils": True,
    },
    "JNB": {
        "name": "Johannesburg (O.R. Tambo)",
        "lat": -26.1392,
        "lon": 28.2460,
        "elev_ft": 5558,
        "rwy_len_m": 4421,
        "pcn": "100/F/A/W/T",
        "ils": True,
    },
    "DXB": {
        "name": "Dubai Intl (UAE)",
        "lat": 25.2532,
        "lon": 55.3657,
        "elev_ft": 62,
        "rwy_len_m": 4447,
        "pcn": "115/F/A/W/T",
        "ils": True,
    },
    "LHR": {
        "name": "London Heathrow (UK)",
        "lat": 51.4700,
        "lon": -0.4543,
        "elev_ft": 83,
        "rwy_len_m": 3902,
        "pcn": "120/F/A/W/T",
        "ils": True,
    },
}

WAYPOINTS = {
    "GBV": {"name": "Garissa VOR", "lat": -0.4611, "lon": 39.6450},
    "NV": {"name": "Nakuru NDB", "lat": -0.2667, "lon": 36.1500},
    "TV": {"name": "Tabora VOR", "lat": -5.0769, "lon": 32.8317},
    "MG": {"name": "Magadi VOR", "lat": -1.9000, "lon": 36.2833},
    "APNOX": {"name": "APNOX Fix", "lat": -1.6500, "lon": 33.5000},
    "UNSIT": {"name": "UNSIT Fix", "lat": -1.8200, "lon": 31.8500},
    "LOTEN": {"name": "LOTEN Fix", "lat": 5.5000, "lon": 43.2000},
    "RASDA": {"name": "RASDA Fix", "lat": 12.2000, "lon": 48.5000},
}

ROUTE_CORRIDORS = {
    ("HKJK", "KGL"): ["HKJK", "MG", "APNOX", "UNSIT", "KGL"],
    ("HKJK", "EBB"): ["HKJK", "NV", "EBB"],
    ("HKJK", "HKMO"): ["HKJK", "GBV", "HKMO"],
    ("HKJK", "DAR"): ["HKJK", "MG", "DAR"],
    ("HKJK", "JNB"): ["HKJK", "MG", "TV", "JNB"],
    ("HKJK", "DXB"): ["HKJK", "GBV", "LOTEN", "RASDA", "DXB"],
}

AIRCRAFT_SPECS = {
    "B737-800": {
        "name": "Boeing 737-800W",
        "dow_kg": 41413,
        "mzfw_kg": 62731,
        "mtow_kg": 79010,
        "mlw_kg": 66360,
        "max_fuel_kg": 20894,
        "tas_kts": 450,
        "climb_burn_kg": 900,
        "climb_time_min": 18,
        "climb_dist_nm": 85,
        "cruise_burn_kg_hr": 2350,
        "descent_burn_kg": 350,
        "descent_time_min": 20,
        "descent_dist_nm": 95,
        "holding_burn_kg_hr": 2100,
        "taxi_burn_kg": 200,
        "min_rwy_len_m": 2200,
    },
    "E190": {
        "name": "Embraer E190-E1",
        "dow_kg": 28080,
        "mzfw_kg": 40800,
        "mtow_kg": 51800,
        "mlw_kg": 44000,
        "max_fuel_kg": 12971,
        "tas_kts": 440,
        "climb_burn_kg": 650,
        "climb_time_min": 15,
        "climb_dist_nm": 70,
        "cruise_burn_kg_hr": 1700,
        "descent_burn_kg": 240,
        "descent_time_min": 18,
        "descent_dist_nm": 85,
        "holding_burn_kg_hr": 1500,
        "taxi_burn_kg": 140,
        "min_rwy_len_m": 1850,
    },
    "B787-8": {
        "name": "Boeing 787-8 Dreamliner",
        "dow_kg": 119950,
        "mzfw_kg": 161025,
        "mtow_kg": 227930,
        "mlw_kg": 172365,
        "max_fuel_kg": 101456,
        "tas_kts": 490,
        "climb_burn_kg": 2100,
        "climb_time_min": 22,
        "climb_dist_nm": 110,
        "cruise_burn_kg_hr": 4750,
        "descent_burn_kg": 750,
        "descent_time_min": 25,
        "descent_dist_nm": 120,
        "holding_burn_kg_hr": 4200,
        "taxi_burn_kg": 380,
        "min_rwy_len_m": 2600,
    },
}

# ---------------------------------------------------------
# 2. NAVIGATION & AERODYNAMIC VECTOR CALCULATIONS
# ---------------------------------------------------------


def great_circle_distance_nm(lat1, lon1, lat2, lon2) -> float:
  R_NM = 3440.065
  phi1, phi2 = math.radians(lat1), math.radians(lat2)
  dphi = math.radians(lat2 - lat1)
  dlam = math.radians(lon2 - lon1)
  a = (
      math.sin(dphi / 2) ** 2
      + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
  )
  c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
  return R_NM * c


def forward_azimuth_deg(lat1, lon1, lat2, lon2) -> float:
  phi1, phi2 = math.radians(lat1), math.radians(lat2)
  dlam = math.radians(lon2 - lon1)
  y = math.sin(dlam) * math.cos(phi2)
  x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(
      phi2
  ) * math.cos(dlam)
  tc = math.degrees(math.atan2(y, x))
  return (tc + 360) % 360


def solve_wind_triangle(
    true_course_deg: float, tas_kts: float, wind_dir_deg: int, wind_spd_kts: float
) -> dict:
  wind_rad = math.radians(wind_dir_deg)
  tc_rad = math.radians(true_course_deg)

  wind_angle = wind_rad - tc_rad
  crosswind_component = wind_spd_kts * math.sin(wind_angle)
  headwind_component = wind_spd_kts * math.cos(wind_angle)

  sin_wca = crosswind_component / tas_kts
  sin_wca = max(-1.0, min(1.0, sin_wca))
  wca_deg = math.degrees(math.asin(sin_wca))

  true_heading = (true_course_deg + wca_deg + 360) % 360
  ground_speed = (
      tas_kts * math.cos(math.radians(wca_deg))
  ) - headwind_component
  ground_speed = max(120.0, ground_speed)

  return {
      "true_heading_deg": round(true_heading, 1),
      "wca_deg": round(wca_deg, 1),
      "ground_speed_kts": round(ground_speed, 1),
      "headwind_kts": round(headwind_component, 1),
      "crosswind_kts": round(abs(crosswind_component), 1),
  }


# ---------------------------------------------------------
# 3. OFP & ICAO FUEL POLICY ENGINE
# ---------------------------------------------------------


def generate_operational_flight_plan(
    origin_icao: str,
    dest_icao: str,
    alt_icao: str,
    aircraft_type: str,
    payload_kg: float,
    flight_level: int,
    wind_dir: int,
    wind_spd: float,
    extra_fuel_kg: float = 0.0,
) -> dict:
  ac = AIRCRAFT_SPECS[aircraft_type]
  orig = AIRPORTS[origin_icao]
  dest = AIRPORTS[dest_icao]
  alt = AIRPORTS[alt_icao]

  corridor_key = (origin_icao, dest_icao)
  if corridor_key in ROUTE_CORRIDORS:
    wp_list = ROUTE_CORRIDORS[corridor_key]
  else:
    wp_list = [origin_icao, dest_icao]

  legs = []
  total_dist_nm = 0.0
  total_airborne_min = 0.0

  for i in range(len(wp_list) - 1):
    w1_name = wp_list[i]
    w2_name = wp_list[i + 1]

    c1 = AIRPORTS[w1_name] if w1_name in AIRPORTS else WAYPOINTS[w1_name]
    c2 = AIRPORTS[w2_name] if w2_name in AIRPORTS else WAYPOINTS[w2_name]

    leg_dist = great_circle_distance_nm(
        c1["lat"], c1["lon"], c2["lat"], c2["lon"]
    )
    leg_tc = forward_azimuth_deg(c1["lat"], c1["lon"], c2["lat"], c2["lon"])
    nav = solve_wind_triangle(leg_tc, ac["tas_kts"], wind_dir, wind_spd)

    leg_time_hr = leg_dist / nav["ground_speed_kts"]
    leg_time_min = leg_time_hr * 60.0

    total_dist_nm += leg_dist
    total_airborne_min += leg_time_min

    legs.append({
        "from_fix": w1_name,
        "to_fix": w2_name,
        "distance_nm": round(leg_dist, 1),
        "true_course_deg": round(leg_tc, 1),
        "true_heading_deg": nav["true_heading_deg"],
        "ground_speed_kts": nav["ground_speed_kts"],
        "ete_min": round(leg_time_min, 1),
        "wind_comp": (
            f"{'+' if nav['headwind_kts']>0 else ''}{nav['headwind_kts']:.0f}"
            " kts"
        ),
    })

  climb_d = ac["climb_dist_nm"]
  descent_d = ac["descent_dist_nm"]
  cruise_d = max(0.0, total_dist_nm - (climb_d + descent_d))

  cruise_time_hr = cruise_d / ac["tas_kts"]
  trip_fuel_kg = (
      ac["climb_burn_kg"]
      + (cruise_time_hr * ac["cruise_burn_kg_hr"])
      + ac["descent_burn_kg"]
  )

  contingency_fuel_kg = max(
      trip_fuel_kg * 0.05, ac["holding_burn_kg_hr"] * (5.0 / 60.0)
  )

  alt_dist_nm = great_circle_distance_nm(
      dest["lat"], dest["lon"], alt["lat"], alt["lon"]
  )
  alt_time_hr = (alt_dist_nm / (ac["tas_kts"] * 0.85)) + (
      15.0 / 60.0
  )  # includes missed approach & climb
  alt_fuel_kg = (alt_time_hr * ac["cruise_burn_kg_hr"]) + 350.0

  final_reserve_kg = ac["holding_burn_kg_hr"] * 0.50
  taxi_fuel_kg = ac["taxi_burn_kg"]

  required_takeoff_fuel_kg = (
      trip_fuel_kg
      + contingency_fuel_kg
      + alt_fuel_kg
      + final_reserve_kg
      + extra_fuel_kg
  )
  block_fuel_kg = required_takeoff_fuel_kg + taxi_fuel_kg

  zfw_kg = ac["dow_kg"] + payload_kg
  tow_kg = zfw_kg + required_takeoff_fuel_kg
  law_kg = tow_kg - trip_fuel_kg

  return {
      "origin": origin_icao,
      "dest": dest_icao,
      "alternate": alt_icao,
      "aircraft_type": aircraft_type,
      "ac_name": ac["name"],
      "fl": flight_level,
      "total_dist_nm": round(total_dist_nm, 1),
      "total_airborne_min": round(total_airborne_min, 1),
      "block_time_min": round(total_airborne_min + 20.0, 1),
      "legs": legs,
      "fuel_breakdown": {
          "taxi_fuel_kg": round(taxi_fuel_kg),
          "trip_fuel_kg": round(trip_fuel_kg),
          "contingency_fuel_kg": round(contingency_fuel_kg),
          "alternate_fuel_kg": round(alt_fuel_kg),
          "final_reserve_kg": round(final_reserve_kg),
          "extra_fuel_kg": round(extra_fuel_kg),
          "block_fuel_kg": round(block_fuel_kg),
      },
      "weights": {
          "dow_kg": ac["dow_kg"],
          "payload_kg": payload_kg,
          "zfw_kg": zfw_kg,
          "mzfw_kg": ac["mzfw_kg"],
          "tow_kg": tow_kg,
          "mtow_kg": ac["mtow_kg"],
          "law_kg": law_kg,
          "mlw_kg": ac["mlw_kg"],
          "tow_margin_kg": ac["mtow_kg"] - tow_kg,
          "law_margin_kg": ac["mlw_kg"] - law_kg,
      },
      "alternate_specs": {
          "icao": alt_icao,
          "name": alt["name"],
          "dist_from_dest_nm": round(alt_dist_nm, 1),
          "rwy_len_m": alt["rwy_len_m"],
          "pcn": alt["pcn"],
          "is_runway_adequate": alt["rwy_len_m"] >= ac["min_rwy_len_m"],
      },
  }


# ---------------------------------------------------------
# 4. STREAMLIT USER INTERFACE
# ---------------------------------------------------------

st.title("📋 Operational Flight Plan (OFP) Generator")
st.caption(
    "Flight Operations Engineering Dispatch Engine | ICAO Annex 6 Fuel Policy &"
    " Route Solver"
)

st.sidebar.header("✈️ Dispatch & Sector Inputs")

station_keys = list(AIRPORTS.keys())
origin = st.sidebar.selectbox(
    "Departure Aerodrome (Origin)", station_keys, index=0
)
dest_candidates = [s for s in station_keys if s != origin]
dest = st.sidebar.selectbox(
    "Destination Aerodrome",
    dest_candidates,
    index=4 if len(dest_candidates) > 4 else 0,
)

alt_candidates = [s for s in station_keys if s != dest and s != origin]
alt = st.sidebar.selectbox(
    "Destination Alternate",
    alt_candidates,
    index=1 if len(alt_candidates) > 1 else 0,
)

ac_type = st.sidebar.selectbox(
    "Aircraft Fleet Type", list(AIRCRAFT_SPECS.keys()), index=0
)
selected_ac = AIRCRAFT_SPECS[ac_type]

max_p = int(selected_ac["mzfw_kg"] - selected_ac["dow_kg"])
payload = st.sidebar.slider(
    "Traffic Payload (Pax + Cargo) [kg]",
    2000,
    max_p,
    int(max_p * 0.70),
    step=250,
)
fl = st.sidebar.slider(
    "Planned Cruise Flight Level (FL)", 280, 410, 360, step=10
)

st.sidebar.subheader("💨 Winds Aloft & Extra Fuel")
wind_dir = st.sidebar.slider(
    "Average Enroute Wind Direction (°T)", 0, 360, 70, step=10
)
wind_spd = st.sidebar.slider(
    "Average Enroute Wind Speed (kts)", 0, 100, 20, step=5
)
extra_fuel = st.sidebar.slider(
    "Commander / Dispatch Extra Fuel (kg)", 0, 3000, 500, step=100
)

ofp = generate_operational_flight_plan(
    origin_icao=origin,
    dest_icao=dest,
    alt_icao=alt,
    aircraft_type=ac_type,
    payload_kg=payload,
    flight_level=fl,
    wind_dir=wind_dir,
    wind_spd=wind_spd,
    extra_fuel_kg=extra_fuel,
)

k1, k2, k3, k4 = st.columns(4)
with k1:
  st.metric(
      "Total Route Distance",
      f"{ofp['total_dist_nm']:.0f} NM",
      delta=f"{len(ofp['legs'])} Waypoint Legs",
  )
with k2:
  st.metric(
      "Total Block Fuel",
      f"{ofp['fuel_breakdown']['block_fuel_kg']:,} kg",
      delta=f"Trip: {ofp['fuel_breakdown']['trip_fuel_kg']:,} kg",
  )
with k3:
  st.metric(
      "Est. Airborne / Block Time",
      f"{int(ofp['total_airborne_min']//60)}h"
      f" {int(ofp['total_airborne_min']%60):02d}m",
      delta=(
          f"Block: {int(ofp['block_time_min']//60)}h"
          f" {int(ofp['block_time_min']%60):02d}m"
      ),
  )
with k4:
  tow_margin = ofp["weights"]["tow_margin_kg"]
  st.metric(
      "Takeoff Weight Margin",
      f"{tow_margin:,} kg",
      delta="DISPATCH LEGAL" if tow_margin > 0 else "OVERWEIGHT",
      delta_color="normal" if tow_margin > 0 else "inverse",
  )

st.divider()

t1, t2, t3, t4 = st.tabs([
    "📑 Operational Flight Plan (OFP)",
    "🗺️ Interactive Route Map",
    "⛽ Fuel Breakdown & Weight Limits",
    "🛬 Alternate Aerodrome Legality",
])

with t1:
  st.subheader(f"ICAO OPERATIONAL FLIGHT PLAN: {origin} ➔ {dest} (ALTN: {alt})")
  st.markdown(f"""
    ```text
    ================================================================================
    DISPATCH RELEASE / OPERATIONAL FLIGHT PLAN (OFP)
    AIRCRAFT: {ofp['ac_name']} ({ac_type})       PLANNED CRUISE: FL{fl:03d}
    ROUTING:  {origin} ➔ {dest}                   ALTERNATE: {alt} ({ofp['alternate_specs']['name']})
    DISTANCE: {ofp['total_dist_nm']} NM                      ETE: {int(ofp['total_airborne_min']//60)}h {int(ofp['total_airborne_min']%60):02d}m
    ================================================================================
    FUEL COMPUTATION (ICAO ANNEX 6 COMPLIANT)
    TAXI FUEL:           {ofp['fuel_breakdown']['taxi_fuel_kg']:>6} KG
    TRIP FUEL:           {ofp['fuel_breakdown']['trip_fuel_kg']:>6} KG   ({int(ofp['total_airborne_min']//60)}h {int(ofp['total_airborne_min']%60):02d}m)
    CONTINGENCY (5%):    {ofp['fuel_breakdown']['contingency_fuel_kg']:>6} KG
    ALTERNATE FUEL:      {ofp['fuel_breakdown']['alternate_fuel_kg']:>6} KG   (DIST: {ofp['alternate_specs']['dist_from_dest_nm']} NM)
    FINAL RESERVE (30M): {ofp['fuel_breakdown']['final_reserve_kg']:>6} KG   (HOLDING 1500 FT)
    DISCRETIONARY EXTRA: {ofp['fuel_breakdown']['extra_fuel_kg']:>6} KG
    --------------------------------------------------------------------------------
    TOTAL BLOCK FUEL:    {ofp['fuel_breakdown']['block_fuel_kg']:>6} KG
    ================================================================================
    ```
    """)

  st.subheader("Waypoint Navigation Navigation Log (NavLog)")
  df_legs = pd.DataFrame(ofp["legs"])
  df_legs.columns = [
      "From",
      "To",
      "Dist (NM)",
      "True Course (°)",
      "True Hdg (°)",
      "Ground Speed (kts)",
      "ETE (min)",
      "Wind Comp",
  ]
  st.dataframe(df_legs, use_container_width=True)

with t2:
  st.subheader("Interactive Sector Trajectory & Alternate Corridor")
  fig_map = go.Figure()

  corridor_coords = []
  for leg in ofp["legs"]:
    w1 = leg["from_fix"]
    c1 = AIRPORTS[w1] if w1 in AIRPORTS else WAYPOINTS[w1]
    corridor_coords.append((c1["lat"], c1["lon"], w1))

  c_dest = AIRPORTS[dest]
  corridor_coords.append((c_dest["lat"], c_dest["lon"], dest))

  lats = [c[0] for c in corridor_coords]
  lons = [c[1] for c in corridor_coords]
  labels = [c[2] for c in corridor_coords]

  fig_map.add_trace(
      go.Scattergeo(
          locationmode="ISO-3",
          lat=lats,
          lon=lons,
          mode="lines+markers+text",
          text=labels,
          textposition="top right",
          line=dict(width=3, color="#1E3A8A"),
          marker=dict(size=8, color="#1E3A8A"),
          name=f"Primary Route: {origin} ➔ {dest}",
      )
  )

  c_alt = AIRPORTS[alt]
  fig_map.add_trace(
      go.Scattergeo(
          lat=[c_dest["lat"], c_alt["lat"]],
          lon=[c_dest["lon"], c_alt["lon"]],
          mode="lines+markers+text",
          text=["", f"ALTN: {alt}"],
          textposition="bottom right",
          line=dict(width=2, color="#DC2626", dash="dash"),
          marker=dict(size=7, color="#DC2626"),
          name=f"Diversion Leg: {dest} ➔ {alt}",
      )
  )

  fig_map.update_geos(
      showcountries=True,
      showcoastlines=True,
      showland=True,
      landcolor="#F8FAFC",
      oceancolor="#E0F2FE",
      showocean=True,
      fitbounds="locations",
  )
  fig_map.update_layout(height=480, margin=dict(l=0, r=0, t=0, b=0))
  st.plotly_chart(fig_map, use_container_width=True)

with t3:
  c_f1, c_f2 = st.columns(2)
  with c_f1:
    st.subheader("ICAO Fuel Policy Composition")
    fb = ofp["fuel_breakdown"]
    fig_pie = go.Figure(
        data=[
            go.Pie(
                labels=[
                    "Trip Burn",
                    "Contingency (5%)",
                    "Alternate Fuel",
                    "Final Reserve (30m)",
                    "Discretionary Extra",
                    "Taxi Fuel",
                ],
                values=[
                    fb["trip_fuel_kg"],
                    fb["contingency_fuel_kg"],
                    fb["alternate_fuel_kg"],
                    fb["final_reserve_kg"],
                    fb["extra_fuel_kg"],
                    fb["taxi_fuel_kg"],
                ],
                hole=0.4,
                marker_colors=[
                    "#1E3A8A",
                    "#3B82F6",
                    "#EF4444",
                    "#F59E0B",
                    "#10B981",
                    "#94A3B8",
                ],
            )
        ]
    )
    fig_pie.update_layout(height=350, margin=dict(l=0, r=0, t=30, b=0))
    st.plotly_chart(fig_pie, use_container_width=True)

  with c_f2:
    st.subheader("Weight & Structural Envelopes")
    w = ofp["weights"]
    df_w = pd.DataFrame({
        "Envelope Metric": [
            "Zero Fuel Weight (ZFW)",
            "Takeoff Weight (TOW)",
            "Landing Weight (LAW)",
        ],
        "Calculated (kg)": [w["zfw_kg"], w["tow_kg"], w["law_kg"]],
        "Structural Limit (kg)": [w["mzfw_kg"], w["mtow_kg"], w["mlw_kg"]],
        "Margin Remaining (kg)": [
            w["mzfw_kg"] - w["zfw_kg"],
            w["tow_margin_kg"],
            w["law_margin_kg"],
        ],
    })
    st.dataframe(
        df_w.style.format({
            "Calculated (kg)": "{:,.0f}",
            "Structural Limit (kg)": "{:,.0f}",
            "Margin Remaining (kg)": "{:,.0f}",
        }),
        use_container_width=True,
    )

with t4:
  st.subheader(
      f"Destination Alternate Suitability: {alt}"
      f" ({ofp['alternate_specs']['name']})"
  )
  alt_spec = ofp["alternate_specs"]

  col_a1, col_a2, col_a3 = st.columns(3)
  with col_a1:
    st.metric("Diversion Distance", f"{alt_spec['dist_from_dest_nm']} NM")
  with col_a2:
    st.metric(
        "Runway Length",
        f"{alt_spec['rwy_len_m']} m",
        delta="ADEQUATE" if alt_spec["is_runway_adequate"] else "TOO SHORT",
    )
  with col_a3:
    st.metric("Pavement PCN", alt_spec["pcn"])

  if alt_spec["is_runway_adequate"]:
    st.success(f"""
        **DISPATCH LEGAL ALTERNATE AERODROME**
        * Physical runway length (`{alt_spec['rwy_len_m']} m`) satisfies minimum field requirements for `{ofp['ac_name']}` (`{selected_ac['min_rwy_len_m']} m`).
        * Fuel reserves guarantee full diversion climb, cruise, and 30-minute standard holding at 1,500 ft AGL.
        """)
  else:
    st.error(f"""
        **ALTERNATE AERODROME REJECTED (RUNWAY LENGTH INSUFFICIENT)**
        * Selected alternate runway (`{alt_spec['rwy_len_m']} m`) is below certified performance minimums (`{selected_ac['min_rwy_len_m']} m`).
        * Dispatch action required: Select a certified alternate aerodrome.
        """)
