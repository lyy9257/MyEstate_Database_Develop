#-*- coding: utf-8 -*- 
import asyncio
import configparser
import pandas as pd
import pymysql

# Custom Lib
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from Collect import mysql_con

## 지역코드 저장
class Store():

    ## 초기화
    def __init__(self):
        self.db_con = mysql_con.Areacode()

    ## 기존 데이터 호출
    def import_rawdata(self):
        temp = pd.read_csv('https://goo.gl/tM6r3v', sep='\t', dtype={'법정동코드':str, '법정동명':str})

        return temp

    ## 데이터 전처리
    def refine(self, raw_data):
        temp = raw_data
        temp = temp[temp['폐지여부'] == '존재']
        temp = (temp[['법정동코드', '법정동명']])
        temp = temp[temp['법정동명'].str[-3:-1] != '특별시']
        temp = temp[temp['법정동명'].str[-3:-1] != '광역시']
        temp = temp[temp['법정동명'].str[-1] != '도']

        result = temp[temp['법정동명'].str[-1] != ')']

        return result
    
    ## 전처리한 데이터를 저장을 위해 변환
    ## apply 함수
    def change_save_format(self, row):
        code_list = [str(row['법정동코드']), str(row['법정동코드'][:4]), str(row['법정동코드'][4:5]), str(row['법정동코드'][5:])]
        area_list = list(row['법정동명'].split())
        
        ### 저장을 위해 리스트 합체
        result_list = code_list + area_list

        ### 없는 데이터는 '-' 로 채움
        result_list = result_list + ['-'] * (9 - len(result_list))
        
        return result_list

    ## 전체 루틴
    def routine(self): 

        ### 1. 데이터 호출 후 정제
        raw_data = self.import_rawdata()
        refined_data = self.refine(raw_data)
        
        ### 2. 저장용 데이터 포맷으로 변경
        formated_data = list()
        
        for r in refined_data.iterrows():
            row = r[1] # 튜플 형식으로 인덱스 - 데이터 순으로 나와서 인덱스는 날려야됨
            changed_data = self.change_save_format(row)
            formated_data.append(changed_data)

        ### 3. 최종 저장용 테이블 생성
        final_code_table = pd.DataFrame(
            formated_data, 
            columns = [
                'code_raw', 'code_head', 'code_mid', 'code_tail',
                'area_1st', 'area_2nd', 'area_3rd', 'area_4th', 'area_5th'
            ]
        )

        ### 4. 저장
        self.db_con.save(final_code_table)

        return True

# 실행
if __name__ == '__main__':
    Areacode = Store()
    Areacode.routine()

