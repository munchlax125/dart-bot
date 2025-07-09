# dart_client.py
import requests
import xml.etree.ElementTree as ET
import zipfile
import io
import logging
from typing import Dict, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class DARTApiException(Exception):
    """DART API 관련 커스텀 예외"""
    pass

@dataclass
class CompanyInfo:
    corp_code: str
    corp_name: str
    stock_code: str

class DARTClient:
    """DART API 클라이언트"""
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("DART API 키가 필요합니다.")
        self.api_key = api_key
        self.base_url = "https://opendart.fss.or.kr/api"

    def _request_get(self, url: str, params: Dict) -> requests.Response:
        """GET 요청 래퍼"""
        try:
            response = requests.get(url, params=params, timeout=20)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            raise DARTApiException(f"DART API 네트워크 오류: {e}")

    def search_company(self, company_name: str) -> List[CompanyInfo]:
        """회사명으로 DART 기업 검색"""
        url = f"{self.base_url}/corpCode.xml"
        params = {'crtfc_key': self.api_key}
        response = self._request_get(url, params)
        
        content = self._extract_zip_content(response.content)
        xml_string = self._decode_content(content)
        root = ET.fromstring(xml_string)
        
        companies = []
        for corp in root.findall('.//list'):
            corp_name_el = corp.find('corp_name')
            if corp_name_el is not None and company_name.lower() in corp_name_el.text.lower():
                companies.append(CompanyInfo(
                    corp_code=corp.findtext('corp_code', ''),
                    corp_name=corp.findtext('corp_name', ''),
                    stock_code=corp.findtext('stock_code', '')
                ))
        return companies[:10]

    def get_financial_statements(self, corp_code: str, year: str) -> Dict:
        """재무제표 정보 조회 (연결 -> 개별 순차 조회)"""
        logger.info(f"재무제표 조회 시작: {corp_code}, {year}년")
        
        for fs_div in ['CFS', 'OFS']:  # 연결(CFS) 먼저, 없으면 개별(OFS)
            params = {
                'crtfc_key': self.api_key, 
                'corp_code': corp_code,
                'bsns_year': year, 
                'reprt_code': '11011',  # 사업보고서
                'fs_div': fs_div
            }
            
            try:
                response = self._request_get(f"{self.base_url}/fnlttSinglAcnt.json", params)
                result = response.json()
                
                if result.get('status') == '000' and result.get('list'):
                    logger.info(f"{year}년 재무제표 조회 성공 (구분: {fs_div})")
                    return result
                elif result.get('status') == '013':
                    logger.warning(f"{year}년 {fs_div} 재무제표 없음, 다른 구분 시도")
                    continue
                else:
                    logger.warning(f"DART API 응답 오류: {result.get('message', 'Unknown error')}")
                    
            except Exception as e:
                logger.error(f"재무제표 API 호출 오류: {e}")
                continue
        
        # 모든 시도 실패
        raise DARTApiException(f"{year}년도 재무제표 데이터를 찾을 수 없습니다.")

    def _extract_zip_content(self, content: bytes) -> bytes:
        """ZIP 파일 압축 해제"""
        try:
            if content.startswith(b'PK'):
                with zipfile.ZipFile(io.BytesIO(content)) as zf:
                    return zf.read(zf.namelist()[0])
            return content
        except Exception as e:
            logger.error(f"ZIP 압축 해제 오류: {e}")
            return content

    def _decode_content(self, content: bytes) -> str:
        """콘텐츠 인코딩 처리"""
        try:
            return content.decode('utf-8')
        except UnicodeDecodeError:
            try:
                return content.decode('euc-kr')
            except UnicodeDecodeError:
                logger.error("콘텐츠 디코딩 실패")
                return content.decode('utf-8', errors='ignore')