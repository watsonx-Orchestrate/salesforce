import json
from datetime import datetime, timedelta

import requests

# FastAPI 서버 URL
BASE_URL = "https://salesforce-custom.1wpveihz0wfq.us-south.codeengine.appdomain.cloud"


def test_get_pricebooks():
    """가격 책자 조회 테스트"""
    print("=== 가격 책자 조회 테스트 ===")
    try:
        response = requests.get(f"{BASE_URL}/pricebooks")
        if response.status_code == 200:
            data = response.json()
            print("✅ 성공!")
            print(f"응답 데이터: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 실패: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ 에러: {e}")
    print()


def test_get_all_orders():
    """모든 주문 조회 테스트"""
    print("=== 모든 주문 조회 테스트 ===")
    try:
        response = requests.get(f"{BASE_URL}/get_all_orders")
        if response.status_code == 200:
            data = response.json()
            print("✅ 성공!")
            print(f"응답 데이터: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 실패: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ 에러: {e}")
    print()


def test_create_order():
    """주문 생성 테스트"""
    print("=== 주문 생성 테스트 ===")
    try:
        # 테스트용 파라미터 (실제 Salesforce 데이터에 맞게 수정 필요)
        params = {
            "account_id": "001IU00002pmnF0YAI",  # 실제 Account ID로 변경 필요
            "date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
            "Pricebook2Id": "01sIU000009VjkSYAS",  # 실제 Pricebook2 ID로 변경 필요
            "name": "Test Company",  # 실제 회사명으로 변경 필요
            "status": "Draft",
        }

        response = requests.get(f"{BASE_URL}/create_orders", params=params)
        if response.status_code == 200:
            data = response.json()
            print("✅ 성공!")
            print(f"생성된 주문 ID: {data.get('order_id')}")
            return data.get("order_id")
        else:
            print(f"❌ 실패: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ 에러: {e}")
        return None
    print()


def test_create_order_item(order_id=None):
    """주문 아이템 생성 테스트"""
    print("=== 주문 아이템 생성 테스트 ===")
    if not order_id:
        print("⚠️ 주문 ID가 없어서 테스트를 건너뜁니다.")
        return

    try:
        # 테스트용 파라미터 (실제 데이터에 맞게 수정 필요)
        params = {
            "order": order_id,
            "pricebook_id": "01sIU000009VjkSYAS",  # 실제 Pricebook2 ID로 변경 필요
            "pricebook_name": "Standard Price Book",  # 실제 가격 책자명으로 변경 필요
            "quantity": 5,
        }

        response = requests.post(f"{BASE_URL}/create_order_item/", params=params)
        if response.status_code == 200:
            data = response.json()
            print("✅ 성공!")
            print(f"응답 데이터: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 실패: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ 에러: {e}")
    print()


def check_server_status():
    """서버 상태 확인"""
    print("=== 서버 상태 확인 ===")
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print("✅ FastAPI 서버가 실행 중입니다.")
            return True
        else:
            print("❌ 서버 응답이 올바르지 않습니다.")
            return False
    except Exception as e:
        print(f"❌ 서버에 연결할 수 없습니다: {e}")
        print("💡 먼저 'python custom_salesforce.py'로 서버를 실행해주세요.")
        return False


def main():
    """메인 테스트 함수"""
    print("🚀 Salesforce FastAPI 엔드포인트 테스트 시작\n")

    # 서버 상태 확인
    if not check_server_status():
        return

    print()

    # 각 엔드포인트 테스트
    test_get_pricebooks()
    test_get_all_orders()

    print("🏁 테스트 완료!")


if __name__ == "__main__":
    main()
