'''
아파트 실거래 상세로그 호출
'''

#-*- coding: utf-8 -*- 
import asyncio
import pandas as pd
import pymysql
from sqlalchemy import create_engine
from datetime import datetime
import requests
import xmltodict
import json
import gc

import configparser

# Custom Lib
# 설정 호출 
import os
import sys

from Collect import Areacode, mysql_con

# 아파트 거래내역 데이터 크롤링 
class Routine():

    ## 초기화
    def __init__(self, area, opt):

        ### get prev path 
        self.prev_path = os.path.abspath(os.path.join(os.path.dirname(__file__),".."))

        ### API 접근 필요 데이터
        self.access_key = open("api_key/ApartDetailTradeLog.txt", 'rt').read()
        self.root_url = 'http://openapi.molit.go.kr/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptTradeDev'

        ### 공통사용 데이터 호출
        self.area = area
        self.mysql_con = mysql_con.ApartTradeLog(area)
        self.mysql_con_areacode = mysql_con.Areacode()
        self.mysql_con_apartlist = mysql_con.ApartTradeList(area)

        today = datetime.today().strftime("%Y-%m-%d")    
        
        self.timeframe_list = pd.date_range('2010-01-01', str(today), freq='MS').strftime("%Y%m").tolist()

        ### 처음 구축할 경우 05년부터
        if opt == 'First':
            self.timeframe_list = self.timeframe_list[::-1]
        ### 업데이트 일 경우 2달치만
        elif opt == 'Update':
            self.timeframe_list = self.timeframe_list[-2:]

    ## 지역코드 데이터 호출
    def query_areacode(self, areaname):
        raw_data = self.mysql_con_areacode.search_areacode_data(areaname)
        result = raw_data['code_head']

        return result

    ## 데이터 크롤링
    def call_data(self, areacode, tradeyear):
        
        ### 파라미터 설정
        ### 참고 : https://somjang.tistory.com/entry/SERVICE-KEY-IS-NOT-REGISTERED-ERROR
        parameters = {
            "ServiceKey" : requests.utils.unquote(self.access_key),
            "pageNo" : 1,
            "numOfRows" : 99999,
            "LAWD_CD" : areacode,
            "DEAL_YMD" : tradeyear
        }

        ## convert XML to DataFrame
        ## Process : XML(Raw) > Dict > JSON > DataFrame
        content = requests.get(self.root_url, params = parameters).content
        dict = xmltodict.parse(content)

        try:
            jsonString = json.dumps(dict['response']['body'], ensure_ascii=False)
            jsonObj = json.loads(jsonString)

            df = pd.read_json(json.dumps(jsonObj['items']['item']))

            return df
            ## self.tradelog = pd.concat([self.tradelog, df], sort=True)

        except:
            ## 행정구가 있는 케이스는 예외처리로 패스시킴
            print("[%s] None Data!" %areacode)

        return 0  

    ## 전처리
    def refine(self, rawdata):

        ### 없앨 컬럼 리스트
        drop_column_list = ['도로명', '지역코드', '지번']
        
        refined_data = rawdata.drop(columns=drop_column_list)      
        
        ### 평수, 평당금액 생성
        refined_data['평수'] = (refined_data['전용면적'].astype(float)/3.3).round(0).astype(int)
        refined_data['거래금액'] = refined_data['거래금액'].apply(lambda x: x.replace(',',''))
        refined_data['평당가'] = (refined_data['거래금액'].astype(int)/refined_data['평수']).round(0).map(int)  

        ### 도로명코드 고유번호 생성
        ### 도로명시군구코드 - 도로명코드 - 도로명건물본번호코드 - 도로명건물부번호코드
        ### 이 코드를 기반으로 좌표 매칭
        refined_data['도로명코드고유번호'] = refined_data['도로명시군구코드'].astype(str) + \
            refined_data['도로명코드'].astype(str) + refined_data['도로명건물본번호코드'].astype(str) + \
            refined_data['도로명건물부번호코드'].astype(str)
        
        ### 필요없는 데이터 제거
        try:
            refined_data = refined_data.drop(
                columns = [
                    '도로명시군구코드', '도로명코드', '도로명건물본번호코드',
                    '도로명건물부번호코드', '도로명지상지하코드', '도로명일련번호코드', '법정동'
                ]
            )    
            
        except:
            refined_data = refined_data.drop(
                columns = [
                    '도로명시군구코드', '도로명코드', '도로명건물본번호코드',
                    '도로명건물부번호코드', '도로명일련번호코드', '법정동'
                ]
            )  

        ### 데이터 재정렬
        refined_data = refined_data[
            [
                '년', '월', '일', '건축년도', '법정동시군구코드',
                '법정동읍면동코드', '법정동지번코드', '법정동본번코드', '법정동부번코드', 
                '아파트', '층', '전용면적', '평수', '거래금액', '평당가', 
                '해제여부', '해제사유발생일', '도로명코드고유번호'
            ]
        ]

        ### 빈 자리 x로 채움
        for c in refined_data.columns:
            refined_data[c] = refined_data[c].apply(lambda x: 'X' if x == None else x)
        refined_data = refined_data.fillna('X')

        ### 거래일련번호 추가
        refined_data['거래일련번호'] = refined_data[
            [
                '년', '월', '일', '건축년도', '법정동시군구코드',
                '법정동읍면동코드', '법정동지번코드', '법정동본번코드',
                '법정동부번코드', '층', '평수', '거래금액', '해제여부'
            ]
        ].astype(str).agg(''.join, axis=1)

        ### 저장되는 데이터 확인
        print(refined_data)

        return refined_data

    ## 거래로그 저장
    def save_tradelog(self, data, code):
        print('[INFO] tradelog data length is %s' %len(data.index))
        self.mysql_con.save('tradelog', data, code)

        return True

    ## run
    def run(self):

        ### crawling from data.go.kr
        areacode_list = self.query_areacode(self.area).tolist()
        
        ### 지역별 -> 시간별 순으로 돌아가며 데이터 저장
        for code in areacode_list:
            for time in self.timeframe_list: 

                ### 데이터 호출(data.go.kr에서)
                result = self.call_data(code, time)

                ### 데이터가 있으면
                if type(result) == pd.DataFrame:

                    ### 전처리 
                    refine_result = self.refine(result)

                    ### 전처리 후 데이터 저장
                    if type(refine_result) == pd.DataFrame:
                        
                        ### 취소사유가 없는 칸은 X로 메워 저장
                        tradelog_list = refine_result.where(pd.notnull(refine_result), 'X')
                        
                        ### 데이터 적재
                        self.save_tradelog(tradelog_list, code)

                else:
                    pass

        self.mysql_con_apartlist.routine()

        return True
