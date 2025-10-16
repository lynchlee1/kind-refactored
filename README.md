# KIND 투자 조사 프로그램

CB, EB, BW에 대해 메자닌 투자시 고려할 수 있는 누적 전환액과 전환가액 변동내역을 자동으로 조사해서 EXCEL과 JSON으로 저장하는 프로그램입니다.

## 주요 기능

### 1. 추가상장 기록 조회 (hist)
- CB, EB, BW 관련 추가상장 기록을 자동 조사
- 회차별 추가주식수, 발행가격 정보 수집
- JSON 데이터베이스에 저장

### 2. 전환가액 변동 조회 (prc)
- 전환가액 조정 내역을 자동 조사
- 조정 전/후 전환가액 비교 데이터 수집
- JSON 데이터베이스에 저장

### 3. Excel 자동 생성
- 수집된 데이터를 Excel 파일로 자동 변환
- Holdings 시트와 연동하여 누적값 계산
- 전환가 변동내역을 포함한 종합 리포트 생성

### 4. 웹 인터페이스
- Flask 기반 웹 UI 제공
- 기업별/전체 기업 조사 옵션
- 날짜 범위 설정 가능
- 실시간 데이터베이스 조회

## 사용법

1. **프로그램 실행**
   ```bash
   python html_server.py
   ```

2. **웹 브라우저 접속**
   - 자동으로 브라우저가 열리거나 `http://localhost:5000` 접속

3. **조사 모드 선택**
   - 추가상장 기록 조회: CB/EB/BW 관련 추가상장 데이터 수집
   - 전환가액 변동 조회: 전환가액 조정 내역 수집

4. **결과 확인**
   - JSON: `resources/` 폴더의 `database_hist.json`, `database_prc.json`
   - Excel: `results.xlsx` 파일

## 출력 파일

- **database_hist.json**: 추가상장 기록 데이터
- **database_prc.json**: 전환가액 변동 데이터  
- **results.xlsx**: Excel 형태의 종합 리포트
- **results.json**: 최종 결과 데이터

## 기술 스택

- Python 3.x
- Selenium (웹 스크래핑)
- Flask (웹 서버)
- Pandas (데이터 처리)
- OpenPyXL (Excel 파일 생성)
