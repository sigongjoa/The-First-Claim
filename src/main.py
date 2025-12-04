#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PROJECT: OVERRIDE
Test-Driven Legal Engine (테스트 주도형 법률 엔진 구축 프로젝트)

메인 진입점 - 게임 엔진 시작
"""

import os
import sys
import uuid
from datetime import datetime
import time

# 프로젝트 경로 설정
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

# Import game engine and UI
from src.ui.game import GameEngine, GameInterface, GameStatus


class ProjectIntroduction:
    """프로젝트 소개 및 초기화"""

    def __init__(self):
        self.project_name = "PROJECT: OVERRIDE"
        self.tagline = "Test-Driven Legal Engine"
        self.start_date = "2025-12-03"
        self.version = "0.1.0"

    def display_welcome(self):
        """환영 메시지 표시"""
        print("\n" + "=" * 70)
        print(f"{self.project_name.center(70)}")
        print(f"{self.tagline.center(70)}")
        print("=" * 70)
        print()
        print("📚 변리사 시험을 위한 TDD 학습 플랫폼에 오신 것을 환영합니다!")
        print()
        print("이 프로젝트는:")
        print("  ✓ 기출문제부터 시작하는 역순 학습")
        print("  ✓ AI 심사관과의 법률 배틀")
        print("  ✓ 코드로 검증하는 법률 이해")
        print()
        print("핵심 철학: '법을 읽는 사용자가 아니라, 법을 설계하는 창조자가 된다'")
        print()
        print("=" * 70)
        print()

    def display_startup_status(self):
        """시작 상태 표시"""
        print("[시스템 초기화 중...]")
        print()
        print(f"Project: {self.project_name}")
        print(f"Version: {self.version}")
        print(f"Start Date: {self.start_date}")
        print(f"Current Date: {datetime.now().strftime('%Y-%m-%d')}")
        print()

    def display_menu(self):
        """메인 메뉴 표시"""
        print("[메인 메뉴]")
        print()
        print("1. 📖 문서 읽기 (프로젝트 개요)")
        print("2. 🎮 게임 시작 (Phase 1: 민법의 기초)")
        print("3. 📊 학습 진도 확인")
        print("4. 🧪 테스트 실행")
        print("5. ⚙️  프로젝트 설정")
        print("6. 🚀 시스템 상태 확인")
        print("7. 📚 문서 인덱스")
        print("0. 🚪 종료")
        print()

    def show_documentation_index(self):
        """문서 인덱스 표시"""
        print("\n[📚 문서 인덱스]")
        print()
        print("1. 01_project_overview.md")
        print("   → 프로젝트의 전체 개요 및 목표")
        print()
        print("2. 02_game_mechanics.md")
        print("   → 게임 시스템 및 게임 플레이 설명")
        print()
        print("3. 03_technical_architecture.md")
        print("   → 기술 스택 및 시스템 아키텍처")
        print()
        print("4. 04_roadmap.md")
        print("   → 단계별 개발 및 학습 로드맵")
        print()
        print("5. 05_study_methodology.md")
        print("   → TDD 학습 방법론 상세 설명")
        print()
        print("6. 06_design_philosophy.md")
        print("   → 설계 철학 및 핵심 원칙")
        print()

    def get_user_choice(self):
        """사용자 선택 받기"""
        while True:
            try:
                choice = input("\n메뉴를 선택하세요 (0-7): ").strip()
                if choice in ["0", "1", "2", "3", "4", "5", "6", "7"]:
                    return choice
                else:
                    print("⚠️  잘못된 선택입니다. 0-7 사이의 숫자를 입력해주세요.")
            except KeyboardInterrupt:
                print("\n\n시스템을 종료합니다.")
                sys.exit(0)

    def handle_choice(self, choice):
        """선택에 따른 처리"""
        if choice == "0":
            self.display_goodbye()
            sys.exit(0)

        elif choice == "1":
            self.display_project_overview()

        elif choice == "2":
            self.start_game()

        elif choice == "3":
            self.show_progress()

        elif choice == "4":
            self.run_tests()

        elif choice == "5":
            self.show_settings()

        elif choice == "6":
            self.show_system_status()

        elif choice == "7":
            self.show_documentation_index()

    def display_project_overview(self):
        """프로젝트 개요 표시"""
        print("\n" + "=" * 70)
        print("PROJECT: OVERRIDE - 프로젝트 개요")
        print("=" * 70)
        print()
        print("📌 프로젝트 목표:")
        print("   - 변리사 시험 고득점 합격")
        print("   - AI Legal Tech 포트폴리오 구축")
        print("   - 대체 불가능한 변리사 양성")
        print()
        print("📌 핵심 특징:")
        print("   - TDD (Test-Driven Development) 기반 학습")
        print("   - AI 심사관과의 법률 배틀")
        print("   - 게임화된 학습 경험")
        print()
        print("📌 4단계 구성:")
        print("   Phase 1: 민법의 기초 (로직 게이트)")
        print("   Phase 2: 특허법의 구조 (시스템 아키텍처)")
        print("   Phase 3: 판례의 시각화 (데이터베이스)")
        print("   Phase 4: Final Override (시험장 배포)")
        print()
        print("더 자세한 내용은 docs/01_project_overview.md를 참고하세요.")
        print("=" * 70)

    def start_game(self):
        """게임 시작 - 실제 게임 루프"""
        try:
            print("\n" + "=" * 70)
            print("🎮 청구항 작성 게임 시작")
            print("=" * 70)
            print()

            # 게임 엔진 초기화
            engine = GameEngine()
            ui = GameInterface()

            # 1. 플레이어 이름 입력
            print(ui.display_welcome())

            player_name = input("플레이어 이름을 입력하세요: ").strip()
            if not player_name:
                player_name = "Anonymous Player"

            # 2. 레벨 선택
            print("\n[📋 레벨 선택]")
            print()
            for level_id, level in engine.levels.items():
                print(f"{level_id}. {level}")
                print(f"   설명: {level.description}")
                print(f"   필요 청구항: {level.target_claims}개")
                print(f"   시간 제한: {level.time_limit}초")
                print()

            while True:
                try:
                    level_choice = input("레벨을 선택하세요 (1-3): ").strip()
                    level_id = int(level_choice)
                    if 1 <= level_id <= 3:
                        break
                    else:
                        print("⚠️  1-3 사이의 숫자를 입력해주세요.")
                except ValueError:
                    print("⚠️  숫자를 입력해주세요.")

            # 3. 게임 세션 생성
            session_id = f"session_{uuid.uuid4().hex[:8]}"
            session = engine.create_session(
                session_id=session_id,
                player_name=player_name,
                level_id=level_id
            )

            session.start_game(time.time())

            level = engine.get_level(level_id)
            print(ui.display_level_info(level))
            print(ui.display_progress(session.player))

            # 4. 청구항 입력
            print(f"\n[📝 청구항 작성]")
            print(f"총 {level.target_claims}개의 청구항을 작성해야 합니다.")
            print()

            for i in range(1, level.target_claims + 1):
                claim_type = "독립항" if i == 1 else "종속항"
                print(f"\n청구항 {i} ({claim_type}):")
                if i == 1:
                    print("  💡 팁: 기본적인 기술적 특징을 명확하게 포함해야 합니다.")
                else:
                    print("  💡 팁: 선행항을 명시적으로 참조해야 합니다 (예: 제1항)")

                print()

                claim_content = input(f"청구항 {i}를 입력하세요 (최소 20자): ").strip()

                if not claim_content:
                    print("⚠️  청구항이 비어있습니다. 다시 입력해주세요.")
                    i -= 1
                    continue

                session.submit_claim(claim_content)

            # 5. 청구항 평가
            print("\n" + "=" * 70)
            print("📊 청구항 평가 중...")
            print("=" * 70)
            print()

            success, feedback, details = engine.evaluate_claims(session_id)

            # 6. 결과 표시
            for msg in feedback:
                print(msg)

            session.complete_game(time.time(), success)

            # 7. 최종 결과
            print("\n" + "=" * 70)
            if success:
                print(f"🎉 {player_name}님, 축하합니다!")
                print(f"레벨 {level_id}을(를) 통과했습니다!")
                print(f"획득 점수: {details.get('score', 0)}점")
                session.player.complete_level(level_id)
            else:
                print(f"❌ {player_name}님, 아쉽습니다.")
                print(f"아직 요구사항을 충족하지 못했습니다.")
                print("\n다시 시도해주세요!")

            print("=" * 70)
            print()

        except Exception as e:
            from src.utils.logger import get_logger
            logger = get_logger("game_main")
            logger.error(
                "Game session failed with exception",
                error=e,
                context={
                    "error_type": type(e).__name__,
                    "traceback": traceback.format_exc()[:500]
                }
            )
            print(f"\n❌ 게임 중 오류 발생: {e}")
            print("오류가 기록되었습니다. 관리자에게 문의해주세요.")

    def show_progress(self):
        """학습 진도 확인"""
        print("\n" + "=" * 70)
        print("📊 학습 진도 확인")
        print("=" * 70)
        print()
        print("시스템: 아직 학습 데이터가 없습니다.")
        print()
        print("첫 번째 기출문제를 풀어보세요!")
        print("  $ python -m pytest tests/test_civil_law.py")
        print()
        print("진도가 저장되려면:")
        print("  1. 기출문제 풀이")
        print("  2. AI 심사관으로부터 피드백")
        print("  3. 코드 리팩토링")
        print("  4. 다시 문제 풀기 (검증)")
        print()
        print("=" * 70)

    def run_tests(self):
        """테스트 실행"""
        print("\n" + "=" * 70)
        print("🧪 테스트 실행")
        print("=" * 70)
        print()
        print("현재 테스트 상황:")
        print("  ☐ 테스트 코드가 아직 작성되지 않았습니다.")
        print()
        print("테스트 작성 방법:")
        print("  1. tests/ 디렉토리에서 test_*.py 파일 작성")
        print("  2. 다음 명령어로 실행:")
        print("     $ pytest tests/ -v")
        print()
        print("예시:")
        print("  $ pytest tests/test_civil_law.py::test_acquisition_by_prescription")
        print()
        print("=" * 70)

    def show_settings(self):
        """프로젝트 설정"""
        print("\n" + "=" * 70)
        print("⚙️  프로젝트 설정")
        print("=" * 70)
        print()
        print("개발 환경:")
        print(f"  - Python 버전: {sys.version.split()[0]}")
        print(f"  - 프로젝트 경로: {PROJECT_ROOT}")
        print()
        print("필수 패키지 설치:")
        print("  $ pip install -r requirements.txt")
        print()
        print("개발 패키지 설치:")
        print("  $ pip install -r requirements-dev.txt")
        print()
        print("=" * 70)

    def show_system_status(self):
        """시스템 상태 확인"""
        print("\n" + "=" * 70)
        print("🚀 시스템 상태")
        print("=" * 70)
        print()
        print("프로젝트 상태: ✓ 초기화 완료")
        print()
        print("디렉토리 구조:")
        print(f"  ✓ {PROJECT_ROOT}/src/")
        print(f"  ✓ {PROJECT_ROOT}/tests/")
        print(f"  ✓ {PROJECT_ROOT}/docs/")
        print(f"  ✓ {PROJECT_ROOT}/data/")
        print()
        print("문서 상태:")
        print("  ✓ 01_project_overview.md")
        print("  ✓ 02_game_mechanics.md")
        print("  ✓ 03_technical_architecture.md")
        print("  ✓ 04_roadmap.md")
        print("  ✓ 05_study_methodology.md")
        print("  ✓ 06_design_philosophy.md")
        print()
        print("개발 상태:")
        print("  ☐ Phase 1: 게임 엔진 개발 예정")
        print("  ☐ Phase 2: 청구항 시스템 개발 예정")
        print("  ☐ Phase 3: RAG 시스템 개발 예정")
        print("  ☐ Phase 4: 최종 시뮬레이션 개발 예정")
        print()
        print("다음 단계:")
        print("  1. 문서를 읽고 프로젝트를 이해한다")
        print("  2. src/game_engine.py 파일을 작성한다")
        print("  3. 테스트 코드를 작성한다")
        print("  4. 게임을 실행한다")
        print()
        print("=" * 70)

    def display_goodbye(self):
        """종료 메시지"""
        print("\n" + "=" * 70)
        print("감사합니다!")
        print("=" * 70)
        print()
        print("✨ PROJECT: OVERRIDE와 함께 변리사의 길을 걸어가세요!")
        print()
        print("다음에 다시 시작할 때:")
        print("  $ python src/main.py")
        print()
        print("=" * 70 + "\n")

    def run(self):
        """메인 루프"""
        self.display_welcome()
        self.display_startup_status()

        while True:
            self.display_menu()
            choice = self.get_user_choice()
            self.handle_choice(choice)
            print()


def main():
    """메인 함수"""
    try:
        intro = ProjectIntroduction()
        intro.run()
    except KeyboardInterrupt:
        print("\n프로그램이 사용자에 의해 중단되었습니다.")
        sys.exit(0)
    except Exception as e:
        from src.utils.logger import get_logger
        import traceback
        logger = get_logger("main")
        logger.error(
            "Application crashed with unhandled exception",
            error=e,
            context={
                "error_type": type(e).__name__,
                "traceback": traceback.format_exc()[:1000]
            }
        )
        print(f"\n❌ 오류 발생: {e}")
        print("문제가 발생했습니다. 관리자에게 문의해주세요.")
        sys.exit(1)


if __name__ == "__main__":
    main()
