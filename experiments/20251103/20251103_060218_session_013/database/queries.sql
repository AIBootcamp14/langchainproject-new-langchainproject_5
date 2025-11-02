-- 실행 시간: 2025-11-03 06:02:30
                            -- 도구: 
                            -- 설명: 
                        -- 파라미터: ('%BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding%',)
-- 결과 개수: 1


        SELECT paper_id, title, authors, abstract, publish_date
        FROM papers
        WHERE title ILIKE %s
        LIMIT 1
        ;

