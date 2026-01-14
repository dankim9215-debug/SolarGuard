import os
import requests
from openai import OpenAI

# 1. 환경 설정 및 API 키
UPSTAGE_API_KEY = "YOUR_UPSTAGE_API_KEY" # 실제 키로 교체하세요
client = OpenAI(api_key=UPSTAGE_API_KEY, base_url="https://api.upstage.ai/v1/solar")

def run_solarguard_agent(pdf_file_path, market_price, deposit_amount):
    """
    Step 1: Document Parse -> Step 2: Information Extract -> Step 3: Solar LLM 분석
    """
    
    # --- [Step 1: Document Parse] ---
    # 복잡한 등기부등본 PDF의 표 구조를 마크다운으로 변환
    print("Step 1: 문서 파싱 시작 (Document Parse API)...")
    parse_url = "https://api.upstage.ai/v1/document-ai/document-parse"
    headers = {"Authorization": f"Bearer {UPSTAGE_API_KEY}"}
    files = {"document": open(pdf_file_path, "rb")}
    
    parse_response = requests.post(parse_url, headers=headers, files=files)
    # 실제 API 호출 시 응답에서 텍스트 추출 (여기서는 데모용 변수 처리)
    parsed_markdown = parse_response.json().get("content", {}).get("text", "")
    print("✅ 문서 구조 추출 완료.")

    # --- [Step 2: Information Extract] ---
    # 파싱된 텍스트에서 '채권최고액(융자)'만 정확히 추출
    print("\nStep 2: 핵심 지표 추출 시작 (Information Extract via Solar)...")
    
    # Solar의 추출 능력을 활용하여 JSON 형태로 리턴받도록 구성
    extract_msg = [
        {"role": "system", "content": "너는 문서에서 숫자 데이터만 정확히 뽑아내는 추출 전문가야. 결과는 반드시 JSON 숫자로만 답해."},
        {"role": "user", "content": f"다음 등기부등본 마크다운 내용에서 '채권최고액'의 모든 합계를 찾아 숫자만 출력해줘: {parsed_markdown}"}
    ]
    
    extract_res = client.chat.completions.create(model="solar-1-mini-chat", messages=extract_msg)
    # 예: "250000000" 추출
    debt_total = int(extract_res.choices[0].message.content.replace(",", "").strip())
    print(f"✅ 선순위 채권 합계 추출 완료: {debt_total}원")

    # --- [Step 3: Solar LLM Risk Analysis] ---
    # 추출된 수치와 사용자의 전세금을 바탕으로 최종 리스크 판단
    print("\nStep 3: Solar LLM 종합 리스크 분석 및 솔루션 생성...")
    
    analysis_prompt = f"""
    당신은 부동산 전문 AI 에이전트 'SolarGuard'입니다. 
    제공된 데이터를 바탕으로 임차인을 위한 '전세 안심 보고서'를 작성하세요.

    [데이터 정보]
    - 매물 시세: {market_price}원
    - 임차 전세금: {deposit_amount}원
    - 등기부상 선순위 채권(융자): {debt_total}원
    - 원문 내용 요약: {parsed_markdown[:500]}... (생략)

    [보고서 필수 포함 항목]
    1. 위험 등급: (안전 / 주의 / 위험) 중 택1
    2. 부채 비율: (채권 + 전세금)이 시세의 몇 %인지 계산
    3. 상세 분석: 왜 위험한지 또는 왜 안전한지 설명 (한국 법령 기준)
    4. 추천 특약: 계약 시 반드시 넣어야 할 특약 문구 제안
    """

    final_res = client.chat.completions.create(
        model="solar-1-mini-chat",
        messages=[{"role": "user", "content": analysis_prompt}]
    )

    return final_res.choices[0].message.content

# --- [데모 실행 영역] ---
if __name__ == "__main__":
    # 테스트 데이터 (파일 경로, 시세, 본인 전세금)
    MY_PDF = "real_estate_sample.pdf"
    MARKET_PRICE = 500000000   # 5억
    MY_DEPOSIT = 350000000    # 3.5억
    
    # 결과 출력
    report = run_solarguard_agent(MY_PDF, MARKET_PRICE, MY_DEPOSIT)
    print("\n" + "="*50)
    print("🏠 SolarGuard 최종 분석 보고서")
    print("="*50)
    print(report)
