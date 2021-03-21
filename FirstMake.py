'''
처음 구축시 실행하세요.
(단 apart, areacode 데이터베이스를 먼저 생성 후 실행해야 합니다.)
'''

from Collect import ApartData, Areacode

if __name__ == '__main__':
    
    ## 지역코드 데이터 저장
    areacode = Areacode.Store()
    areacode.routine()

    area_list = (
        '경기도', '강원도', '경상남', '경상북',
        '광주광', '대구광', '대전광', '부산광',
        '서울특', '세종특', '울산광', '인천광',
        '전라남', '전라북', '제주특', '충청남', '충청북'
    )
    
    for area in area_list:
        print("[INFO] Start ApartTradeDetailLog Data Store")
        ApartTradeDetailLog = ApartData.Routine(area, 'First')
        ApartTradeDetailLog.run()