-- 실행 시간: 2025-11-04 21:58:00
                            -- 도구: 
                            -- 설명: 
                        -- 파라미터: ('%첫번째로 말한 논문의 제목 정보가 제공되지 않아 추출할 수 없습니다. 논문 제목을 명확히 입력해주세요.%',)
-- 결과 개수: 0


        SELECT paper_id, title, authors, abstract, publish_date
        FROM papers
        WHERE title ILIKE %s
        LIMIT 1
        ;

-- 실행 시간: 2025-11-04 21:58:44
                            -- 도구: 
                            -- 설명: 
                        -- 파라미터: ('%Meta-prompting Optimized Retrieval-augmented Generation%',)
-- 결과 개수: 1


        SELECT paper_id, title, authors, abstract, publish_date
        FROM papers
        WHERE title ILIKE %s
        LIMIT 1
        ;

