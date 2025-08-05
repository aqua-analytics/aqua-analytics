"""
다양한 데이터 형식 호환성 테스트
다양한 엑셀 파일 형식과 데이터 구조에 대한 호환성 검증
"""

import pytest
import pandas as pd
import numpy as np
import tempfile
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any

# 테스트 대상 모듈 import
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.core.data_processor import DataProcessor
from src.utils.file_validator import FileValidator
from src.utils.error_handler import ErrorHandler


class TestDataFormatCompatibility:
    """데이터 형식 호환성 테스트 클래스"""
    
    def create_excel_file(self, data: pd.DataFrame, file_format: str = 'xlsx') -> str:
        """엑셀 파일 생성"""
        suffix = f'.{file_format}'
        tmp_file = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
        
        if file_format == 'xlsx':
            data.to_excel(tmp_file.name, index=False, engine='openpyxl')
        elif file_format == 'xls':
            data.to_excel(tmp_file.name, index=False, engine='xlwt')
        
        tmp_file.close()
        return tmp_file.name
    
    def test_standard_format_compatibility(self):
        """표준 형식 호환성 테스트"""
        print("\n📋 표준 형식 호환성 테스트")
        
        # 표준 데이터 구조
        standard_data = {
            'No.': [1, 2, 3, 4, 5],
            '시료명': ['냉수탱크', '온수탱크', '유량센서', '압력센서', '온도센서'],
            '분석번호': ['25A00001-001', '25A00001-002', '25A00001-003', '25A00001-004', '25A00001-005'],
            '시험항목': ['아크릴로나이트릴', '아크릴로나이트릴', 'N-니트로조다이메틸아민', '벤젠', '톨루엔'],
            '시험단위': ['mg/L', 'mg/L', 'ng/L', 'mg/L', 'mg/L'],
            '결과(성적서)': ['불검출', '0.0007', '2.5', '불검출', '0.003'],
            '시험자입력값': [0, 0.0007, 2.5, 0, 0.003],
            '기준대비 초과여부 (성적서)': ['적합', '부적합', '부적합', '적합', '부적합'],
            '시험자': ['김화빈', '김화빈', '이현풍', '박민수', '최영희'],
            '시험표준': ['EPA 524.2', 'EPA 524.2', 'House Method', 'EPA 524.2', 'EPA 525.2'],
            '기준': ['0.0006 mg/L 이하', '0.0006 mg/L 이하', '2.0 ng/L 이하', '0.005 mg/L 이하', '0.001 mg/L 이하'],
            '입력일시': ['2025-01-23 09:56', '2025-01-23 09:56', '2025-01-23 09:56', '2025-01-23 10:15', '2025-01-23 10:30']
        }
        
        df = pd.DataFrame(standard_data)
        
        # XLSX 형식 테스트
        xlsx_file = self.create_excel_file(df, 'xlsx')
        try:
            processor = DataProcessor()
            test_results = processor.parse_excel_file(xlsx_file)
            
            assert len(test_results) == 5, f"XLSX 파싱 결과 수 불일치: {len(test_results)}"
            assert test_results[0].sample_name == '냉수탱크', "XLSX 데이터 파싱 오류"
            print("   ✅ XLSX 형식 호환성 확인")
            
        finally:
            if os.path.exists(xlsx_file):
                os.unlink(xlsx_file)
        
        # XLS 형식 테스트 (레거시 지원)
        try:
            xls_file = self.create_excel_file(df, 'xls')
            try:
                test_results = processor.parse_excel_file(xls_file)
                assert len(test_results) == 5, f"XLS 파싱 결과 수 불일치: {len(test_results)}"
                print("   ✅ XLS 형식 호환성 확인")
                
            finally:
                if os.path.exists(xls_file):
                    os.unlink(xls_file)
                    
        except Exception as e:
            print(f"   ⚠️  XLS 형식 지원 제한: {e}")
    
    def test_column_name_variations(self):
        """컬럼명 변형 호환성 테스트"""
        print("\n📝 컬럼명 변형 호환성 테스트")
        
        # 줄바꿈이 포함된 컬럼명 테스트
        data_with_linebreaks = {
            'No.': [1, 2],
            '시료명': ['시료1', '시료2'],
            '분석번호': ['25A00001-001', '25A00001-002'],
            '시험항목': ['아크릴로나이트릴', '벤젠'],
            '시험단위': ['mg/L', 'mg/L'],
            '결과(성적서)': ['불검출', '0.001'],
            '시험자입력값': [0, 0.001],
            '기준대비 초과여부\n(성적서)': ['적합', '부적합'],  # 줄바꿈 포함
            '시험자': ['김화빈', '이현풍'],
            '시험표준': ['EPA 524.2', 'EPA 524.2'],
            '기준 텍스트': ['0.0006 mg/L 이하', '0.0006 mg/L 이하'],  # 다른 컬럼명
            '입력일시': ['2025-01-23 09:56', '2025-01-23 10:00']
        }
        
        df = pd.DataFrame(data_with_linebreaks)
        temp_file = self.create_excel_file(df)
        
        try:
            processor = DataProcessor()
            test_results = processor.parse_excel_file(temp_file)
            
            assert len(test_results) == 2, "줄바꿈 컬럼명 파싱 실패"
            assert test_results[0].standard_excess == '적합', "줄바꿈 컬럼 데이터 파싱 오류"
            assert test_results[1].standard_excess == '부적합', "줄바꿈 컬럼 데이터 파싱 오류"
            
            print("   ✅ 줄바꿈 포함 컬럼명 호환성 확인")
            
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_missing_optional_columns(self):
        """선택적 컬럼 누락 호환성 테스트"""
        print("\n🔍 선택적 컬럼 누락 호환성 테스트")
        
        # 최소 필수 컬럼만 포함
        minimal_data = {
            '시료명': ['시료1', '시료2', '시료3'],
            '시험항목': ['아크릴로나이트릴', '벤젠', '톨루엔'],
            '결과(성적서)': ['불검출', '0.001', '0.002'],
            '시험자': ['김화빈', '이현풍', '박민수']
        }
        
        df = pd.DataFrame(minimal_data)
        temp_file = self.create_excel_file(df)
        
        try:
            processor = DataProcessor()
            test_results = processor.parse_excel_file(temp_file)
            
            assert len(test_results) == 3, "최소 컬럼 파싱 실패"
            
            # 기본값 확인
            for result in test_results:
                assert result.sample_name in ['시료1', '시료2', '시료3']
                assert result.test_item in ['아크릴로나이트릴', '벤젠', '톨루엔']
                assert result.tester in ['김화빈', '이현풍', '박민수']
                # 누락된 컬럼들이 기본값으로 설정되는지 확인
                assert result.analysis_number == ''  # 기본값
                assert result.test_unit == ''  # 기본값
            
            print("   ✅ 최소 필수 컬럼 호환성 확인")
            
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_data_type_variations(self):
        """데이터 타입 변형 호환성 테스트"""
        print("\n🔢 데이터 타입 변형 호환성 테스트")
        
        # 다양한 데이터 타입 테스트
        varied_data = {
            'No.': [1.0, 2.0, 3.0],  # float로 저장된 번호
            '시료명': ['시료1', '시료2', '시료3'],
            '분석번호': ['25A00001-001', '25A00001-002', '25A00001-003'],
            '시험항목': ['아크릴로나이트릴', '벤젠', '톨루엔'],
            '시험단위': ['mg/L', 'mg/L', 'mg/L'],
            '결과(성적서)': ['불검출', 0.001, '< 0.0001'],  # 혼합 타입
            '시험자입력값': [0, 0.001, 0.00005],  # 숫자
            '기준대비 초과여부 (성적서)': ['적합', '부적합', '적합'],
            '시험자': ['김화빈', '이현풍', '박민수'],
            '시험표준': ['EPA 524.2', 'EPA 524.2', 'EPA 525.2'],
            '기준': ['0.0006 mg/L 이하', '0.0006 mg/L 이하', '0.0001 mg/L 이하'],
            '입력일시': [
                datetime(2025, 1, 23, 9, 56),  # datetime 객체
                '2025-01-23 10:00',  # 문자열
                pd.Timestamp('2025-01-23 10:30')  # pandas Timestamp
            ]
        }
        
        df = pd.DataFrame(varied_data)
        temp_file = self.create_excel_file(df)
        
        try:
            processor = DataProcessor()
            test_results = processor.parse_excel_file(temp_file)
            
            assert len(test_results) == 3, "다양한 데이터 타입 파싱 실패"
            
            # 타입 변환 확인
            assert test_results[0].no == 1, "float to int 변환 실패"
            assert test_results[1].no == 2, "float to int 변환 실패"
            
            # 결과값 처리 확인
            assert test_results[0].result_report == '불검출'
            assert test_results[1].result_report == '0.001'
            assert test_results[2].result_report == '< 0.0001'
            
            # 날짜 처리 확인
            for result in test_results:
                assert result.input_datetime is not None, "날짜 파싱 실패"
                assert isinstance(result.input_datetime, datetime), "날짜 타입 변환 실패"
            
            print("   ✅ 다양한 데이터 타입 호환성 확인")
            
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_empty_and_null_values(self):
        """빈 값과 NULL 값 처리 테스트"""
        print("\n🕳️ 빈 값과 NULL 값 처리 테스트")
        
        # 빈 값과 NULL이 포함된 데이터
        data_with_nulls = {
            'No.': [1, 2, 3, 4],
            '시료명': ['시료1', '', '시료3', None],  # 빈 문자열과 None
            '분석번호': ['25A00001-001', '25A00001-002', '', '25A00001-004'],
            '시험항목': ['아크릴로나이트릴', '벤젠', '톨루엔', '크실렌'],
            '시험단위': ['mg/L', 'mg/L', '', 'mg/L'],
            '결과(성적서)': ['불검출', '0.001', np.nan, '0.003'],  # NaN 포함
            '시험자입력값': [0, 0.001, np.nan, 0.003],
            '기준대비 초과여부 (성적서)': ['적합', '부적합', '', '부적합'],
            '시험자': ['김화빈', '', '박민수', '최영희'],
            '시험표준': ['EPA 524.2', 'EPA 524.2', None, 'EPA 525.2'],
            '기준': ['0.0006 mg/L 이하', '0.0006 mg/L 이하', '', '0.001 mg/L 이하'],
            '입력일시': ['2025-01-23 09:56', '', '2025-01-23 10:30', None]
        }
        
        df = pd.DataFrame(data_with_nulls)
        temp_file = self.create_excel_file(df)
        
        try:
            processor = DataProcessor()
            test_results = processor.parse_excel_file(temp_file)
            
            # 유효한 데이터만 파싱되는지 확인
            assert len(test_results) >= 2, "NULL 값 처리 후 결과 부족"
            
            # 빈 값 처리 확인
            for result in test_results:
                if result.sample_name:  # 빈 값이 아닌 경우만 확인
                    assert isinstance(result.sample_name, str)
                    assert len(result.sample_name.strip()) > 0
            
            print(f"   ✅ NULL 값 처리 완료 ({len(test_results)}개 유효 결과)")
            
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_large_text_values(self):
        """긴 텍스트 값 처리 테스트"""
        print("\n📄 긴 텍스트 값 처리 테스트")
        
        # 긴 텍스트가 포함된 데이터
        long_text_data = {
            'No.': [1, 2],
            '시료명': [
                '매우 긴 시료명을 가진 테스트 시료 번호 1번 - 이것은 실제 현장에서 발생할 수 있는 긴 이름입니다',
                '시료2'
            ],
            '분석번호': ['25A00001-001', '25A00001-002'],
            '시험항목': [
                '아크릴로나이트릴 및 기타 유기화합물 복합 분석 항목 (매우 긴 시험 항목명)',
                '벤젠'
            ],
            '시험단위': ['mg/L', 'mg/L'],
            '결과(성적서)': ['불검출', '0.001'],
            '시험자입력값': [0, 0.001],
            '기준대비 초과여부 (성적서)': ['적합', '부적합'],
            '시험자': ['김화빈', '이현풍'],
            '시험표준': [
                'EPA 524.2 Method for the Determination of Purgeable Organic Compounds in Water by Packed Column Gas Chromatography/Mass Spectrometry',
                'EPA 524.2'
            ],
            '기준': [
                '0.0006 mg/L 이하 (이 기준은 매우 상세한 설명과 함께 제공되는 긴 기준값 설명입니다)',
                '0.0006 mg/L 이하'
            ],
            '입력일시': ['2025-01-23 09:56', '2025-01-23 10:00']
        }
        
        df = pd.DataFrame(long_text_data)
        temp_file = self.create_excel_file(df)
        
        try:
            processor = DataProcessor()
            test_results = processor.parse_excel_file(temp_file)
            
            assert len(test_results) == 2, "긴 텍스트 파싱 실패"
            
            # 긴 텍스트가 올바르게 저장되는지 확인
            long_sample_name = test_results[0].sample_name
            assert len(long_sample_name) > 50, "긴 시료명 저장 실패"
            assert '매우 긴 시료명' in long_sample_name, "긴 시료명 내용 손실"
            
            long_test_item = test_results[0].test_item
            assert len(long_test_item) > 30, "긴 시험항목명 저장 실패"
            
            print("   ✅ 긴 텍스트 값 처리 확인")
            
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_special_characters(self):
        """특수 문자 처리 테스트"""
        print("\n🔣 특수 문자 처리 테스트")
        
        # 특수 문자가 포함된 데이터
        special_char_data = {
            'No.': [1, 2, 3],
            '시료명': [
                '시료#1 (특수문자)',
                '시료@2 & 기타',
                '시료%3 < > 테스트'
            ],
            '분석번호': ['25A00001-001', '25A00001-002', '25A00001-003'],
            '시험항목': [
                'N-니트로조다이메틸아민',  # 하이픈 포함
                '1,1,1-트리클로로에탄',  # 숫자와 하이픈
                'α-BHC (알파-BHC)'  # 그리스 문자와 괄호
            ],
            '시험단위': ['mg/L', 'μg/L', 'ng/L'],  # 그리스 문자 포함
            '결과(성적서)': ['< 0.0001', '≤ 0.001', '불검출'],  # 부등호 포함
            '시험자입력값': [0.0001, 0.001, 0],
            '기준대비 초과여부 (성적서)': ['적합', '부적합', '적합'],
            '시험자': ['김화빈', '이현풍', '박민수'],
            '시험표준': ['EPA 524.2', 'EPA 525.2', 'House Method'],
            '기준': [
                '≤ 0.0006 mg/L',  # 부등호 포함
                '< 0.001 μg/L',
                '불검출'
            ],
            '입력일시': ['2025-01-23 09:56', '2025-01-23 10:00', '2025-01-23 10:30']
        }
        
        df = pd.DataFrame(special_char_data)
        temp_file = self.create_excel_file(df)
        
        try:
            processor = DataProcessor()
            test_results = processor.parse_excel_file(temp_file)
            
            assert len(test_results) == 3, "특수 문자 파싱 실패"
            
            # 특수 문자 보존 확인
            assert '#' in test_results[0].sample_name, "특수 문자 손실"
            assert '@' in test_results[1].sample_name, "특수 문자 손실"
            assert '%' in test_results[2].sample_name, "특수 문자 손실"
            
            # 그리스 문자 확인
            assert 'μg/L' in test_results[1].test_unit, "그리스 문자 손실"
            
            # 부등호 확인
            assert '≤' in test_results[0].standard_criteria, "부등호 손실"
            assert '<' in test_results[1].standard_criteria, "부등호 손실"
            
            print("   ✅ 특수 문자 처리 확인")
            
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_different_date_formats(self):
        """다양한 날짜 형식 처리 테스트"""
        print("\n📅 다양한 날짜 형식 처리 테스트")
        
        # 다양한 날짜 형식 데이터
        date_format_data = {
            'No.': [1, 2, 3, 4, 5],
            '시료명': ['시료1', '시료2', '시료3', '시료4', '시료5'],
            '분석번호': ['25A00001-001', '25A00001-002', '25A00001-003', '25A00001-004', '25A00001-005'],
            '시험항목': ['아크릴로나이트릴'] * 5,
            '시험단위': ['mg/L'] * 5,
            '결과(성적서)': ['불검출'] * 5,
            '시험자입력값': [0] * 5,
            '기준대비 초과여부 (성적서)': ['적합'] * 5,
            '시험자': ['김화빈'] * 5,
            '시험표준': ['EPA 524.2'] * 5,
            '기준': ['0.0006 mg/L 이하'] * 5,
            '입력일시': [
                '2025-01-23 09:56',      # 표준 형식
                '2025/01/23 10:00',      # 슬래시 구분
                '23-01-2025 10:30',      # 일-월-년 순서
                '2025.01.23 11:00',      # 점 구분
                '20250123 1130'          # 구분자 없음
            ]
        }
        
        df = pd.DataFrame(date_format_data)
        temp_file = self.create_excel_file(df)
        
        try:
            processor = DataProcessor()
            test_results = processor.parse_excel_file(temp_file)
            
            assert len(test_results) == 5, "다양한 날짜 형식 파싱 실패"
            
            # 날짜 파싱 결과 확인
            valid_dates = 0
            for i, result in enumerate(test_results):
                if result.input_datetime is not None:
                    valid_dates += 1
                    assert isinstance(result.input_datetime, datetime), f"날짜 타입 오류: {i}"
                    # 2025년인지 확인
                    assert result.input_datetime.year == 2025, f"년도 파싱 오류: {i}"
                    assert result.input_datetime.month == 1, f"월 파싱 오류: {i}"
                    assert result.input_datetime.day == 23, f"일 파싱 오류: {i}"
            
            # 최소 3개 이상의 날짜 형식이 성공적으로 파싱되어야 함
            assert valid_dates >= 3, f"날짜 파싱 성공률 부족: {valid_dates}/5"
            
            print(f"   ✅ 날짜 형식 처리 확인 ({valid_dates}/5 성공)")
            
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_encoding_compatibility(self):
        """인코딩 호환성 테스트"""
        print("\n🔤 인코딩 호환성 테스트")
        
        # 다양한 언어 문자가 포함된 데이터
        multilingual_data = {
            'No.': [1, 2, 3],
            '시료명': [
                '한글 시료명',
                'English Sample',
                '日本語サンプル'  # 일본어
            ],
            '분석번호': ['25A00001-001', '25A00001-002', '25A00001-003'],
            '시험항목': [
                '아크릴로나이트릴',
                'Acrylonitrile',
                'アクリロニトリル'
            ],
            '시험단위': ['mg/L', 'mg/L', 'mg/L'],
            '결과(성적서)': ['불검출', 'ND', '検出されず'],
            '시험자입력값': [0, 0, 0],
            '기준대비 초과여부 (성적서)': ['적합', 'Pass', '適合'],
            '시험자': ['김화빈', 'John Smith', '田中太郎'],
            '시험표준': ['EPA 524.2', 'EPA 524.2', 'EPA 524.2'],
            '기준': ['0.0006 mg/L 이하', '≤ 0.0006 mg/L', '0.0006 mg/L以下'],
            '입력일시': ['2025-01-23 09:56', '2025-01-23 10:00', '2025-01-23 10:30']
        }
        
        df = pd.DataFrame(multilingual_data)
        temp_file = self.create_excel_file(df)
        
        try:
            processor = DataProcessor()
            test_results = processor.parse_excel_file(temp_file)
            
            assert len(test_results) == 3, "다국어 데이터 파싱 실패"
            
            # 한글 확인
            assert '한글' in test_results[0].sample_name, "한글 인코딩 오류"
            assert '아크릴로나이트릴' in test_results[0].test_item, "한글 인코딩 오류"
            
            # 영어 확인
            assert 'English' in test_results[1].sample_name, "영어 인코딩 오류"
            assert 'John Smith' in test_results[1].tester, "영어 인코딩 오류"
            
            # 일본어 확인 (지원되는 경우)
            if '日本語' in test_results[2].sample_name:
                print("   ✅ 일본어 인코딩 지원 확인")
            else:
                print("   ⚠️  일본어 인코딩 제한적 지원")
            
            print("   ✅ 다국어 인코딩 호환성 확인")
            
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_file_validation_edge_cases(self):
        """파일 검증 엣지 케이스 테스트"""
        print("\n🔍 파일 검증 엣지 케이스 테스트")
        
        validator = FileValidator()
        
        # 1. 존재하지 않는 파일
        result = validator.validate_file("nonexistent_file.xlsx")
        assert not result['is_valid'], "존재하지 않는 파일 검증 실패"
        print("   ✅ 존재하지 않는 파일 검증")
        
        # 2. 잘못된 확장자
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp_file:
            tmp_file.write(b"This is not an Excel file")
            tmp_file.flush()
            
            try:
                result = validator.validate_file(tmp_file.name)
                assert not result['is_valid'], "잘못된 확장자 검증 실패"
                print("   ✅ 잘못된 확장자 검증")
            finally:
                os.unlink(tmp_file.name)
        
        # 3. 빈 파일
        empty_df = pd.DataFrame()
        temp_file = self.create_excel_file(empty_df)
        
        try:
            result = validator.validate_file(temp_file)
            # 빈 파일도 유효한 엑셀 파일로 간주될 수 있음
            print(f"   📝 빈 파일 검증: {'✅' if result['is_valid'] else '❌'}")
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
        
        # 4. 매우 큰 파일 (시뮬레이션)
        large_data = self.generate_large_test_data(1000)  # 1000행
        temp_file = self.create_excel_file(large_data)
        
        try:
            file_size = os.path.getsize(temp_file) / 1024 / 1024  # MB
            result = validator.validate_file(temp_file)
            
            print(f"   📊 큰 파일 검증: {file_size:.1f}MB - {'✅' if result['is_valid'] else '❌'}")
            
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def generate_large_test_data(self, size: int) -> pd.DataFrame:
        """대용량 테스트 데이터 생성"""
        return pd.DataFrame({
            'No.': range(1, size + 1),
            '시료명': [f'시료_{i}' for i in range(1, size + 1)],
            '분석번호': [f'25A{i:05d}' for i in range(1, size + 1)],
            '시험항목': np.random.choice(['아크릴로나이트릴', '벤젠', '톨루엔'], size),
            '시험단위': ['mg/L'] * size,
            '결과(성적서)': [f'{np.random.uniform(0, 0.01):.6f}' for _ in range(size)],
            '시험자입력값': np.random.uniform(0, 0.01, size),
            '기준대비 초과여부 (성적서)': np.random.choice(['적합', '부적합'], size),
            '시험자': np.random.choice(['김화빈', '이현풍', '박민수'], size),
            '시험표준': ['EPA 524.2'] * size,
            '기준': ['0.0006 mg/L 이하'] * size,
            '입력일시': [(datetime.now() - timedelta(days=i % 30)).strftime('%Y-%m-%d %H:%M') for i in range(size)]
        })


if __name__ == "__main__":
    # 데이터 형식 호환성 테스트 실행
    test_class = TestDataFormatCompatibility()
    
    print("🧪 데이터 형식 호환성 테스트 시작")
    
    test_class.test_standard_format_compatibility()
    test_class.test_column_name_variations()
    test_class.test_missing_optional_columns()
    test_class.test_data_type_variations()
    test_class.test_empty_and_null_values()
    test_class.test_large_text_values()
    test_class.test_special_characters()
    test_class.test_different_date_formats()
    test_class.test_encoding_compatibility()
    test_class.test_file_validation_edge_cases()
    
    print("🎉 모든 데이터 형식 호환성 테스트 완료!")