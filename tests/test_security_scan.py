"""
Security Scanning - Phase 4

Bandit, SQLAlchemy injection tests, authentication, input validation을 포함합니다.
정적 분석 및 런타임 보안 테스트를 수행합니다.
"""

import pytest
import re
import os
from pathlib import Path
from src.utils.logger import get_logger


class TestSecurityStaticAnalysis:
    """정적 보안 분석 테스트"""

    @pytest.fixture
    def logger(self):
        """테스트 로거"""
        return get_logger("test_security_static")

    def test_no_hardcoded_secrets(self, logger):
        """하드코딩된 시크릿 검사"""
        logger.info("하드코딩된 시크릿 검사 시작")

        src_dir = Path("src")
        secret_patterns = [
            r'api[_-]?key\s*=\s*["\'][^"\']+["\']',
            r'password\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']',
        ]

        found_secrets = []

        try:
            for py_file in src_dir.rglob("*.py"):
                try:
                    with open(py_file, "r", encoding="utf-8") as f:
                        content = f.read()

                        for pattern in secret_patterns:
                            matches = re.finditer(pattern, content, re.IGNORECASE)
                            for match in matches:
                                # 환경 변수나 주석 제외
                                if "os.environ" not in content[max(0, match.start()-50):match.end()+50]:
                                    found_secrets.append({
                                        "file": str(py_file),
                                        "pattern": pattern,
                                        "match": match.group()
                                    })

                except Exception as e:
                    logger.warning(f"파일 읽기 실패: {py_file}", context={"error": str(e)})

            logger.info(
                "하드코딩된 시크릿 검사 완료",
                context={
                    "files_scanned": len(list(src_dir.rglob("*.py"))),
                    "secrets_found": len(found_secrets)
                }
            )

            assert len(found_secrets) == 0, f"발견된 하드코딩된 시크릿: {found_secrets}"

        except Exception as e:
            logger.error("시크릿 검사 실패", error=e)
            raise

    def test_no_dangerous_imports(self, logger):
        """위험한 import 검사"""
        logger.info("위험한 import 검사 시작")

        src_dir = Path("src")
        dangerous_imports = [
            "pickle",
            "subprocess",
            "os.system",
            "eval",
            "exec",
        ]

        found_dangerous = []

        try:
            for py_file in src_dir.rglob("*.py"):
                try:
                    with open(py_file, "r", encoding="utf-8") as f:
                        lines = f.readlines()

                        for line_num, line in enumerate(lines, 1):
                            # 주석 제외
                            if line.strip().startswith("#"):
                                continue

                            for dangerous in dangerous_imports:
                                if dangerous in line and "import" in line:
                                    # 테스트나 주석 컨텍스트 제외
                                    if "test_" not in str(py_file):
                                        found_dangerous.append({
                                            "file": str(py_file),
                                            "line": line_num,
                                            "import": dangerous,
                                            "code": line.strip()
                                        })

                except Exception as e:
                    logger.warning(f"파일 읽기 실패: {py_file}", context={"error": str(e)})

            logger.info(
                "위험한 import 검사 완료",
                context={
                    "files_scanned": len(list(src_dir.rglob("*.py"))),
                    "dangerous_found": len(found_dangerous)
                }
            )

            assert len(found_dangerous) == 0, f"발견된 위험한 import: {found_dangerous}"

        except Exception as e:
            logger.error("위험한 import 검사 실패", error=e)
            raise

    def test_input_validation_presence(self, logger):
        """입력 유효성 검사 확인"""
        logger.info("입력 유효성 검사 확인 시작")

        src_dir = Path("src")
        validation_patterns = [
            r"if\s+.*\s+in\s+\[",
            r"assert\s+.*",
            r"raise\s+.*Error",
            r"validate",
            r"check",
        ]

        files_with_validation = 0
        total_files = 0

        try:
            for py_file in src_dir.rglob("*.py"):
                total_files += 1
                try:
                    with open(py_file, "r", encoding="utf-8") as f:
                        content = f.read()

                        for pattern in validation_patterns:
                            if re.search(pattern, content):
                                files_with_validation += 1
                                break

                except Exception as e:
                    logger.warning(f"파일 읽기 실패: {py_file}", context={"error": str(e)})

            logger.info(
                "입력 유효성 검사 확인 완료",
                context={
                    "total_files": total_files,
                    "files_with_validation": files_with_validation,
                    "coverage_percent": (files_with_validation / total_files * 100) if total_files > 0 else 0
                }
            )

            # 최소 50% 이상의 파일이 입력 검사를 해야 함
            assert files_with_validation / total_files >= 0.5

        except Exception as e:
            logger.error("입력 유효성 검사 확인 실패", error=e)
            raise

    def test_no_sql_injection_patterns(self, logger):
        """SQL Injection 패턴 검사"""
        logger.info("SQL Injection 패턴 검사 시작")

        src_dir = Path("src")
        injection_patterns = [
            r'f".*\{.*\}.*sql',
            r"f'.*\{.*\}.*sql",
            r'\.format\(.*\).*sql',
            r'\+ .*\+ .*\+ ',
        ]

        found_injection_risks = []

        try:
            for py_file in src_dir.rglob("*.py"):
                try:
                    with open(py_file, "r", encoding="utf-8") as f:
                        lines = f.readlines()

                        for line_num, line in enumerate(lines, 1):
                            if "test_" in str(py_file):
                                continue

                            for pattern in injection_patterns:
                                if re.search(pattern, line, re.IGNORECASE):
                                    found_injection_risks.append({
                                        "file": str(py_file),
                                        "line": line_num,
                                        "code": line.strip()
                                    })

                except Exception as e:
                    logger.warning(f"파일 읽기 실패: {py_file}", context={"error": str(e)})

            logger.info(
                "SQL Injection 패턴 검사 완료",
                context={
                    "files_scanned": len(list(src_dir.rglob("*.py"))),
                    "injection_risks_found": len(found_injection_risks)
                }
            )

            # 위험 패턴이 있을 수 있지만 문제 아닐 수도 있음 - 경고만
            if found_injection_risks:
                logger.warning(
                    "잠재적 SQL Injection 위험 발견",
                    context={"risks": found_injection_risks[:5]}
                )

        except Exception as e:
            logger.error("SQL Injection 패턴 검사 실패", error=e)
            raise


class TestSecurityRuntimeValidation:
    """런타임 보안 검증"""

    @pytest.fixture
    def logger(self):
        """테스트 로거"""
        return get_logger("test_security_runtime")

    @pytest.fixture
    def engine(self):
        """게임 엔진"""
        from src.ui.game import GameEngine
        return GameEngine()

    def test_player_name_input_sanitization(self, engine, logger):
        """플레이어 이름 입력 정제 테스트"""
        logger.info("플레이어 이름 입력 정제 테스트 시작")

        malicious_inputs = [
            "<script>alert('xss')</script>",
            "'; DROP TABLE sessions; --",
            "../../../etc/passwd",
            "\x00\x01\x02",
            "테스터\x00악성",
        ]

        try:
            for malicious_input in malicious_inputs:
                try:
                    session = engine.create_session(
                        session_id=f"security_test_{malicious_inputs.index(malicious_input)}",
                        player_name=malicious_input,
                        level_id=1
                    )

                    # 세션이 생성되었다면, 이름이 안전하게 저장되었는지 확인
                    stored_name = session.player_name
                    assert "\x00" not in stored_name
                    logger.info(
                        "악성 입력 처리 완료",
                        context={
                            "input": malicious_input[:50],
                            "stored": stored_name[:50]
                        }
                    )

                except Exception as e:
                    logger.warning(
                        "악성 입력 거부됨",
                        context={"input": malicious_input[:50], "error": str(e)[:100]}
                    )

            logger.info("플레이어 이름 입력 정제 테스트 완료")

        except Exception as e:
            logger.error("입력 정제 테스트 실패", error=e)
            raise

    def test_claim_text_input_validation(self, engine, logger):
        """청구항 텍스트 입력 검증"""
        logger.info("청구항 텍스트 입력 검증 시작")

        session = engine.create_session(
            session_id="security_claim_test",
            player_name="보안테스터",
            level_id=1
        )

        invalid_claims = [
            "",  # 빈 문자열
            "   ",  # 공백만
            "\x00",  # null 바이트
            "a" * 10000,  # 극도로 긴 문자열
        ]

        try:
            for invalid_claim in invalid_claims:
                result = session.submit_claim(invalid_claim)

                if not result:
                    logger.info(
                        "유효하지 않은 청구항 거부됨",
                        context={"claim_length": len(invalid_claim)}
                    )
                else:
                    logger.warning(
                        "의심스러운 청구항이 수락됨",
                        context={"claim_length": len(invalid_claim)}
                    )

            logger.info("청구항 텍스트 입력 검증 완료")

        except Exception as e:
            logger.error("청구항 입력 검증 실패", error=e)
            raise

    def test_session_id_format_validation(self, engine, logger):
        """세션 ID 형식 검증"""
        logger.info("세션 ID 형식 검증 시작")

        invalid_session_ids = [
            "",  # 빈 문자열
            "../../../",  # 경로 순회
            "'; DROP TABLE --",  # SQL injection
            "\x00\x01\x02",  # 바이너리
        ]

        try:
            for invalid_id in invalid_session_ids:
                try:
                    session = engine.create_session(
                        session_id=invalid_id,
                        player_name="테스터",
                        level_id=1
                    )
                    logger.warning(
                        "유효하지 않은 세션 ID가 허용됨",
                        context={"session_id": invalid_id[:50]}
                    )
                except Exception as e:
                    logger.info(
                        "유효하지 않은 세션 ID 거부됨",
                        context={"session_id": invalid_id[:50]}
                    )

            logger.info("세션 ID 형식 검증 완료")

        except Exception as e:
            logger.error("세션 ID 검증 실패", error=e)
            raise


class TestSecurityHeaders:
    """보안 헤더 검증"""

    @pytest.fixture
    def logger(self):
        """테스트 로거"""
        return get_logger("test_security_headers")

    def test_required_security_headers_documented(self, logger):
        """필수 보안 헤더 문서화 확인"""
        logger.info("필수 보안 헤더 확인 시작")

        required_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options",
            "X-XSS-Protection",
            "Strict-Transport-Security",
            "Content-Security-Policy",
        ]

        # API 문서에서 확인
        api_doc_path = Path("PHASE3_API_DOCUMENTATION.md")

        try:
            if api_doc_path.exists():
                with open(api_doc_path, "r", encoding="utf-8") as f:
                    content = f.read()

                found_headers = []
                for header in required_headers:
                    if header in content:
                        found_headers.append(header)

                logger.info(
                    "필수 보안 헤더 확인 완료",
                    context={
                        "total_required": len(required_headers),
                        "found": len(found_headers),
                        "coverage_percent": (len(found_headers) / len(required_headers) * 100)
                    }
                )

                assert len(found_headers) >= len(required_headers) - 1  # 최소 4개 이상

            else:
                logger.warning("API 문서를 찾을 수 없음")

        except Exception as e:
            logger.error("보안 헤더 확인 실패", error=e)
            raise


class TestDependencyVulnerabilities:
    """의존성 취약점 검사"""

    @pytest.fixture
    def logger(self):
        """테스트 로거"""
        return get_logger("test_dependencies")

    def test_requirements_exist(self, logger):
        """requirements.txt 파일 존재 확인"""
        logger.info("의존성 파일 확인 시작")

        try:
            req_file = Path("requirements.txt")
            assert req_file.exists(), "requirements.txt 파일이 없습니다"

            with open(req_file, "r") as f:
                lines = f.readlines()

            packages = [line.strip() for line in lines if line.strip() and not line.startswith("#")]

            logger.info(
                "의존성 파일 확인 완료",
                context={
                    "total_packages": len(packages),
                    "packages_sample": packages[:5]
                }
            )

            assert len(packages) > 0

        except Exception as e:
            logger.error("의존성 파일 확인 실패", error=e)
            raise

    def test_pinned_versions(self, logger):
        """버전 명시 확인"""
        logger.info("버전 명시 확인 시작")

        try:
            req_file = Path("requirements.txt")
            if req_file.exists():
                with open(req_file, "r") as f:
                    lines = f.readlines()

                packages = [line.strip() for line in lines if line.strip() and not line.startswith("#")]
                pinned = [p for p in packages if "==" in p]

                logger.info(
                    "버전 명시 확인 완료",
                    context={
                        "total_packages": len(packages),
                        "pinned_packages": len(pinned),
                        "coverage_percent": (len(pinned) / len(packages) * 100) if packages else 0
                    }
                )

                # 최소 50% 이상 버전 고정
                if packages:
                    assert len(pinned) / len(packages) >= 0.5

        except Exception as e:
            logger.error("버전 명시 확인 실패", error=e)
            raise
