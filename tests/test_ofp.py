"""
Automated unit tests for Operational Flight Plan navigation and fuel policy calculations.
"""

from app import (
    forward_azimuth_deg,
    generate_operational_flight_plan,
    great_circle_distance_nm,
    solve_wind_triangle,
)


def test_distance_and_azimuth():
  dist = great_circle_distance_nm(-1.3192, 36.9278, -1.9686, 30.1394)
  az = forward_azimuth_deg(-1.3192, 36.9278, -1.9686, 30.1394)
  assert 400 < dist < 420
  assert 250 < az < 280


def test_wind_triangle_headwind():
  res = solve_wind_triangle(
      true_course_deg=90.0,
      tas_kts=450.0,
      wind_dir_deg=90,
      wind_spd_kts=50.0,
  )
  assert res["ground_speed_kts"] == 400.0
  assert res["wca_deg"] == 0.0


def test_ofp_generation():
  ofp = generate_operational_flight_plan(
      origin_icao="HKJK",
      dest_icao="KGL",
      alt_icao="EBB",
      aircraft_type="B737-800",
      payload_kg=12000,
      flight_level=360,
      wind_dir=70,
      wind_spd=20,
      extra_fuel_kg=500,
  )
  assert (
      ofp["fuel_breakdown"]["block_fuel_kg"]
      > ofp["fuel_breakdown"]["trip_fuel_kg"]
  )
  assert ofp["weights"]["tow_margin_kg"] > 0
  assert len(ofp["legs"]) > 0


if __name__ == "__main__":
  test_distance_and_azimuth()
  test_wind_triangle_headwind()
  test_ofp_generation()
  print("All OFP generator tests passed successfully!")
