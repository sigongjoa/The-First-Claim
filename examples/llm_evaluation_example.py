"""
LLM 기반 청구항 평가 예제

이 예제는 Claude API를 사용하여 한국 특허법 기준으로 청구항을 평가합니다.
"""

import os
import sys

# 프로젝트 경로 설정
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from src.ui.game import GameEngine


def main():
    """LLM 기반 평가 예제"""
    
    # API 키 확인
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY 환경변수가 설정되지 않았습니다.")
        print("설정 방법:")
        print("  export ANTHROPIC_API_KEY='your-api-key'")
        return

    # LLM 모드로 게임 엔진 초기화
    print("🚀 LLM 기반 청구항 평가 시스템 시작...\n")
    
    try:
        engine = GameEngine(use_llm=True)
        print("✅ LLM 평가기 초기화 완료\n")
    except Exception as e:
        print(f"❌ LLM 초기화 실패: {e}")
        return

    # 게임 세션 생성
    session = engine.create_session(
        session_id="llm_example_session",
        player_name="LLM 평가 테스트",
        level_id=1
    )

    # 청구항 예제
    claims = [
        "배터리 장치는 양극, 음극, 전해질, 분리막을 포함하는 에너지 저장 장치이다",
        "제1항의 배터리 장치에서 양극은 리튬 함유 산화물로 이루어진다",
        "제1항의 배터리 장치에서 음극은 흑연계 재료로 이루어진다",
    ]

    # 청구항 제출
    print("📝 청구항 제출 중...\n")
    for i, claim in enumerate(claims, 1):
        session.submit_claim(claim)
        print(f"청구항 {i}: {claim[:50]}...")

    print()

    # LLM 기반 평가 실행
    print("🤖 LLM 기반 평가 진행 중...\n")
    print("=" * 70)
    
    try:
        success, feedback, details = engine.evaluate_claims_with_llm(
            "llm_example_session"
        )

        # 결과 출력
        for line in feedback:
            print(line)

        print("=" * 70)
        print()

        # 최종 결과
        if success:
            print(f"✅ 최종 결과: {'성공' if details['overall_success'] else '실패'}")
            print(f"획득 점수: {details.get('score', 0)}점")
        else:
            print("❌ 평가 실패")

        print()
        print("📊 상세 평가 결과:")
        for eval_result in details.get("llm_evaluations", []):
            print(f"\n  청구항 {eval_result['claim_number']}:")
            print(f"    - 상태: {'✅ 등록 가능' if eval_result['is_approvable'] else '❌ 등록 불가'}")
            print(f"    - 점수: {eval_result['overall_score']:.2f}/1.0")
            print(f"    - 승인 확률: {eval_result['approval_probability']:.1%}")

    except Exception as e:
        print(f"❌ LLM 평가 중 오류 발생: {e}")
        print(f"   오류 타입: {type(e).__name__}")
        print(f"   API 키가 올바른지 확인하세요.")


if __name__ == "__main__":
    main()
