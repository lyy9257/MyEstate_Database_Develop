'''
업데이트시 실행하세요.
'''

from Collect import ApartData

if __name__ == '__main__':
    area_list = (
        '강원도', '경기도', '경상남', '경상북',
        '광주광', '대구광', '대전광', '부산광',
        '서울특', '세종특', '울산광', '인천광',
        '전라남', '전라북', '제주특', '충청남', '충청북'
    )
    
    for area in area_list:
        print("[INFO] Start ApartTradeDetailLog Data Update")

        ApartTradeDetailLog = ApartData.Routine(area, 'Update')
        ApartTradeDetailLog.run()