부동산데이터베이스 구축 길잡이.


이 리포지토리가 파이썬으로 부동산 데이터를 분석하실 분들의 길잡이가 되길 바라며,

사용의 목적은 연구용, 2차 서비스 등 제한을 두지 않습니다.


다만, 영리적 목적(서비스 구축 등)으로 사용시

출처를 반드시 표기해 주시길 바라며


특히 이 소스코드를 무단으로 표절하여

강의 플랫폼(클래스101, 패스트캠퍼스 등) 등지에서 강의하는 일은

절대 없길 바랍니다.


이 리포지토리 내 코드를 사용하였을 경우,

해당 언급사항에 대해 동의한것으로 간주되며,

지키지않음으로 발생하는 불이익은 사용자에게 있습니다.


스스로 양심에 찔리는 행위를 하지 맙시다!


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

