import streamlit as st
import paho.mqtt.client as mqtt
import json
import time
import random
import numpy as np
import os
from datetime import datetime, timezone

# --- 1. Configuration & Initial State ---
st.set_page_config(page_title="AI Predictive Maintenance Simulator", layout="wide")
st.title("🛡️ Integrated AI Fire & Fault Prediction Simulator")

if 'simulation_state' not in st.session_state:
    st.session_state.simulation_state = {
        "temp": 24.0, 
        "humi": 45.0,
        "arc": 0.0,
        "vibe": 0.95,
        "co": 2.0,     # Normal state for CO (0-5 ppm)
        "smoke": 0.0   # Normal state for Smoke (0%)
    }

if 'running' not in st.session_state:
    st.session_state.running = False
if 'step' not in st.session_state:
    st.session_state.step = 1

def toggle_run():
    st.session_state.running = not st.session_state.running

# --- 2. Sidebar: Control Parameters ---
with st.sidebar:
    st.header("🎛️ Scenario Control")
    load_amp = st.slider("Load Current (Amperes)", 0.0, 150.0, 20.0)
    
    threat_type = st.selectbox("Primary Threat Scenario", 
                               ["Normal", "insulation_aging", "fire_overload", "condensation", "breakdown"])
    intensity = st.slider("Anomaly Intensity (Probability Base)", 0.0, 1.0, 0.1)
    
    st.markdown("---")
    st.header("📡 Communication")
    broker = st.text_input("MQTT Broker", "broker.emqx.io")
    topic = st.text_input("Publish Topic", "factory/ai/prediction_output")
    hz = st.slider("Publish Frequency (Hz)", 1, 10, 1)
    sb_id = st.text_input("Switchboard ID", "SB-251212140925-P")

    st.markdown("---")
    st.header("💾 Local Storage")
    save_local = st.checkbox("Save output locally", value=False)
    save_dir = st.text_input("Save Directory", "/Users/mdproduct/Documents/MqttDataGen/")
    
st.button("🚀 Start / 🛑 Stop MQTT Stream", type="primary", use_container_width=True, on_click=toggle_run)

# --- 3. Logical Engine ---
def determine_system_status(temp, co, smoke, arc):
    """
    Determine the system status based on sensor guidelines:
    - Normal (정상): All sensors within normal ranges
    - Caution (주의): Temp >= 50, CO >= 70, Smoke >= 5, or intermittent Arc (> 0)
    - Warning (경고): Temp >= 65, CO >= 150, Smoke >= 10, or sustained Arc (> 0.5)
    - Danger (위험): Temp >= 75 OR CO >= 400 OR Smoke >= 15 OR (High Temp + Gas/Smoke + Arc)
    """
    status, color, icon = "Normal (정상)", "green", "🟢"
    
    # Caution (황색)
    if temp >= 50 or co >= 70 or smoke >= 5 or arc > 0:
        status, color, icon = "Caution (주의)", "orange", "🟡"
        
    # Warning (주황색)
    if temp >= 65 or co >= 150 or smoke >= 10 or arc >= 0.5:
        status, color, icon = "Warning (경고)", "orange", "🟠"
        
    # Danger (적색)
    # Using specific Danger thresholds from the tables
    if temp >= 75 or co >= 400 or smoke >= 15 or (temp >= 75 and (co >= 150 or smoke >= 15) and arc >= 1.0):
        status, color, icon = "Danger (위험)", "red", "🔴"
        
    return status, color, icon

def generate_organic_packets(load, threat, p_base, step, current_sb_id):
    prev = st.session_state.simulation_state
    
    # 1. Arc Logic
    # Arc flashes are short bursts of energy resulting from insulation failure or loose connections
    is_arc_active = (threat == "insulation_aging" and random.random() > 0.75) 
    arc_val = np.random.normal(3.5, 1.0) * p_base if is_arc_active else 0.0
    # Let's add continuous micro-arcs for severe breakdown
    if threat == "breakdown" and p_base > 0.5:
        arc_val = max(arc_val, np.random.normal(1.0, 0.5))
    arc_val = max(0.0, arc_val)
    
    # 2. Temperature Logic (I^2R Heating + Arc Heat)
    # Target temperature depends on the electrical load (Heating)
    target_temp = 24.0 + (load**2 * 0.003) 
    if threat == "fire_overload": target_temp += (p_base * 60) # Massive heat surge
    
    # Arc flashes add a sudden surge of heat (localized plasma)
    target_temp += (arc_val * 15.0)
    
    # Apply thermal inertia (System heats up gradually, cools down gradually)
    inertia_factor = 0.05
    noise_temp = np.random.normal(0, 0.1)
    temp = prev['temp'] + (target_temp - prev['temp']) * inertia_factor + noise_temp
    
    # 3. Humidity Logic (Relative Humidity is inversely correlated to Temperature)
    # As temp rises in an enclosed switchboard, RH drops. 
    # Condensation threat forces external moisture in.
    base_target_humi = 45.0
    if threat == "condensation":
        base_target_humi = 80.0 + (p_base * 20.0) # Up to 100%
        
    # Apply inverse relationship to temperature (simple approximation)
    temp_diff = max(0, temp - 24.0)
    target_humi = base_target_humi - (temp_diff * 0.8) # Temp up by 10C -> RH down by 8%
    
    humi = prev['humi'] + (target_humi - prev['humi']) * 0.1 + np.random.normal(0, 0.5)
    humi = max(0.0, min(100.0, humi))
    
    # 4. Vibration Logic
    target_vibe = 0.95
    if threat == "breakdown":
        target_vibe += (p_base * 0.4) # Loosened mechanical parts rumble
    vibe = prev['vibe'] + (target_vibe - prev['vibe']) * 0.3 + np.random.normal(0, 0.005)
    
    # 5. CO (Carbon Monoxide) Logic - Arrhenius Equation inspired Pyrolysis
    # Insulation (e.g. PVC) starts out-gassing CO as it approaches 80-100+ degrees C.
    co_emission_rate = 0.0
    if temp > 75.0:
        # Exponential increase in CO emission based on temperature exceeding safe limits
        co_emission_rate = min(50.0, np.exp(0.12 * (temp - 75.0)) * p_base)
    # Sudden large arc vaporizes insulation instantly creating CO burst
    if arc_val > 1.0:
        co_emission_rate += (arc_val * 20.0)
        
    co_decay = prev['co'] * 0.05 # Switchboard ventilation removes CO over time
    background_co = np.random.normal(2.0, 0.5) # Natural trace CO
    
    co = prev['co'] + co_emission_rate - co_decay
    co = max(background_co, co)
    
    # 6. Smoke (4uP-SM) Logic - Time Delayed Integration of severe CO & High Temp
    # Smoldering creates CO first. Open flame or severe charring later creates visible smoke.
    smoke_emission_rate = 0.0
    if co > 100.0 and temp > 85.0:
        # Smoke only starts building after a critical mass of CO and heat (Fire ignition)
        smoke_emission_rate = (co - 100.0) * 0.05 # Proportional to severe CO
        
    smoke_decay = prev['smoke'] * 0.02 # Smoke lingering (slower decay than CO)
    smoke = prev['smoke'] + smoke_emission_rate - smoke_decay + np.random.normal(0, 0.1)
    smoke = max(0.0, min(100.0, smoke))

    # Save state
    st.session_state.simulation_state = {
        "temp": temp, "humi": humi, "arc": arc_val, "vibe": vibe, "co": co, "smoke": smoke
    }

    # ISO 8601 UTC timestamp format
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Generate isolated JSON packets per sensor
    packets = [
        {"sb_id": current_sb_id, "device_id": f"{current_sb_id}001", "type": "temperatur", "value": round(temp, 2), "unit": "C", "ts": ts},
        {"sb_id": current_sb_id, "device_id": f"{current_sb_id}002", "type": "humidity", "value": round(humi, 2), "unit": "%", "ts": ts},
        {"sb_id": current_sb_id, "device_id": f"{current_sb_id}003", "type": "arc_detected", "value": round(arc_val, 2), "unit": "-", "ts": ts},
        {"sb_id": current_sb_id, "device_id": f"{current_sb_id}004", "type": "vibration", "value": round(vibe, 4), "unit": "G", "ts": ts},
        {"sb_id": current_sb_id, "device_id": f"{current_sb_id}005", "type": "4uP-Co", "value": round(co, 1), "unit": "ppm", "ts": ts},
        {"sb_id": current_sb_id, "device_id": f"{current_sb_id}006", "type": "4uP-SM", "value": round(smoke, 2), "unit": "%", "ts": ts}
    ]
    
    status_info = determine_system_status(temp, co, smoke, arc_val)
    
    return packets, status_info

# --- 4. Main Execution Loop ---
display_area = st.empty()

if st.session_state.running:
    try:
        # Check compatibility for paho-mqtt ^2.0.0 vs older versions
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    except AttributeError:
        client = mqtt.Client()
            
    try:
        try:
            client.connect(broker, 1883)
        except Exception as e:
            display_area.error(f"MQTT Connection Error: {e}")
            st.session_state.running = False
            st.rerun()
            
        packets, status_info = generate_organic_packets(load_amp, threat_type, intensity, st.session_state.step, sb_id)
        
        # Save locally if checked
        if save_local:
            os.makedirs(save_dir, exist_ok=True)
            log_file_path = os.path.join(save_dir, "simulated_data.jsonl")
            with open(log_file_path, "a", encoding="utf-8") as f:
                for packet in packets:
                    f.write(json.dumps(packet) + "\n")
                    
        for packet in packets:
            client.publish(topic, json.dumps(packet))
            
        with display_area.container():
            st.success(f"📡 Connected to {broker} - Publishing at {hz} Hz")
            
            # Display Status
            status_text, status_color, status_icon = status_info
            st.markdown(f"### Current System Status: {status_icon} :{status_color}[**{status_text}**]")
            st.markdown("---")
            
            m_col1, m_col2, m_col3 = st.columns(3)
            m_col1.metric("Temperature", f"{packets[0]['value']} °C")
            m_col2.metric("Humidity", f"{packets[1]['value']} %")
            m_col3.metric("Arc Signal", f"{packets[2]['value']}")
            
            m_col4, m_col5, m_col6 = st.columns(3)
            m_col4.metric("Vibration", f"{packets[3]['value']} G")
            m_col5.metric("CO Level (4uP-Co)", f"{packets[4]['value']} ppm")
            m_col6.metric("Smoke (4uP-SM)", f"{packets[5]['value']} %")
            
            st.write("#### Outbound JSON Payloads")
            for p in packets:
                st.json(p)
                
        st.session_state.step += 1
        time.sleep(1/hz)
        
        # Trigger next loop iteration cleanly in Streamlit
        st.rerun()
        
    except Exception as e:
        display_area.error(f"MQTT Error: {e}")
        st.session_state.running = False
    finally:
        client.disconnect()
else:
    display_area.info("⏸️ Simulator is currently stopped. Click the Start / Stop button to begin.")