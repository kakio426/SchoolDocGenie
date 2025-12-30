# Implementation Plan: School-Doc Genie (Hybrid Deployment Strategy)

Status: ✅ Complete
Started: 2025-12-30
Last Updated: 2025-12-31

## 📋 Overview

### Feature Description
기존의 서버 중심 파일 변환 방식을 '로컬 에이전트(PC 설치형)' 방식으로 분리하여, 한글과컴퓨터 라이선스 위반 소지를 원천 차단하고 **교육청 보안 지침(데이터 외부 유출 방지)**을 준수하는 하이브리드 아키텍처로 전환합니다. 로컬에서 비식별화 및 사용자 검토(Preview/Edit)를 수행하여 보안성을 극대화합니다.

### Success Criteria
- [x] **Local Agent**: Windows PC에서 실행되는 .exe 형태로, HWP 변환 및 비식별화를 로컬에서 수행
- [x] **Preview & Confirm**: AI 전송 전, 마스킹된 텍스트를 사용자가 직접 확인하고 수정할 수 있는 GUI 팝업 제공
- [x] **Clean Server**: 서버에서 HWP 변환 로직 제거 및 텍스트 기반 분석 API로 전환
- [x] **Real-time Sync**: 에이전트에서 전송 시 웹 대시보드에 실시간으로 분석 결과 반영

---

## 🏗️ Architecture Decisions

| Decision | Rationale | Trade-offs |
| :---- | :---- | :---- |
| **Local Agent (Tkinter GUI)** | 사용자 친화적인 검토 환경 제공 및 법적 책임 분산 | 사용자가 별도 프로그램을 실행해야 함 |
| **Human-in-the-loop** | AI 마스킹의 한계를 사용자가 직접 보완하여 보안 사고 방지 | 원클릭 방식보다 한 단계 더 필요함 |
| **Server-Side AI Only** | 리눅스 배포 호환성 확보 및 원본 파일 유출 위험 제거 | 텍스트 형태로만 서버에 전송됨 |

---

## 🚀 Implementation Phases

### Phase 1: Backend Diet (Server Refactoring)
Goal: 서버에서 HWP 변환 로직을 완전히 제거하고, 텍스트 분석 API만 남김  
Status: ✅ Complete

- [x] **Task 1.1**: `POST /analyze/text` 엔드포인트 구현 (Markdown 수신)
- [x] **Task 1.2**: 웹 직접 업로드 기능 및 서버 내 HWP 변환 로직 제거
- [x] **Task 1.3**: 서버 환경 변수(Supabase, Gemini) 로딩 및 인식 로직 유연화
- [x] **Task 1.4**: 리무버블 아키텍처를 위한 `ConverterService` 리팩토링

### Phase 2: Local Agent Core Logic
Goal: 클라이언트용 독립 변환 및 마스킹 스크립트 구현  
Status: ✅ Complete

- [x] **Task 2.1**: 로컬 전용 한글 변환 엔진(`LocalConverterService`) 구현
- [x] **Task 2.2**: 로컬 개인정보 마스킹 엔진(`MaskingService`) 구현
- [x] **Task 2.3**: API 전송 모듈 구현 및 통합 테스트

### Phase 3: Packaging & UI (The ".exe" with Safety Nets)
Goal: 법적 보호를 위한 미리보기/편집 UI가 포함된 독립 실행 파일 제작  
Status: ✅ Complete

- [x] **Task 3.1**: **Main GUI (Tkinter)** 기반 에이전트 인터페이스 구현
- [x] **Task 3.2**: **[Critical] Preview & Edit Popup** 구현 (전송 전 텍스트 수정 기능)
- [x] **Task 3.3**: **Legal Disclaimer Popup** 구현 (최초 실행 시 약관 동의 강제)
- [x] **Task 3.4**: 드래그 앤 드롭 및 파일 선택 다이얼로그 연동
- [x] **Task 3.5**: PyInstaller 기반 빌드 테스트 완료 (`agent_main.py` -> `.exe`)

### Phase 4: Web Dashboard Sync
Goal: 로컬에서 보낸 데이터를 웹에서 실시간으로 확인  
Status: ✅ Complete

- [x] **Task 4.1**: **Supabase Realtime**을 통한 문서 목록 자동 갱신 구현
- [x] **Task 4.2**: 하이브리드용 웹 대시보드 개편 (직접 업로드 제거 및 에이전트 가이드 추가)
- [x] **Task 4.3**: 실시간 피드 내 문서 카드 및 상세 조회 연동

---

## 📝 Learnings & Notes
- **보안의 민감성**: 단순 자동화보다 사용자가 한 번 더 확인(Preview)하게 만드는 것이 교육 현장의 보안 신뢰도를 높이는 데 결정적임.
- **아키텍처 설계**: 서버 라이선스 이슈를 해결하기 위해 로컬의 리소스를 활용하는 하이브리드 방식이 리눅스 배포와 라이선스 합법성을 동시에 해결함.
