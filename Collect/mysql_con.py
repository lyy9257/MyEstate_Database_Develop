# MySQL Data Save
import configparser
import numpy as np
import pandas as pd
import pymysql
import random
import sys
import os

# 아파트 거래로그 저장
class ApartTradeLog():

    ## 초기화
    def __init__(self, area_name):

        ### set areaname
        self.area_name = area_name

        ### import config file
        self.prev_path = os.path.dirname(os.path.dirname(__file__))
        self.config = configparser.ConfigParser()
        self.config.read(self.prev_path + '\config.cfg', encoding = 'utf-8')

        ### Read config about database
        self.db_ip = self.config.get('MYSQL', 'DB_IP')
        self.db_port = self.config.get('MYSQL', 'DB_PORT')
        self.db_id = self.config.get('MYSQL', 'DB_ID')
        self.db_pw = self.config.get('MYSQL', 'DB_PW')

        ### Database, table name 설정 (사용자 입력)
        self.db_name = 'apart'
        self.table_name = 'temp'
        
        ### 저장할 데이터베이스 호출(pymysql)
        self.db_conn = pymysql.connect(
            host = self.db_ip,
            user = self.db_id,
            password = self.db_pw,
            db = self.db_name,
            charset = 'utf8'
        )

    ## DB 생성
    def create_db(self):
        ### 구문작성
        sql_syntax = 'CREATE DATABASE %s' %self.db_name       
        
        ### 커밋후 저장, 종료
        cur = self.db_conn.cursor()
        cur.execute(sql_syntax)
        self.db_conn.commit()

    ## 테이블 생성
    def create_tradelog_table(self):
        
        # 구문 작성
        sql_syntax = """
            CREATE TABLE tradelog_%s
            (   년 int, 월 int, 일 int, 건축년도 int,
                법정동시군구코드 varchar(8), 법정동읍면동코드 varchar(8), 법정동지번코드 varchar(8),
                법정동본번코드 varchar(8), 법정동부번코드 varchar(8), 아파트 varchar(255), 층 int,
                전용면적 float, 평수 int, 거래금액 int, 평당가 int, 해제여부 varchar(255),
                해제사유발생일 varchar(255), 도로명코드고유번호 varchar(512), 거래일련번호 varchar(1024) primary key
            );

            """ %self.area_name

        ### 커밋후 저장, 종료
        cur = self.db_conn.cursor()
        cur.execute(sql_syntax)
        self.db_conn.commit()

    ## 열별로 레코드 입력
    ## df.apply를 이용하여 작동
    def insert_bulk_record(self, table_header, record):
        
        ### 입력할 데이터 입력
        record_data_list = str(tuple(record.apply(lambda x: tuple(x.tolist()), axis=1)))[1:-1]
        
        ### 맨끝 반점 삭제
        if record_data_list[-1] == ',':
            record_data_list = record_data_list[:-1]

        ### 구문생성
        sql_syntax = 'INSERT IGNORE INTO %s.%s_%s values %s' %(
            self.db_name, table_header, self.area_name, record_data_list
        )

        ### 커밋후 저장, 종료
        cur = self.db_conn.cursor()
        cur.execute(sql_syntax)
        self.db_conn.commit()

        return True

    ## 아파트 거래로그 데이터 검색
    def search_tradelog_data(self, area_code):

        ### 구문생성
        sql_syntax = 'SELECT * FROM %s.tradelog_%s WHERE 법정동시군구코드 = %s' %(
            self.db_name, self.area_name, area_code
        )

        ### 쿼리 실행 
        cur = self.db_conn.cursor(pymysql.cursors.DictCursor)
        cur.execute(sql_syntax)
        
        result = pd.DataFrame(cur.fetchall())

        return result

    ## 총 데이터 입력
    def save(self, opt, data, code):

        ### 아파트리스트 데이터
        if opt == 'apartlist':
            try:
                self.create_apart_list_table()
            except:
                pass
            
            try:
                prev_apt_data = self.search_apart_list_data()
                data = pd.concat([prev_apt_data.astype(str), data.astype(str)]).drop_duplicates(keep=False)
            
            except:
                pass

        ### 거래로그
        elif opt == 'tradelog':
            try:
                self.create_tradelog_table()
            except:
                pass

            # prev_apt_data = self.search_tradelog_data(code)
            # data = pd.concat([prev_apt_data.astype(str), data.astype(str)]).drop_duplicates(keep=False)

        ### 잘못된 파라미터
        else:
            return False 

        if len(data.index) > 0:
            print("[INFO] %s Non-exist data len is %s" %(opt, len(data.index)))
            self.insert_bulk_record(opt, data)

        else:
            print("[INFO] Data Already Exists.")

        return True

# 아파트 리스트 생성
class ApartTradeList():
    
    ## 초기화
    def __init__(self, area_name):

        ### set areaname
        self.area_name = area_name

        ### import config file
        self.prev_path = os.path.dirname(os.path.dirname(__file__))
        self.config = configparser.ConfigParser()
        self.config.read(self.prev_path + '\config.cfg', encoding = 'utf-8')

        ### Read config about database
        self.db_ip = self.config.get('MYSQL', 'DB_IP')
        self.db_port = self.config.get('MYSQL', 'DB_PORT')
        self.db_id = self.config.get('MYSQL', 'DB_ID')
        self.db_pw = self.config.get('MYSQL', 'DB_PW')

        ### Database, table name 설정 (사용자 입력)
        self.db_name = 'apart'
        self.table_name = 'temp'
        
        ### 저장할 데이터베이스 호출(pymysql)
        self.db_conn = pymysql.connect(
            host = self.db_ip,
            user = self.db_id,
            password = self.db_pw,
            db = self.db_name,
            charset = 'utf8'
        )

    ## 아파트 별 고유 코드 생성
    ## 건축년도-법정동본번코드-법정동부번코드-법정동시군구코드-법정동읍면동코드
    def create_apart_code(self, row):
        head = str(row['건축년도'])
        mid1 = str(row['법정동시군구코드'])
        mid2 = str(row['법정동읍면동코드'])
        mid3 = str(row['법정동지번코드'])
        mid4 = str(row['법정동본번코드'])
        tail = str(row['법정동부번코드'])
        
        temp = [head, mid1, mid2, mid3, mid4, tail]
        code = str(''.join(temp))

        return code

    ## 아파트 리스트 쿼리
    def query_apartlist(self):
        
        ### 구문
        sql_syntax = """
            SELECT 건축년도, 법정동시군구코드, 법정동읍면동코드, 법정동지번코드, 법정동본번코드, 법정동부번코드, 아파트, 도로명코드고유번호
            FROM apart.tradelog_%s
            GROUP BY 건축년도, 법정동시군구코드, 법정동읍면동코드, 법정동지번코드, 법정동본번코드, 법정동부번코드, 아파트, 도로명코드고유번호
            HAVING COUNT(*) > 0
        """ %self.area_name

        ### 쿼리 실행 
        cur = self.db_conn.cursor(pymysql.cursors.DictCursor)
        cur.execute(sql_syntax)
        
        result = pd.DataFrame(cur.fetchall())
        result['ApartCode'] = result.apply(lambda row : self.create_apart_code(row), axis=1)

        return result
    
    ## 아파트리스트 테이블 생성
    def create_apart_list_table(self):

        # 구문 작성
        sql_syntax = """
            CREATE TABLE apartlist_%s
            (
                건축년도 int, 법정동시군구코드 varchar(16), 법정동읍면동코드 varchar(16),
                법정동지번코드 varchar(16), 법정동본번코드 varchar(16), 법정동부번코드 varchar(16),
                아파트 varchar(255), 도로명코드고유번호 varchar(512) Primary Key, 아파트코드 varchar(255)
            );
            """ %(self.area_name)

        ### 커밋후 저장, 종료
        cur = self.db_conn.cursor()
        cur.execute(sql_syntax)
        self.db_conn.commit()

    ## 열별로 레코드 입력
    ## df.apply를 이용하여 작동
    def insert_bulk_record(self, record):
        
        ### 입력할 데이터 입력
        record_data_list = str(tuple(record.apply(lambda x: tuple(x.tolist()), axis=1)))[1:-1]
        
        ### 맨끝 반점 삭제
        if record_data_list[-1] == ',':
            record_data_list = record_data_list[:-1]

        ### 구문생성
        sql_syntax = 'INSERT IGNORE INTO %s.apartlist_%s values %s' %(
            self.db_name, self.area_name, record_data_list
        )

        ### 커밋후 저장, 종료
        cur = self.db_conn.cursor()
        cur.execute(sql_syntax)
        self.db_conn.commit()

        return True

    ## 총 데이터 입력
    def save(self, data):

        ### 테이블이 존재하지 않으면 테이블 생성
        try:
            self.create_apart_list_table()
        except:
            pass
        
        ### 데이터 저장
        self.insert_bulk_record(data)

        return True

    ## 전체 루틴
    def routine(self):
        print('[INFO] Start Making Apart List')
        apart_list = self.query_apartlist()
        self.save(apart_list)

        return True

# 지역코드 데이터 저장
class Areacode():

    ## 초기화
    def __init__(self):

        ### import config file
        self.prev_path = os.path.dirname(os.path.dirname(__file__))
        self.config = configparser.ConfigParser()
        self.config.read(self.prev_path + '\config.cfg', encoding = 'utf-8')

        ### Read config about database
        self.db_ip = self.config.get('MYSQL', 'DB_IP')
        self.db_port = self.config.get('MYSQL', 'DB_PORT')
        self.db_id = self.config.get('MYSQL', 'DB_ID')
        self.db_pw = self.config.get('MYSQL', 'DB_PW')

        ### Database, table name 설정 (사용자 입력)
        self.db_name = 'areacode'
        self.table_name = 'temp'
        
        ### 저장할 데이터베이스 호출(pymysql)
        self.db_conn = pymysql.connect(
            host = self.db_ip,
            user = self.db_id,
            password = self.db_pw,
            db = self.db_name,
            charset = 'utf8'
        )

    ## DB 생성
    def create_db(self):
        ### 구문작성
        sql_syntax = 'CREATE DATABASE %s' %self.db_name       
        
        ### 커밋후 저장, 종료
        cur = self.db_conn.cursor()
        cur.execute(sql_syntax)
        self.db_conn.commit()

    ## 지역코드 저장용 테이블 생성
    def create_areacode_table(self):
        # 구문 작성
        sql_syntax = """
            CREATE TABLE areacode_list
            (
                code_raw varchar(10) PRIMARY KEY, code_head varchar(4), code_mid varchar(1),code_tail varchar(5),
                area_1st varchar(128), area_2nd varchar(128), area_3rd varchar(128), area_4th varchar(128), area_5th varchar(128)
            );
            """

        ### 커밋후 저장, 종료
        cur = self.db_conn.cursor()
        cur.execute(sql_syntax)
        self.db_conn.commit()

    ## 열별로 레코드 입력
    ## df.apply를 이용하여 작동
    def insert_bulk_record(self, record):
        
        ### 입력할 데이터 입력
        record_data_list = str(tuple(record.apply(lambda x: tuple(x.tolist()), axis=1)))[1:-1]
        
        ### 맨끝 반점 삭제
        if record_data_list[-1] == ',':
            record_data_list = record_data_list[:-1]

        ### 구문생성
        sql_syntax = 'INSERT IGNORE INTO %s.areacode_list values %s' %(
            self.db_name, record_data_list
        )

        ### 커밋후 저장, 종료
        cur = self.db_conn.cursor()
        cur.execute(sql_syntax)
        self.db_conn.commit()

        return True

    ## 데이터 저장
    def save(self, data):

        try:
            self.create_areacode_table()
        except:
            pass

        self.insert_bulk_record(data)

        return True

    ## 지역코드 데이터 검색
    def search_areacode_data(self, areaname):
        
        ### 구문 생성
        sql_syntax = """
            SELECT distinct(code_head) FROM %s.areacode_list
            WHERE area_1st LIKE "%s%%" and area_3rd != '-' and area_4th = '-'
        """ %(self.db_name, areaname)
        
        ### 쿼리 실행 
        cur = self.db_conn.cursor(pymysql.cursors.DictCursor)
        cur.execute(sql_syntax)
        
        result = pd.DataFrame(cur.fetchall())

        return result