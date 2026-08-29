# Operational-Flight-Plan-OFP-Generator-with-Alternate-Diversion-Logic

# 📋 Commercial Airline Operational Flight Plan (OFP) Generator

An end-to-end Flight Operations Engineering dispatch software platform designed to generate ICAO Annex 6 compliant Operational Flight Plans (OFP), calculate waypoint navigation logs with aerodynamic wind triangle corrections, and validate destination alternate aerodrome dispatch legality.

[![Live Demo](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://scalstein-operational-flight-plan-generator.streamlit.app/)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📌 1. Operational Context & Problem Statement
An **Operational Flight Plan (OFP)** is the safety-critical dispatch contract governing commercial flight execution. Flight dispatchers must accurately account for aircraft structural weight limits, en-route wind vectors aloft, corridor waypoint geometry, and mandatory regulatory fuel reserves.

This system provides a full flight planning engine that computes:
1. **True Course & Wind Correction Angles (WCA):** Great-circle waypoint track geometry.
2. **Ground Speed ($GS$) & Estimated Time En-Route (ETE):** Corrected for dynamic headwind/tailwind aloft components.
3. **ICAO Annex 6 Fuel Policy:** Strict accounting of Taxi, Trip, Contingency (5%), Alternate, Final Reserve (30-min holding at 1,500 ft AGL), and Commander Discretionary Extra fuel.
4. **Alternate Aerodrome Suitability:** Runway length and pavement classification number (PCN) dispatch validation.

---

## 🧮 2. Mathematical Formulation & Navigation Math

### A. Great Circle Forward Azimuth (True Course $\theta$)
$$\theta = \text{atan2}\left(\sin(\Delta \lambda) \cdot \cos(\phi_2), \; \cos(\phi_1) \cdot \sin(\phi_2) - \sin(\phi_1) \cdot \cos(\phi_2) \cdot \cos(\Delta \lambda)\right)$$

### B. Wind Triangle & Ground Speed Decomposition
Given True Airspeed ($TAS$), True Course ($\theta$), wind direction ($\theta_{\text{wind}}$), and wind velocity ($V_{\text{wind}}$):

$$\sin(\text{WCA}) = \frac{V_{\text{wind}}}{TAS} \cdot \sin(\theta_{\text{wind}} - \theta)$$

$$\text{True Heading } (TH) = \theta + \text{WCA}$$

$$\text{Ground Speed } (GS) = TAS \cdot \cos(\text{WCA}) - V_{\text{wind}} \cdot \cos(\theta_{\text{wind}} - \theta)$$

$$\text{Segment ETE} = \frac{\text{Segment Distance}}{GS}$$

### C. ICAO Annex 6 Fuel Reserve Policy
$$\text{Block Fuel} = M_{\text{taxi}} + M_{\text{trip}} + M_{\text{contingency}} + M_{\text{alternate}} + M_{\text{final\_reserve}} + M_{\text{extra}}$$

*Where:*
* $M_{\text{contingency}} = \max\left(0.05 \cdot M_{\text{trip}}, \; \text{Burn for 5-min holding}\right)$
* $M_{\text{final\_reserve}} = \text{Fuel burn for 30 minutes at 1,500 ft AGL in standard holding configuration}$

---

## 🏗️ 3. Repository Architecture

```text
operational-flight-plan-generator/
├── app.py                     # Self-contained Streamlit application & navigation solver
├── requirements.txt           # Production dependencies
├── .gitignore
├── README.md
└── tests/
    └── test_ofp.py            # Automated pytest unit test vectors
