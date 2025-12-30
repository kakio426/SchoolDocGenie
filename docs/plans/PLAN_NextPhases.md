# School-Doc Genie: Next Phases Implementation Plan (Phase 11-15)

Status: ⏳ Pending
Started: 2025-12-30
Last Updated: 2025-12-30
Estimated Completion: 2026-01-15

## 📋 Overview

### Feature Description
이 계획은 School-Doc Genie의 핵심 기능(변환, 분석, 저장, 검색)을 넘어, 사용자가 공문을 더 효율적으로 활용할 수 있도록 돕는 실무 강화 기능들을 포함합니다.

### Success Criteria
- [ ] **AI 채팅**: 개별 공문 및 전체 아카이브에 대한 질의응답 (RAG) 기능 구현
- [ ] **일괄 처리**: 다량의 공문을 한 번에 업로드하고 분석하는 기능
- [ ] **고급 검색**: 날짜, 문서 번호 등 상세 필터를 통한 정밀 검색
- [ ] **HWP 결과 내보내기**: 분석 결과를 학교 표준 HWP 양식에 맞게 변환하여 다운로드
- [ ] **대시보드**: 문서 통계 및 주요 현황 시각화

---

## 🏗️ Architecture Decisions

| Decision | Rationale | Trade-offs |
| :---- | :---- | :---- |
| **Streamlit-style Chat** | 직관적인 대화형 UI로 RAG 활용 극대화 | 단순 분석 결과 대비 UI 복잡도 증가 |
| **Concurrent Processing** | 일괄 업로드 시 속도 향상 (FastAPI Background Tasks) | 서버 자원 소모량 증가 |
| **Template Filling (pyhwpx)** | 분석 결과를 실무 문서로 즉시 전환 | 한글 프로그램 의존성 유지 (Windows 전용) |

---

## 🚀 Implementation Phases

### Phase 11: AI 채팅 인터페이스 및 RAG 고도화
Goal: 단일 문서 및 전체 저장소에 대해 AI와 대화하며 정보를 찾는 기능 구현  
Verification Mode: 🖥️ TERMINAL ONLY (No Browser)  
Status: ⏳ Pending

#### Tasks
**🔴 RED: Write Failing Tests First**
- [ ] **Test 11.1**: `/chat` 엔드포인트의 RAG 응답 기능 테스트 코드 작성
- [ ] **Test 11.2**: 특정 문서 ID를 컨텍스트로 지정했을 때의 정확도 테스트

**🟢 GREEN: Implement to Make Tests Pass**
- [ ] **Task 11.3**: `SupabaseService.query_rag` 메서드 구현
- [ ] **Task 11.4**: FastAPI `/chat` 엔드포인트 구현 (Streaming Response 지원)

**🔵 REFACTOR: Clean Up Code**
- [ ] **Task 11.5**: 프롬프트 템플릿 최적화 및 토큰 관리 로직 개선

---

### Phase 12: 일괄 업로드 및 파일 관리
Goal: 여러 파일을 한 번에 처리하고 진행 상황을 확인할 수 있는 기능  
Verification Mode: 🖥️ TERMINAL ONLY (No Browser)  
Status: ⏳ Pending

#### Tasks
- [ ] **Task 12.1**: `/upload/batch` API 및 비동기 작업(Task Queue) 구현
- [ ] **Task 12.2**: 전체 문서 목록 조회 및 삭제 기능 구현 (Pagination 포함)

---

### Phase 13: 고급 필터링 및 통계 검색
Goal: 날짜 범위, 키워드 포함/제외, 문서 분류 등 정밀 검색 엔진 구축  
Verification Mode: 🖥️ TERMINAL ONLY (No Browser)  
Status: ⏳ Pending

#### Tasks
- [ ] **Task 13.1**: Supabase SQL 필터링 로직 추가 (날짜, 문서번호 등)
- [ ] **Task 13.2**: 검색 결과 내에서 '주요 키워드 클라우드' 데이터 생성 API

---

### Phase 14: 분석 결과 HWP 템플릿 출력
Goal: AI 분석 결과를 실제 한글(HWP) 기안문/보고서 양식으로 자동 생성  
Verification Mode: 🧪 JSDOM / HEADLESS  
Status: ⏳ Pending

#### Tasks
- [ ] **Task 14.1**: `pyhwpx`를 이용한 HWP 템플릿 필링(Field Fill) 서비스 개발
- [ ] **Task 14.2**: `/export/hwp` 엔드포인트 생성 및 바이너리 다운로드 지원

---

### Phase 15: 종합 대시보드 및 리포팅
Goal: 처리된 문서들의 통계를 시각화하고 기간별 분석 리포트 생성  
Verification Mode: ⚠️ BROWSER ALLOWED (Visual check)  
Status: ⏳ Pending

#### Tasks
- [ ] **Task 15.1**: 기간별 문서 유입량 및 업무 카테고리 분포 통계 API
- [ ] **Task 15.2**: 분석 결과를 모은 '주간/월간 업무 보고' 자동 생성 기능

---

## 🧪 Test Strategy (Terminal First)
- 모든 로직은 Browser를 띄우지 않고 `pytest`와 `curl`을 통해 검증합니다.
- 품질 게이트: 테스트 커버리지 80% 이상 유지, 모든 Lint 통과.

## ⚠️ Risk Assessment
| Risk | Probability | Impact | Mitigation Strategy |
| :---- | :---- | :---- | :---- |
| Gemini API 비용 | Medium | Medium | 캐싱 및 토큰 최적화 로직 강화 |
| HWP 변환 실패 (복잡한 표) | Low | Medium | HTML 변환 후 정제 로직 예외 처리 강화 |

## 📚 References
- [pyhwpx Docs](https://pyhwpx.github.io/)
- [Supabase Vector Docs](https://supabase.com/docs/guides/ai)
- [Gemini API reference](https://ai.google.dev/api/rest)
