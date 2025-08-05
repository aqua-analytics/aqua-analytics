#!/usr/bin/env python3
"""
데이터베이스 관리자 - 분석 결과 영속성 관리
"""

import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import uuid

class DatabaseManager:
    """데이터베이스 관리 클래스"""
    
    def __init__(self, db_path: str = "data/analysis_database.json"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.ensure_database_exists()
    
    def ensure_database_exists(self):
        """데이터베이스 파일이 존재하지 않으면 생성"""
        if not self.db_path.exists():
            initial_data = {
                "files": {},
                "reports": {},
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "version": "1.0"
                }
            }
            self.save_database(initial_data)
    
    def load_database(self) -> Dict[str, Any]:
        """데이터베이스 로드"""
        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                "files": {},
                "reports": {},
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "version": "1.0"
                }
            }
    
    def save_database(self, data: Dict[str, Any]) -> bool:
        """데이터베이스 저장 (강화된 버전)"""
        try:
            # 백업 생성
            backup_path = self.db_path.with_suffix('.json.backup')
            if self.db_path.exists():
                import shutil
                shutil.copy2(self.db_path, backup_path)
            
            # 데이터 저장
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # 저장 검증
            try:
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    json.load(f)
                print("데이터베이스 저장 및 검증 완료")
                return True
            except json.JSONDecodeError:
                # 저장된 파일이 손상된 경우 백업에서 복원
                if backup_path.exists():
                    import shutil
                    shutil.copy2(backup_path, self.db_path)
                    print("데이터베이스 저장 실패 - 백업에서 복원됨")
                return False
                
        except Exception as e:
            print(f"데이터베이스 저장 오류: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def save_analysis_result(self, file_name: str, test_results: List, 
                           client: str = "미지정", project_name: str = None, upload_time: datetime = None) -> str:
        """분석 결과 저장"""
        db = self.load_database()
        
        file_id = str(uuid.uuid4())
        processed_at = (upload_time or datetime.now()).isoformat()
        
        # 분석 결과 요약 계산
        total_items = len(test_results)
        fail_items = len([r for r in test_results if r.is_non_conforming()])
        failure_rate = (fail_items / total_items * 100) if total_items > 0 else 0
        
        # 부적합 항목별 집계
        violation_by_item = {}
        for result in test_results:
            if result.is_non_conforming():
                item = result.test_item
                violation_by_item[item] = violation_by_item.get(item, 0) + 1
        
        # 시료별 집계
        samples = list(set(r.sample_name for r in test_results))
        violation_samples = list(set(r.sample_name for r in test_results if r.is_non_conforming()))
        
        # 보고서 파일명 생성
        date_str = (upload_time or datetime.now()).strftime('%Y%m%d')
        file_stem = file_name.replace('.xlsx', '').replace('.xls', '')
        report_filename = f"{date_str}_{file_stem}_분석결과.html"
        
        file_record = {
            "file_id": file_id,
            "file_name": file_name,
            "project_name": project_name or file_stem,
            "client": client,
            "processed_at": processed_at,
            "report_path": f"dashboard_reports/{report_filename}",
            "summary": {
                "total_items": total_items,
                "fail_items": fail_items,
                "failure_rate": round(failure_rate, 2),
                "total_samples": len(samples),
                "violation_samples": len(violation_samples),
                "violation_by_item": violation_by_item,
                "top_violation_item": max(violation_by_item.items(), key=lambda x: x[1])[0] if violation_by_item else None
            },
            "test_results": [self._serialize_test_result(r) for r in test_results]
        }
        
        db["files"][file_id] = file_record
        self.save_database(db)
        
        return file_id
    
    def _serialize_test_result(self, test_result) -> Dict[str, Any]:
        """TestResult 객체를 직렬화"""
        # 이미 딕셔너리인 경우 그대로 반환 (중복 직렬화 방지)
        if isinstance(test_result, dict):
            return test_result
        
        # TestResult 객체인 경우 직렬화
        try:
            return {
                "no": getattr(test_result, 'no', 0),
                "sample_name": getattr(test_result, 'sample_name', ''),
                "analysis_number": getattr(test_result, 'analysis_number', ''),
                "test_item": getattr(test_result, 'test_item', ''),
                "test_unit": getattr(test_result, 'test_unit', ''),
                "result_report": getattr(test_result, 'result_report', ''),
                "tester_input_value": getattr(test_result, 'tester_input_value', 0),
                "standard_excess": getattr(test_result, 'standard_excess', '적합'),
                "tester": getattr(test_result, 'tester', ''),
                "test_standard": getattr(test_result, 'test_standard', ''),
                "standard_criteria": getattr(test_result, 'standard_criteria', ''),
                "text_digits": getattr(test_result, 'text_digits', ''),
                "processing_method": getattr(test_result, 'processing_method', ''),
                "result_display_digits": getattr(test_result, 'result_display_digits', 0),
                "result_type": getattr(test_result, 'result_type', ''),
                "tester_group": getattr(test_result, 'tester_group', ''),
                "input_datetime": test_result.input_datetime.isoformat() if hasattr(test_result, 'input_datetime') and test_result.input_datetime else datetime.now().isoformat(),
                "approval_request": getattr(test_result, 'approval_request', ''),
                "test_result_display_limit": getattr(test_result, 'test_result_display_limit', 0),
                "quantitative_limit_processing": getattr(test_result, 'quantitative_limit_processing', ''),
                "test_equipment": getattr(test_result, 'test_equipment', ''),
                "judgment_status": getattr(test_result, 'judgment_status', ''),
                "report_output": getattr(test_result, 'report_output', ''),
                "kolas_status": getattr(test_result, 'kolas_status', ''),
                "test_lab_group": getattr(test_result, 'test_lab_group', ''),
                "test_set": getattr(test_result, 'test_set', ''),
                "is_non_conforming": test_result.is_non_conforming() if hasattr(test_result, 'is_non_conforming') else False
            }
        except Exception as e:
            # 직렬화 실패 시 기본 딕셔너리 반환
            return {
                "no": 0,
                "sample_name": str(test_result) if test_result else "",
                "analysis_number": "",
                "test_item": "",
                "test_unit": "",
                "result_report": "",
                "tester_input_value": 0,
                "standard_excess": "적합",
                "tester": "",
                "test_standard": "",
                "standard_criteria": "",
                "text_digits": "",
                "processing_method": "",
                "result_display_digits": 0,
                "result_type": "",
                "tester_group": "",
                "input_datetime": datetime.now().isoformat(),
                "approval_request": "",
                "test_result_display_limit": 0,
                "quantitative_limit_processing": "",
                "test_equipment": "",
                "judgment_status": "",
                "report_output": "",
                "kolas_status": "",
                "test_lab_group": "",
                "test_set": "",
                "is_non_conforming": False
            }
    
    def get_files_by_period(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """기간별 파일 조회"""
        db = self.load_database()
        filtered_files = []
        
        for file_record in db["files"].values():
            processed_at = datetime.fromisoformat(file_record["processed_at"])
            if start_date <= processed_at <= end_date:
                filtered_files.append(file_record)
        
        return sorted(filtered_files, key=lambda x: x["processed_at"], reverse=True)
    
    def get_all_files(self) -> List[Dict[str, Any]]:
        """모든 파일 조회"""
        try:
            db = self.load_database()
            files = list(db.get("files", {}).values())
            # 최신 순으로 정렬
            return sorted(files, key=lambda x: x.get('processed_at', ''), reverse=True)
        except Exception as e:
            print(f"파일 조회 오류: {e}")
            return []
    
    def get_file_by_id(self, file_id: str) -> Optional[Dict[str, Any]]:
        """파일 ID로 조회"""
        db = self.load_database()
        return db["files"].get(file_id)
    
    def delete_file(self, file_id: str) -> bool:
        """파일 삭제"""
        db = self.load_database()
        if file_id in db["files"]:
            del db["files"][file_id]
            self.save_database(db)
            return True
        return False
    
    def get_storage_folder_path(self) -> str:
        """저장 폴더 경로 반환"""
        return str(self.db_path.parent.absolute())
    
    def get_integrated_analysis_data(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """통합 분석용 데이터 조회"""
        files = self.get_files_by_period(start_date, end_date)
        
        if not files:
            return {
                "total_files": 0,
                "total_tests": 0,
                "total_violations": 0,
                "violation_rate": 0,
                "top_clients": [],
                "top_violation_items": [],
                "conforming_items": {},
                "non_conforming_items": {},
                "monthly_stats": {},
                "summary_text": "선택된 기간에 분석된 데이터가 없습니다."
            }
        
        # 집계 데이터 계산 (안전한 처리)
        total_files = len(files)
        total_tests = 0
        total_violations = 0
        
        for f in files:
            try:
                if isinstance(f, dict) and "summary" in f:
                    summary = f["summary"]
                    if isinstance(summary, dict):
                        total_tests += summary.get("total_items", 0)
                        total_violations += summary.get("fail_items", 0)
            except Exception:
                continue
                
        violation_rate = (total_violations / total_tests * 100) if total_tests > 0 else 0
        
        # 의뢰 기관별 집계 (안전한 처리)
        client_stats = {}
        for file_record in files:
            try:
                if isinstance(file_record, dict):
                    client = file_record.get("client", "미지정")
                    if client:
                        client_stats[client] = client_stats.get(client, 0) + 1
            except Exception:
                continue
        
        top_clients = sorted(client_stats.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # 부적합 항목별 집계
        violation_items = {}
        conforming_items = {}
        
        for file_record in files:
            # test_results가 리스트인지 확인
            test_results = file_record.get("test_results", [])
            if not isinstance(test_results, list):
                continue
                
            for result in test_results:
                # result가 딕셔너리인지 확인
                if not isinstance(result, dict):
                    continue
                    
                item = result.get("test_item", "")
                if not item:
                    continue
                    
                # is_non_conforming 값 안전하게 확인
                is_non_conforming = result.get("is_non_conforming", False)
                if isinstance(is_non_conforming, str):
                    is_non_conforming = is_non_conforming.lower() in ['true', '1', 'yes']
                
                if is_non_conforming:
                    violation_items[item] = violation_items.get(item, 0) + 1
                else:
                    conforming_items[item] = conforming_items.get(item, 0) + 1
        
        top_violation_items = sorted(violation_items.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # 월별 통계
        monthly_stats = {}
        for file_record in files:
            processed_date = datetime.fromisoformat(file_record["processed_at"])
            month_key = processed_date.strftime("%Y-%m")
            
            if month_key not in monthly_stats:
                monthly_stats[month_key] = {
                    "files": 0,
                    "tests": 0,
                    "violations": 0
                }
            
            monthly_stats[month_key]["files"] += 1
            monthly_stats[month_key]["tests"] += file_record["summary"]["total_items"]
            monthly_stats[month_key]["violations"] += file_record["summary"]["fail_items"]
        
        # 요약 텍스트 생성
        summary_text = self._generate_summary_text(
            start_date, end_date, total_files, total_tests, 
            total_violations, violation_rate, top_clients, top_violation_items
        )
        
        return {
            "total_files": total_files,
            "total_tests": total_tests,
            "total_violations": total_violations,
            "violation_rate": round(violation_rate, 1),
            "top_clients": top_clients,
            "top_violation_items": top_violation_items,
            "conforming_items": conforming_items,
            "non_conforming_items": violation_items,
            "monthly_stats": monthly_stats,
            "summary_text": summary_text,
            "files": files
        }
    
    def _generate_summary_text(self, start_date: datetime, end_date: datetime,
                             total_files: int, total_tests: int, total_violations: int,
                             violation_rate: float, top_clients: List, top_violation_items: List) -> str:
        """요약 텍스트 생성"""
        period_str = f"{start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}"
        
        summary_parts = [
            f"선택된 기간({period_str}) 동안 총 {total_files}건의 시험이 분석되었습니다.",
            f"전체 {total_tests}개 항목 중 {total_violations}개 항목이 부적합으로 판정되어 {violation_rate:.1f}%의 부적합률을 보였습니다."
        ]
        
        if top_clients:
            top_client = top_clients[0][0]
            summary_parts.append(f"주요 의뢰 기관은 '{top_client}'이며, 총 {top_clients[0][1]}건의 시험을 의뢰했습니다.")
        
        if top_violation_items:
            top_item = top_violation_items[0][0]
            top_count = top_violation_items[0][1]
            summary_parts.append(f"가장 빈번한 부적합 항목은 '{top_item}'으로 {top_count}건이 발생했습니다.")
        
        if violation_rate > 20:
            summary_parts.append("부적합률이 20%를 초과하여 품질 관리 강화가 필요합니다.")
        elif violation_rate < 5:
            summary_parts.append("우수한 품질 수준을 유지하고 있습니다.")
        
        return " ".join(summary_parts)
    
    def get_client_statistics(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """기간별 의뢰 기관 통계"""
        files = self.get_files_by_period(start_date, end_date)
        
        client_stats = {}
        for file_record in files:
            client = file_record["client"]
            if client not in client_stats:
                client_stats[client] = {
                    "client": client,
                    "file_count": 0,
                    "total_tests": 0,
                    "total_violations": 0
                }
            
            client_stats[client]["file_count"] += 1
            client_stats[client]["total_tests"] += file_record["summary"]["total_items"]
            client_stats[client]["total_violations"] += file_record["summary"]["fail_items"]
        
        # 파일 수 기준으로 정렬
        return sorted(client_stats.values(), key=lambda x: x["file_count"], reverse=True)
    
    def delete_analysis_result(self, file_id: str) -> bool:
        """분석 결과 삭제 (강화된 버전)"""
        try:
            # 데이터베이스 로드
            db = self.load_database()
            
            # 파일 ID가 존재하는지 확인
            if file_id not in db["files"]:
                print(f"파일 ID {file_id}가 데이터베이스에 존재하지 않습니다.")
                return False
            
            # 삭제 전 백업 (선택적)
            deleted_file = db["files"][file_id].copy()
            
            # 파일 삭제
            del db["files"][file_id]
            
            # 데이터베이스 저장
            success = self.save_database(db)
            
            if success:
                print(f"파일 ID {file_id} 삭제 완료")
                return True
            else:
                # 삭제 실패 시 복원
                db["files"][file_id] = deleted_file
                print(f"파일 ID {file_id} 삭제 실패 - 데이터 복원됨")
                return False
                
        except Exception as e:
            print(f"데이터베이스 삭제 오류: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_file_by_id(self, file_id: str) -> Optional[Dict[str, Any]]:
        """파일 ID로 분석 결과 조회"""
        try:
            db = self.load_database()
            return db["files"].get(file_id)
        except Exception:
            return None

# 전역 인스턴스
db_manager = DatabaseManager()