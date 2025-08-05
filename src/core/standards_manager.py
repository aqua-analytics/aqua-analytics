"""
시험규격 관리 시스템
PDF 파일 업로드, 저장, 미리보기, 다운로드 기능
"""

import streamlit as st
import os
import base64
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

class StandardsManager:
    """시험규격 관리 클래스"""
    
    def __init__(self):
        self.standards_dir = Path("standards")
        self.standards_dir.mkdir(exist_ok=True)
        
        self.metadata_file = self.standards_dir / "standards_metadata.json"
        self.load_metadata()
    
    def load_metadata(self):
        """메타데이터 로드"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
            except:
                self.metadata = {}
        else:
            self.metadata = {}
    
    def save_metadata(self):
        """메타데이터 저장"""
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2, default=str)
    
    def upload_standard(self, uploaded_file, test_item: str, description: str = "") -> bool:
        """규격 파일 업로드"""
        try:
            # 파일 저장
            file_path = self.standards_dir / uploaded_file.name
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # 메타데이터 저장
            file_id = uploaded_file.name.replace('.pdf', '').replace(' ', '_')
            self.metadata[file_id] = {
                'filename': uploaded_file.name,
                'test_item': test_item,
                'description': description,
                'upload_time': datetime.now(),
                'file_size': len(uploaded_file.getbuffer()),
                'file_path': str(file_path)
            }
            
            self.save_metadata()
            return True
            
        except Exception as e:
            st.error(f"파일 업로드 실패: {e}")
            return False
    
    def get_standards_list(self) -> List[Dict]:
        """규격 목록 반환"""
        return list(self.metadata.values())
    
    def get_standard_by_test_item(self, test_item: str) -> Optional[Dict]:
        """시험항목으로 규격 검색"""
        for standard in self.metadata.values():
            if standard['test_item'].lower() in test_item.lower() or test_item.lower() in standard['test_item'].lower():
                return standard
        return None
    
    def get_pdf_base64(self, filename: str) -> Optional[str]:
        """PDF 파일을 base64로 인코딩"""
        try:
            file_path = self.standards_dir / filename
            if file_path.exists():
                with open(file_path, "rb") as f:
                    return base64.b64encode(f.read()).decode()
        except:
            pass
        return None
    
    def delete_standard(self, file_id: str) -> bool:
        """규격 삭제"""
        try:
            if file_id in self.metadata:
                # 파일 삭제
                file_path = Path(self.metadata[file_id]['file_path'])
                if file_path.exists():
                    file_path.unlink()
                
                # 메타데이터에서 제거
                del self.metadata[file_id]
                self.save_metadata()
                return True
        except:
            pass
        return False
    
    def render_pdf_viewer(self, filename: str, height: int = 600):
        """PDF 뷰어 렌더링"""
        pdf_base64 = self.get_pdf_base64(filename)
        if pdf_base64:
            pdf_display = f"""
            <iframe src="data:application/pdf;base64,{pdf_base64}" 
                    width="100%" height="{height}px" type="application/pdf">
                <p>PDF를 표시할 수 없습니다. <a href="data:application/pdf;base64,{pdf_base64}" download="{filename}">다운로드</a>하여 확인하세요.</p>
            </iframe>
            """
            st.markdown(pdf_display, unsafe_allow_html=True)
        else:
            st.error("PDF 파일을 불러올 수 없습니다.")
    
    def get_download_link(self, filename: str) -> Optional[str]:
        """다운로드 링크 생성"""
        pdf_base64 = self.get_pdf_base64(filename)
        if pdf_base64:
            return f"data:application/pdf;base64,{pdf_base64}"
        return None

# 전역 인스턴스
standards_manager = StandardsManager()