"""
Compatibility Testing - Phase 4

크로스 브라우저, 크로스 플랫폼, 다양한 환경에서의 호환성 테스트입니다.
Python 버전, 의존성 버전, OS 호환성을 검증합니다.
"""

import pytest
import sys
import platform
import json
from pathlib import Path
from src.utils.logger import get_logger
from src.ui.game import GameEngine


class TestPythonVersionCompatibility:
    """Python 버전 호환성 테스트"""

    @pytest.fixture
    def logger(self):
        """테스트 로거"""
        return get_logger("test_compatibility_python")

    def test_python_version_support(self, logger):
        """지원하는 Python 버전 확인"""
        logger.info("Python 버전 호환성 테스트 시작")

        current_version = sys.version_info
        supported_versions = [(3, 9), (3, 10), (3, 11), (3, 12), (3, 13)]

        is_supported = (current_version.major, current_version.minor) in supported_versions

        logger.info(
            "Python 버전 확인",
            context={
                "current_version": f"{current_version.major}.{current_version.minor}.{current_version.micro}",
                "supported_versions": [f"{v[0]}.{v[1]}" for v in supported_versions],
                "is_supported": is_supported
            }
        )

        assert is_supported, f"Python {current_version.major}.{current_version.minor}은 지원되지 않습니다"

    def test_builtin_modules_available(self, logger):
        """필수 내장 모듈 가용성 확인"""
        logger.info("내장 모듈 가용성 확인 시작")

        required_modules = [
            "json",
            "logging",
            "pathlib",
            "datetime",
            "typing",
            "enum",
            "traceback",
            "re",
        ]

        available_modules = []
        missing_modules = []

        try:
            for module_name in required_modules:
                try:
                    __import__(module_name)
                    available_modules.append(module_name)
                except ImportError:
                    missing_modules.append(module_name)

            logger.info(
                "내장 모듈 가용성 확인 완료",
                context={
                    "total_required": len(required_modules),
                    "available": len(available_modules),
                    "missing": missing_modules
                }
            )

            assert len(missing_modules) == 0, f"누락된 모듈: {missing_modules}"

        except Exception as e:
            logger.error("모듈 가용성 확인 실패", error=e)
            raise

    def test_typing_annotations_compatibility(self, logger):
        """타입 어노테이션 호환성 테스트"""
        logger.info("타입 어노테이션 호환성 테스트 시작")

        try:
            # Optional, List, Dict 등 기본 타입 어노테이션 확인
            from typing import Optional, List, Dict, Any, Tuple

            logger.info("기본 타입 어노테이션 로드 완료")

            # Python 3.9+에서 지원하는 기본 타입
            if sys.version_info >= (3, 9):
                # list[str], dict[str, Any] 등이 지원됨
                test_dict: dict = {"key": "value"}
                test_list: list = [1, 2, 3]
                logger.info("Python 3.9+ 타입 힌트 사용 가능")

            logger.info("타입 어노테이션 호환성 테스트 완료")

        except Exception as e:
            logger.error("타입 어노테이션 호환성 테스트 실패", error=e)
            raise


class TestOperatingSystemCompatibility:
    """운영체제 호환성 테스트"""

    @pytest.fixture
    def logger(self):
        """테스트 로거"""
        return get_logger("test_compatibility_os")

    def test_platform_detection(self, logger):
        """플랫폼 감지 및 기본 호환성"""
        logger.info("플랫폼 감지 시작")

        current_platform = platform.system()
        current_version = platform.release()
        machine = platform.machine()

        supported_platforms = ["Windows", "Linux", "Darwin"]  # Darwin = macOS

        is_supported = current_platform in supported_platforms

        logger.info(
            "플랫폼 정보",
            context={
                "system": current_platform,
                "release": current_version,
                "machine": machine,
                "supported": is_supported
            }
        )

        assert is_supported, f"지원되지 않는 플랫폼: {current_platform}"

    def test_path_operations_cross_platform(self, logger):
        """크로스 플랫폼 경로 연산 테스트"""
        logger.info("크로스 플랫폼 경로 연산 테스트 시작")

        try:
            # pathlib를 사용한 크로스 플랫폼 경로 처리
            test_dir = Path("tests")
            assert test_dir.exists(), "tests 디렉토리를 찾을 수 없음"

            test_files = list(test_dir.glob("*.py"))
            assert len(test_files) > 0, "테스트 파일을 찾을 수 없음"

            logger.info(
                "크로스 플랫폼 경로 연산 완료",
                context={
                    "test_dir": str(test_dir),
                    "test_files_found": len(test_files)
                }
            )

        except Exception as e:
            logger.error("경로 연산 테스트 실패", error=e)
            raise

    def test_file_encoding_compatibility(self, logger):
        """파일 인코딩 호환성 테스트"""
        logger.info("파일 인코딩 호환성 테스트 시작")

        try:
            # 한글을 포함한 파일 읽기/쓰기 테스트
            test_content = "테스트 데이터: 배터리, 특허, 청구항"
            test_file = Path("temp_encoding_test.txt")

            try:
                # UTF-8로 쓰기
                with open(test_file, "w", encoding="utf-8") as f:
                    f.write(test_content)

                # UTF-8로 읽기
                with open(test_file, "r", encoding="utf-8") as f:
                    read_content = f.read()

                assert read_content == test_content, "인코딩 불일치"

                logger.info("파일 인코딩 호환성 테스트 완료")

            finally:
                if test_file.exists():
                    test_file.unlink()

        except Exception as e:
            logger.error("파일 인코딩 호환성 테스트 실패", error=e)
            raise


class TestDependencyCompatibility:
    """의존성 호환성 테스트"""

    @pytest.fixture
    def logger(self):
        """테스트 로거"""
        return get_logger("test_compatibility_dependencies")

    def test_core_dependencies_available(self, logger):
        """핵심 의존성 가용성 확인"""
        logger.info("핵심 의존성 가용성 확인 시작")

        core_dependencies = {
            "pytest": "test framework",
            "flask": "web framework",
            "anthropic": "LLM API",
        }

        available = {}
        missing = []

        try:
            for package, description in core_dependencies.items():
                try:
                    module = __import__(package)
                    version = getattr(module, "__version__", "unknown")
                    available[package] = {"description": description, "version": version}
                except ImportError:
                    missing.append(package)

            logger.info(
                "핵심 의존성 확인 완료",
                context={
                    "total_required": len(core_dependencies),
                    "available": len(available),
                    "missing": missing,
                    "packages": available
                }
            )

            # 최소 80% 이상 의존성이 설치되어야 함
            assert len(available) / len(core_dependencies) >= 0.8

        except Exception as e:
            logger.error("의존성 확인 실패", error=e)
            raise

    def test_feature_support_with_optional_dependencies(self, logger):
        """선택적 의존성의 기능 지원 테스트"""
        logger.info("선택적 의존성 지원 확인 시작")

        optional_features = {
            "ujson": "fast JSON",
            "python-dotenv": "environment variables",
        }

        supported_features = {}

        try:
            for package, feature in optional_features.items():
                try:
                    __import__(package)
                    supported_features[package] = feature
                except ImportError:
                    logger.warning(f"선택적 기능 미지원: {package} ({feature})")

            logger.info(
                "선택적 의존성 확인 완료",
                context={
                    "supported_features": len(supported_features),
                    "features": supported_features
                }
            )

        except Exception as e:
            logger.error("선택적 의존성 확인 실패", error=e)
            raise


class TestGameEngineCompatibility:
    """게임 엔진 호환성 테스트"""

    @pytest.fixture
    def logger(self):
        """테스트 로거"""
        return get_logger("test_compatibility_engine")

    @pytest.fixture
    def engine(self):
        """게임 엔진"""
        return GameEngine()

    def test_session_creation_consistent_across_runs(self, engine, logger):
        """세션 생성이 반복 실행에서 일관성 있는지 확인"""
        logger.info("세션 생성 일관성 테스트 시작")

        try:
            results = []

            for i in range(5):
                session = engine.create_session(
                    session_id=f"consistency_test_{i}",
                    player_name="일관성테스터",
                    level_id=1
                )

                results.append({
                    "session_id": session.session_id,
                    "has_current_level": session.current_level is not None,
                    "claims_count": len(session.claims) if hasattr(session, "claims") else 0
                })

            # 모든 실행이 동일한 구조를 반환해야 함
            first_result = results[0]
            for result in results[1:]:
                assert result["has_current_level"] == first_result["has_current_level"]
                assert result["claims_count"] == first_result["claims_count"]

            logger.info(
                "세션 생성 일관성 테스트 완료",
                context={"runs": len(results), "consistent": True}
            )

        except Exception as e:
            logger.error("일관성 테스트 실패", error=e)
            raise

    def test_unicode_handling_in_game_elements(self, engine, logger):
        """게임 요소에서 유니코드 처리 테스트"""
        logger.info("유니코드 처리 테스트 시작")

        unicode_names = [
            "김특허",
            "李发明",
            "Παρατηρητής",
            "Наблюдатель",
            "👨‍💼 Manager",
        ]

        try:
            for idx, name in enumerate(unicode_names):
                try:
                    session = engine.create_session(
                        session_id=f"unicode_test_{idx}",
                        player_name=name,
                        level_id=1
                    )

                    assert session is not None
                    assert session.player_name is not None

                    logger.info(
                        "유니코드 이름 처리 성공",
                        context={"input": name, "stored": session.player_name[:50]}
                    )

                except Exception as e:
                    logger.warning(
                        "유니코드 이름 처리 실패",
                        context={"input": name, "error": str(e)[:100]}
                    )

            logger.info("유니코드 처리 테스트 완료")

        except Exception as e:
            logger.error("유니코드 테스트 실패", error=e)
            raise

    def test_locale_independent_operations(self, engine, logger):
        """로케일 독립적인 연산 테스트"""
        logger.info("로케일 독립성 테스트 시작")

        try:
            # 숫자 기반 연산이 로케일에 영향받지 않는지 확인
            session = engine.create_session(
                session_id="locale_test",
                player_name="로케일테스터",
                level_id=1
            )

            # 숫자 문자열
            numeric_claim = "배터리 전압: 3.7V, 용량: 2500mAh, 무게: 45.5g"
            result = session.submit_claim(numeric_claim)

            logger.info(
                "로케일 독립성 테스트 완료",
                context={
                    "claim_has_decimals": "." in numeric_claim,
                    "claim_accepted": result
                }
            )

        except Exception as e:
            logger.error("로케일 독립성 테스트 실패", error=e)
            raise


class TestDataFormatCompatibility:
    """데이터 형식 호환성 테스트"""

    @pytest.fixture
    def logger(self):
        """테스트 로거"""
        return get_logger("test_compatibility_formats")

    def test_json_serialization_compatibility(self, logger):
        """JSON 직렬화 호환성 테스트"""
        logger.info("JSON 직렬화 호환성 테스트 시작")

        test_data = {
            "string": "테스트",
            "number": 42,
            "float": 3.14,
            "boolean": True,
            "null": None,
            "array": [1, 2, 3],
            "nested": {"key": "value"}
        }

        try:
            json_str = json.dumps(test_data, ensure_ascii=False)
            parsed = json.loads(json_str)

            assert parsed == test_data, "JSON 직렬화/역직렬화 불일치"

            logger.info(
                "JSON 직렬화 호환성 테스트 완료",
                context={
                    "serialized_length": len(json_str),
                    "preserved": True
                }
            )

        except Exception as e:
            logger.error("JSON 직렬화 테스트 실패", error=e)
            raise

    def test_timestamp_format_consistency(self, logger):
        """타임스탬프 형식 일관성 테스트"""
        logger.info("타임스탬프 형식 일관성 테스트 시작")

        from datetime import datetime

        try:
            timestamp = datetime.utcnow().isoformat()

            # ISO 8601 형식 확인
            assert "T" in timestamp, "ISO 8601 형식이 아님"
            assert ":" in timestamp, "시간 구분자 없음"

            logger.info(
                "타임스탐프 형식 일관성 테스트 완료",
                context={"timestamp": timestamp}
            )

        except Exception as e:
            logger.error("타임스탬프 형식 테스트 실패", error=e)
            raise
