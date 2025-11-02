-- 실행 시간: 2025-11-03 05:23:27
                            -- 도구: rag_glossary
                            -- 설명: 용어집 검색
                        
SELECT term, definition, easy_explanation, hard_explanation, category FROM glossary WHERE term ILIKE %s;

