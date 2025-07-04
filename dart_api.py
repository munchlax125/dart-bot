"""
DART API 전용 모듈
- 기업 검색
- 재무제표 조회
- XML/JSON 파싱
"""

import requests
import xml.etree.ElementTree as ET
import zipfile
import io
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class CompanyInfo:
    corp_code: str
    corp_name: str
    stock_code: str


class DARTClient:
    """DART API 클라이언트"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://opendart.fss.or.kr/api"
        
    def search_company(self, company_name: str) -> List[CompanyInfo]:
        """회사명으로 DART 기업 검색"""
        url = f"{self.base_url}/corpCode.xml"
        params = {'crtfc_key': self.api_key}
        
        try:
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code != 200:
                raise Exception(f"DART API 호출 실패: {response.status_code}")
            
            # ZIP 파일 처리
            content = self._extract_zip_content(response.content)
            
            # XML 파싱
            xml_string = self._decode_content(content)
            root = ET.fromstring(xml_string)
            
            # 회사 검색
            return self._parse_company_list(root, company_name)
            
        except Exception as e:
            raise Exception(f"기업 검색 실패: {str(e)}")
    
    def get_financial_statements(self, corp_code: str, year: str = "2023") -> Dict:
        """재무제표 정보 조회"""
        url = f"{self.base_url}/fnlttSinglAcnt.json"
        
        # 연결재무제표 시도
        params = {
            'crtfc_key': self.api_key,
            'corp_code': corp_code,
            'bsns_year': year,
            'reprt_code': '11011',
            'fs_div': 'CFS'  # 연결재무제표
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code != 200:
                raise Exception(f"재무제표 조회 실패: {response.status_code}")
            
            result = response.json()
            
            # 연결재무제표가 없으면 개별재무제표 시도
            if result.get('status') == '013':
                params['fs_div'] = 'OFS'  # 개별재무제표
                response = requests.get(url, params=params, timeout=30)
                result = response.json()
                
                if result.get('status') != '000':
                    raise Exception("재무제표 데이터를 찾을 수 없습니다.")
                    
            elif result.get('status') != '000':
                raise Exception(f"API 오류: {result.get('message', '알 수 없는 오류')}")
                
            return result
            
        except Exception as e:
            raise Exception(f"재무제표 조회 실패: {str(e)}")
    
    def get_business_report_list(self, corp_code: str, year: str = "2023") -> Dict:
        """사업보고서 목록 조회"""
        url = f"{self.base_url}/list.json"
        params = {
            'crtfc_key': self.api_key,
            'corp_code': corp_code,
            'bgn_de': f"{year}0101",
            'end_de': f"{year}1231",
            'pblntf_ty': 'A',  # 정기공시
            'pblntf_detail_ty': 'A001',  # 사업보고서
            'page_no': 1,
            'page_count': 10
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code != 200:
                raise Exception(f"사업보고서 조회 실패: {response.status_code}")
            
            result = response.json()
            
            if result.get('status') == '013':
                raise Exception("검색된 데이터가 없습니다.")
            elif result.get('status') != '000':
                raise Exception(f"API 오류: {result.get('message', '알 수 없는 오류')}")
                
            return result
            
        except Exception as e:
            raise Exception(f"사업보고서 조회 실패: {str(e)}")
    
    def validate_api_key(self) -> bool:
        """API 키 유효성 검사"""
        try:
            url = f"{self.base_url}/corpCode.xml"
            params = {'crtfc_key': self.api_key}
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                return True
            elif response.status_code == 401:
                return False
            else:
                return False
                
        except Exception:
            return False
    
    def _extract_zip_content(self, content: bytes) -> bytes:
        """ZIP 파일 압축 해제"""
        if content.startswith(b'PK'):
            with zipfile.ZipFile(io.BytesIO(content)) as zip_file:
                file_list = zip_file.namelist()
                if file_list:
                    return zip_file.read(file_list[0])
        return content
    
    def _decode_content(self, content: bytes) -> str:
        """콘텐츠 인코딩 처리"""
        try:
            if isinstance(content, bytes):
                xml_string = content.decode('utf-8')
            else:
                xml_string = content
            
            # BOM 제거
            if xml_string.startswith('\ufeff'):
                xml_string = xml_string[1:]
            
            return xml_string
            
        except UnicodeDecodeError:
            # UTF-8 실패 시 EUC-KR 시도
            return content.decode('euc-kr')
    
    def _parse_company_list(self, root: ET.Element, company_name: str) -> List[CompanyInfo]:
        """XML에서 회사 목록 파싱"""
        companies = []
        
        for corp in root.findall('.//list'):
            corp_name = corp.find('corp_name')
            corp_code = corp.find('corp_code')
            stock_code = corp.find('stock_code')
            
            if corp_name is not None and corp_code is not None:
                corp_name_text = corp_name.text if corp_name.text else ""
                if company_name.lower() in corp_name_text.lower():
                    companies.append(CompanyInfo(
                        corp_code=corp_code.text,
                        corp_name=corp_name_text,
                        stock_code=stock_code.text if stock_code is not None and stock_code.text else ""
                    ))
                    
        return companies[:10]  # 최대 10개 결과 반환
