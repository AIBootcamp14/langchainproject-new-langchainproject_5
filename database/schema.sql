-- ==================== pgvector Extension 활성화 ==================== --
CREATE EXTENSION IF NOT EXISTS vector;


-- ==================== papers 테이블 (논문 메타데이터) ==================== --
CREATE TABLE IF NOT EXISTS papers (
    paper_id SERIAL PRIMARY KEY,                        -- 논문 고유 ID
    title VARCHAR(500) NOT NULL,                        -- 논문 제목
    authors TEXT,                                       -- 저자 목록 (JSON 또는 TEXT)
    publish_date DATE,                                  -- 발표 날짜
    source VARCHAR(100),                                -- 출처 (arXiv, IEEE, ACL 등)
    url TEXT UNIQUE,                                    -- 논문 URL (중복 방지)
    category VARCHAR(100),                              -- 카테고리 (cs.AI, cs.CL, cs.CV 등)
    citation_count INT DEFAULT 0,                       -- 인용 수
    abstract TEXT,                                      -- 논문 초록
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,     -- 생성 시간
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP      -- 수정 시간
);

-- ---------------------- papers 테이블 인덱스 ---------------------- --
CREATE INDEX IF NOT EXISTS idx_papers_title ON papers USING GIN (to_tsvector('english', title));
CREATE INDEX IF NOT EXISTS idx_papers_category ON papers(category);
CREATE INDEX IF NOT EXISTS idx_papers_publish_date ON papers(publish_date DESC);
CREATE INDEX IF NOT EXISTS idx_papers_created_at ON papers(created_at DESC);


-- ==================== glossary 테이블 (용어집) ==================== --
CREATE TABLE IF NOT EXISTS glossary (
    term_id SERIAL PRIMARY KEY,                         -- 용어 고유 ID
    term VARCHAR(200) NOT NULL UNIQUE,                  -- 용어
    definition TEXT NOT NULL,                           -- 기본 정의
    easy_explanation TEXT,                              -- Easy 모드 설명
    hard_explanation TEXT,                              -- Hard 모드 설명
    category VARCHAR(100),                              -- 카테고리 (ML, NLP, CV, RL 등)
    difficulty_level VARCHAR(20),                       -- 난이도 (beginner, intermediate, advanced)
    related_terms TEXT[],                               -- 관련 용어 배열
    examples TEXT,                                      -- 사용 예시
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,     -- 생성 시간
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP      -- 수정 시간
);

-- ---------------------- glossary 테이블 인덱스 ---------------------- --
CREATE INDEX IF NOT EXISTS idx_glossary_term ON glossary(term);
CREATE INDEX IF NOT EXISTS idx_glossary_category ON glossary(category);
CREATE INDEX IF NOT EXISTS idx_glossary_difficulty ON glossary(difficulty_level);


-- ==================== query_logs 테이블 (사용자 질의 로그) ==================== --
CREATE TABLE IF NOT EXISTS query_logs (
    log_id SERIAL PRIMARY KEY,                          -- 로그 고유 ID
    user_query TEXT NOT NULL,                           -- 사용자 질문
    difficulty_mode VARCHAR(20),                        -- 난이도 모드 (easy, hard)
    tool_used VARCHAR(50),                              -- 사용된 도구명
    response TEXT,                                      -- 생성된 응답
    response_time_ms INT,                               -- 응답 시간 (밀리초)
    success BOOLEAN DEFAULT TRUE,                       -- 성공 여부
    error_message TEXT,                                 -- 오류 메시지 (있는 경우)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP      -- 생성 시간
);

-- ---------------------- query_logs 테이블 인덱스 ---------------------- --
CREATE INDEX IF NOT EXISTS idx_query_logs_created_at ON query_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_query_logs_tool_used ON query_logs(tool_used);
CREATE INDEX IF NOT EXISTS idx_query_logs_success ON query_logs(success);


-- ==================== evaluation_results 테이블 (성능 평가 결과) ==================== --
CREATE TABLE IF NOT EXISTS evaluation_results (
    eval_id SERIAL PRIMARY KEY,                         -- 평가 고유 ID
    question TEXT NOT NULL,                             -- 사용자 질문
    answer TEXT NOT NULL,                               -- AI 답변
    accuracy_score INT CHECK (accuracy_score >= 0 AND accuracy_score <= 10),    -- 정확도 점수 (0-10)
    relevance_score INT CHECK (relevance_score >= 0 AND relevance_score <= 10), -- 관련성 점수 (0-10)
    difficulty_score INT CHECK (difficulty_score >= 0 AND difficulty_score <= 10), -- 난이도 적합성 점수 (0-10)
    citation_score INT CHECK (citation_score >= 0 AND citation_score <= 10),    -- 출처 명시 점수 (0-10)
    total_score INT CHECK (total_score >= 0 AND total_score <= 40),             -- 총점 (0-40)
    comment TEXT,                                       -- 평가 코멘트
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP      -- 생성 시간
);

-- ---------------------- evaluation_results 테이블 인덱스 ---------------------- --
CREATE INDEX IF NOT EXISTS idx_evaluation_results_created_at ON evaluation_results(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_evaluation_results_total_score ON evaluation_results(total_score DESC);