# MqttDataGen
🛡️ **Integrated AI Fire & Fault Prediction Simulator**

A Python and Streamlit-based MQTT data generator designed to simulate physical sensor telemetry for AI predictive maintenance and fire/fault detection systems.

Python과 Streamlit 기반으로 제작된 MQTT 데이터 생성기(시뮬레이터)입니다. AI 예지보전 및 화재/결함 예측 시스템용으로 물리적 센서의 텔레메트리 데이터를 모사(Simulate)합니다.

---

## 🇬🇧 English Description

### Overview
This project generates realistic, organically linked sensor data (Temperature, Humidity, Arc, Vibration, CO, Smoke) based on electrical physics (e.g., $I^2R$ heating) and simulated fault conditions. It automatically publishes the generated data to an MQTT broker in real-time.

### Key Features
- **Dynamic Physics Engine**: Changes in Load Current and Threat Scenarios dynamically cascade to affect multiple sensors. (e.g., High temperature or sustained arcs trigger CO and Smoke levels).
- **Streamlit Dashboard**: A real-time interactive UI to adjust scenarios on the fly, offering visual feedback of the "System Status" (`Normal`, `Caution`, `Warning`, `Danger`).
- **Standardized Payload**: Output data strictly follows a separated JSON (JSONL) format, making it easy to integrate with existing AI engines or IoT databases.
- **Local Storage**: Automatically append and save generated payloads as a `.jsonl` file in a specified local directory alongside MQTT publishing.

### Simulated Sensors
- **Temperature (`temperature`)**: Baseline 24°C, rises with load current or overload scenarios.
- **Humidity (`humidity`)**: Baseline 45%, fluctuates and rises sharply during condensation scenarios. 
- **Arc (`arc`)**: **Binary indication (0.0 or 1.0)**. Triggers frequently under insulation aging/breakdown scenarios.
- **Vibration (`vibration`)**: Baseline 60.0 Hz, fluctuates and scatters during mechanical breakdown scenarios.
- **Carbon Monoxide / CO (`co`)**: Baseline 0~5 ppm (sent as %), sharply increases based on Arrhenius equation if temperature rises or arcs occur.
- **Smoke (`tobacco`)**: Baseline 0~100 intensity, increases based on CO accumulation with a slight time delay.

### Usage
```bash
pip install streamlit paho-mqtt numpy
streamlit run Generater.py
```

---

## 🇰🇷 한국어 설명

### 개요
이 프로젝트는 전기적 물리 법칙($I^2R$ 등)과 가상의 결함 시나리오를 바탕으로 유기적으로 연관된 센서 데이터(온도, 습도, 아크, 진동, 일산화탄소, 연기)를 생성하는 시뮬레이터입니다. 생성된 데이터는 실시간으로 MQTT 브로커를 통해 외부로 전송됩니다.

### 주요 기능
- **동적 물리 엔진**: 부하 전류 값이나 위협 시나리오(Threat Scenario)를 변경하면 여러 센서 값이 연쇄적으로 반응합니다. (예: 온도가 상승하거나 아크가 발생하면 피복 탄화를 모사하여 CO 및 연기 수치 증가).
- **Streamlit 대시보드**: 실시간 인터랙티브 UI를 제공하여 시나리오를 즉시 변경할 수 있으며, 시스템 상태(`정상`, `주의`, `경고`, `위험`)를 시각적으로 한눈에 파악할 수 있습니다.
- **표준화된 페이로드**: 출력 데이터는 개별 센서 단위의 완전 분리형 JSON(JSONL) 포맷을 사용하여, 외부 AI 엔진이나 IoT 데이터베이스와 쉽게 연동할 수 있습니다.
- **로컬 파일 저장 지원**: 사이드바 옵션을 통해, 생성되는 모든 MQTT 패킷 데이터를 지정한 로컬 디렉토리에 `.jsonl` 파일 형태로 실시간 누적 기록(Append)할 수 있습니다.

### 모사되는 센서 목록
- **온도 (`temperature`)**: 기본 24℃. 부하 전류가 높거나 과부하 시나리오 시 상승.
- **습도 (`humidity`)**: 기본 45%. 결로(Condensation) 시나리오 적용 시 급상승.
- **아크 (`arc`)**: **바이너리 지표 (0.0 또는 1.0)**. 절연 노후화(Insulation aging) 시나리오 시 발생.
- **진동 (`vibration`)**: 기본 60.0 Hz. 기계적 결함(Breakdown) 시나리오 시 주파수 변이 발생.
- **일산화탄소 / CO (`co`)**: 기본 무해 농도. 온도가 크게 오르거나 아크가 발생하면 지수 함수적으로 급격히 상승(전송 단위 %).
- **연기 (`tobacco`)**: 기본 0~100 수치. CO 수치가 특정 임계점을 넘어가면 시차를 두고 누적 상승함.

### 실행 방법
```bash
pip install streamlit paho-mqtt numpy
streamlit run Generater.py
```
