import sys
import numpy as np
sys.path.append("/Users/mdproduct/Desktop/Danixai_agent/MqttDataGen")

import streamlit as st
st.session_state["simulation_state"] = {
    "temp": 24.0, "humi": 45.0, "arc": 0.0,
    "vibe": 0.95, "co": 2.0, "smoke": 0.0
}
st.session_state["running"] = False
st.session_state["step"] = 1

from Generater import generate_organic_packets

print("--- 1. Running steps of Normal operation ---")
for _ in range(50):
   generate_organic_packets(20.0, "Normal", 0.1, 1, "TEST")

print("Normal State End:", st.session_state.simulation_state)

print("\n--- 2. Running steps of Fire Overload ---")
co_history = []
smoke_history = []
temp_history = []
humi_history = []

for _ in range(200):
   generate_organic_packets(120.0, "fire_overload", 0.9, 1, "TEST")
   state = st.session_state.simulation_state
   co_history.append(state["co"])
   smoke_history.append(state["smoke"])
   temp_history.append(state["temp"])
   humi_history.append(state["humi"])

print("Overload State End:", st.session_state.simulation_state)

print("\n--- 3. Distribution & Physics Check ---")

print("Temp vs Humidity Check:")
print(f"Temp Started at: {temp_history[0]:.2f}, Ended at: {temp_history[-1]:.2f}")
print(f"Humi Started at: {humi_history[0]:.2f}, Ended at: {humi_history[-1]:.2f}")
if temp_history[-1] > temp_history[0] and humi_history[-1] < humi_history[0]:
    print("SUCCESS: Inverse correlation observed between Temp and Humidity.")
else:
    print("WARNING: Temp/Humidity correlation not working properly.")

co_over_100_idx = next((i for i, v in enumerate(co_history) if v > 100), -1)
smoke_over_5_idx = next((i for i, v in enumerate(smoke_history) if v > 5), -1)

print(f"\nCO crossed 100ppm at step: {co_over_100_idx}")
print(f"Smoke crossed 5% at step: {smoke_over_5_idx}")

if smoke_over_5_idx > co_over_100_idx and co_over_100_idx != -1:
    print("SUCCESS: Smoke builds up predictably AFTER heavy CO buildup, matching pyrolysis physical phenomena.")
else:
    print("WARNING: Smoke/CO lag logic failed.")
