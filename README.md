# School-Doc Genie

학교 행정 공문(HWP, XLS)을 보안 우려 없이 AI로 분석하고 아카이빙하는 시스템입니다.

## 주요 기능

- **클라이언트 사이드 개인정보 마스킹**: 브라우저에서 업로드 전 자동 비식별화
- **문서 변환**: HWP/Excel 파일을 AI가 이해하기 쉬운 Markdown으로 변환
- **AI 분석**: Gemini 3.0 Flash를 활용한 요약 및 키워드 추출
- **RAG 검색**: Supabase Vector DB를 통한 유사 공문 검색

## 프로젝트 구조

```
School-Doc Genie/
├── backend/           # FastAPI 백엔드
│   ├── services/      # 비즈니스 로직 (Gemini, Converter, Supabase)
│   ├── core/          # 로거 등 핵심 유틸리티
│   └── tests/         # Pytest 테스트
├── frontend/          # Next.js 프론트엔드
│   └── src/
│       └── utils/     # 마스킹 유틸리티
└── docs/
    └── plans/         # 구현 계획서
```

## 설치 및 실행

### 백엔드

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# .env 파일에 API 키 입력
uvicorn main:app --reload
```

### 프론트엔드

```bash
cd frontend
npm install
npm run dev
```

## 환경 변수

### Backend (.env)
- `GEMINI_API_KEY`: Google AI Studio API 키
- `SUPABASE_URL`: Supabase 프로젝트 URL (선택)
- `SUPABASE_ANON_KEY`: Supabase Anon 키 (선택)

## 테스트

```bash
# 백엔드 테스트
cd backend
python -m pytest

# 프론트엔드 테스트
cd frontend
npm test
```

## 기술 스택

- **Backend**: FastAPI, Python 3.10+
- **Frontend**: Next.js 15, TypeScript, TailwindCSS
- **AI**: Google Gemini 3.0 Flash, Text Embedding 004
- **Database**: Supabase (PostgreSQL + pgvector)
- **Testing**: Pytest, Jest

## 개발 진행 상황

✅ Phase 1: 프로젝트 기반 및 API 스캐폴딩  
✅ Phase 2: 클라이언트 사이드 개인정보 마스킹  
✅ Phase 3: 문서 변환기 (HWP/XLS to Markdown)  
✅ Phase 4: AI 분석 및 컨텍스트 캐싱  
✅ Phase 5: RAG 및 아카이빙 (Supabase)  

**전체 진행률: 100% 🎉**

## 라이선스

MIT
