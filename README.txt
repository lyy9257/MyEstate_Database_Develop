부동산데이터베이스 구축 길잡이.

1. 공통
    1) config.cfg에 MYSQL DB 정보를 입력합니다.
        -> IP, 계정, 비번, 포트

    2) api_key 폴더에 data.go.kr에서 발급받은 키를 입력합니다.
        -> 그냥 복보로로로복붙

    3) 의존성 패키지를 설치합니다.
        -> pip install -r requirements.txt

    4) areacode, apart 데이터베이스를 만들어줍니다.
        -> CREATE DATABASE areacode, apart;
    
2. 처음 구축 시
    FirstMake.py파일을 돌립니다.
    2010년 데이터부터 적재됩니다.

3. 업데이트 시
    Update.py 파일을 돌립니다.
    2달치 데이터가 추가됩니다. (실거래데이터는 30일내로 신고하기 때문입니다.)

4. 참고사항
    1) SQL Injection에 매우 취약하니, 로컬에서만 사용하시기 바랍니다.
    2) 같은날짜에, 같은아파트, 같은층, 같은평수로, 같은가격에 거래된 데이터는 중복으로 간주하여 적재되지않습니다.
    3) 테이블 명세는 안바쁠때 업데이트 해드릴게요 . . . Sorry

