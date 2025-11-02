-- 실행 시간: 2025-11-03 05:45:00
                            -- 도구: 
                            -- 설명: 
                        -- 파라미터: ('%BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding%',)
-- 결과 개수: 1


        SELECT paper_id, title, authors, abstract, publish_date
        FROM papers
        WHERE title ILIKE %s
        LIMIT 1
        ;

-- 실행 시간: 2025-11-03 05:53:03
                            -- 도구: rag_glossary
                            -- 설명: 용어집 검색
                        
SELECT term, definition, easy_explanation, hard_explanation, category FROM glossary WHERE term ILIKE %s;

