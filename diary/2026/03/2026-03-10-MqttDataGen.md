# Project DevLog: MqttDataGen
* **📅 Date**: 2026-03-10
* **🏷️ Tags**: `#Project` `#DevLog`

---

> 🎯 **Progress Summary**
> 물리 법칙 기반의 센서 상관관계(온도-습도 역관계, CO-연기 지연 발생)를 시뮬레이터(Generater.py)에 성공적으로 반영하고 검증함.

### 🛠️ Execution Details & Changes
* **Git Commits**: `feat(simulator): Apply physics-based logic and validation test`
* **Core File Modifications**:
  * 📄 `Generater.py`: 난수 발생 로직을 열역학/상태 변화 공식 기반 상관관계 로직으로 전면 개편.
  * 📄 `test_physics.py`: 상태 지연(Lag) 및 분포 검증을 위해 250스텝을 강제 실행하는 자동화 테스트 스크립트 작성.
* **Technical Implementation**:
  * 부하 전류 및 아크(Arc) 점화에 따른 열역학적(Heating) 온도 변화 추적.
  * Arrhenius 방정식 기반으로 임계 온도 돌파시 일산화탄소(CO)의 지수적 상승 구현.
  * 연기(Smoke)는 CO가 100ppm을 넘었을 때 비로소 누적 발생하도록 지연 적분(Time-Delayed Integral) 로직 도입.

### 🚨 Troubleshooting
> 🐛 **Problem Encountered**: `test_physics.py` 구동 불가 (Streamlit `ScriptRunContext` 및 session_state 런타임 부재 에러).
> 💡 **Solution**: `st.session_state`를 딕셔너리가 포함된 더미 스텁(Stub)으로 직접 주입하여 CLI 환경에서도 렌더링 없이 시뮬레이션 엔진 틱(Tick)을 테스트하도록 우회.

### ⏭️ Next Steps
- [ ] 인도 팀에게 전달된 요구사항을 바탕으로 AI 모델 아키텍처(LSTM/Transformer) 설계 협의.
- [ ] (필요시) 외부 MQTT Client로 데이터가 정상 수집되는지 End-to-End 동작 확인.
