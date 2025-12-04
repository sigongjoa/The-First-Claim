/**
 * Sentry Error Tracking Initialization for React
 *
 * 프론트엔드 에러 추적 및 모니터링을 위한 Sentry SDK 설정
 */

import * as Sentry from '@sentry/react';
import { BrowserTracing } from '@sentry/tracing';

/**
 * React 앱에 Sentry 초기화
 *
 * @param {Object} options - 설정 옵션
 * @param {string} options.environment - 실행 환경 (development, staging, production)
 * @param {string} options.dsn - Sentry DSN (프로젝트별로 설정 필요)
 * @param {string} options.version - 앱 버전
 *
 * Example:
 *   initSentry({
 *     environment: 'production',
 *     dsn: 'https://example@o0.ingest.sentry.io/0',
 *     version: '0.1.0'
 *   });
 */
export function initSentry(options = {}) {
  const {
    environment = process.env.NODE_ENV || 'development',
    dsn = process.env.REACT_APP_SENTRY_DSN || 'https://example@o0.ingest.sentry.io/0',
    version = process.env.REACT_APP_VERSION || '0.1.0',
  } = options;

  Sentry.init({
    dsn,
    environment,
    release: version,

    // 성능 모니터링 (5% 샘플링)
    tracesSampleRate: 0.05,

    // 에러 샘플링 (프로덕션에서는 100%)
    sampleRate: environment === 'production' ? 1.0 : 0.5,

    // Browser Tracing 통합
    integrations: [
      new BrowserTracing({
        // 라우팅 추적 (React Router 사용 시)
        routingInstrumentation: Sentry.reactRouterV6Instrumentation(
          window.history
        ),
        tracePropagationTargets: [
          'localhost',
          /^\//,
          // API 엔드포인트
          /^https:\/\/api\.example\.com/,
        ],
      }),
      new Sentry.Replay({
        maskAllText: true,
        blockAllMedia: true,
      }),
    ],

    // 세션 리플레이 샘플링
    replaysSessionSampleRate: 0.1,
    replaysOnErrorSampleRate: 1.0,

    // 에러 필터링
    ignoreErrors: [
      // 브라우저 확장 프로그램 에러
      'top.GLOBALS',
      'chrome-extension://',
      'moz-extension://',

      // 흔한 네트워크 에러
      'NetworkError',
      'Network request failed',
      'Failed to fetch',

      // ResizeObserver 에러
      'ResizeObserver loop limit exceeded',

      // 마우스 추적 에러
      'Script error.',
    ],

    // 민감한 정보 필터링
    beforeSend: filterSensitiveData,
    beforeBreadcrumb: filterBreadcrumbs,
  });

  console.log(`✅ Sentry initialized for ${environment} environment`);
}

/**
 * 민감한 데이터 필터링
 */
function filterSensitiveData(event, hint) {
  // 개인정보 제거
  if (event.request) {
    if (event.request.url) {
      // URL의 쿼리 파라미터 제거
      const url = new URL(event.request.url);
      url.search = '';
      event.request.url = url.toString();
    }
  }

  // 에러 메시지에서 민감한 정보 제거
  if (event.exception) {
    event.exception.values?.forEach((exception) => {
      if (exception.value) {
        exception.value = redactPaths(exception.value);
      }
    });
  }

  return event;
}

/**
 * 경로 정보 제거
 */
function redactPaths(text) {
  // 절대 경로 제거
  return text.replace(
    /\/[a-zA-Z0-9_/\-\.]+/g,
    '/***'
  );
}

/**
 * Breadcrumb 필터링
 */
function filterBreadcrumbs(breadcrumb, hint) {
  // 너무 자주 발생하는 이벤트 필터링
  if (breadcrumb.category === 'console') {
    // console 로그는 에러/경고만 캡처
    if (breadcrumb.level !== 'error' && breadcrumb.level !== 'warning') {
      return null;
    }
  }

  // XHR 요청 필터링 (중요한 것만)
  if (breadcrumb.category === 'xhr') {
    // 헬스 체크 요청 제외
    if (breadcrumb.data?.url?.includes('/health')) {
      return null;
    }
  }

  return breadcrumb;
}

/**
 * 사용자 컨텍스트 설정
 */
export function setSentryUser(userId, email = null, username = null) {
  Sentry.setUser({
    id: userId,
    email,
    username,
  });
}

/**
 * 사용자 컨텍스트 해제
 */
export function clearSentryUser() {
  Sentry.setUser(null);
}

/**
 * 에러 캡처 (자동으로 하지 않는 경우)
 */
export function captureError(error, context = {}) {
  const eventId = Sentry.captureException(error);

  // 컨텍스트 추가
  Object.entries(context).forEach(([key, value]) => {
    Sentry.setTag(key, value);
  });

  return eventId;
}

/**
 * 메시지 캡처
 */
export function captureMessage(message, level = 'info', tags = {}) {
  Object.entries(tags).forEach(([key, value]) => {
    Sentry.setTag(key, value);
  });

  Sentry.captureMessage(message, level);
}

/**
 * 컨텍스트 설정
 */
export function setContext(name, context) {
  Sentry.setContext(name, context);
}

/**
 * 태그 설정
 */
export function setTag(key, value) {
  Sentry.setTag(key, value);
}

/**
 * Sentry Profiler HOC
 * 성능 추적이 필요한 컴포넌트를 감싸기
 *
 * Example:
 *   const WrappedComponent = withSentryProfiler(GameScreen);
 */
export function withSentryProfiler(Component) {
  return Sentry.withProfiler(Component);
}

// Sentry ErrorBoundary 재내보내기
export const ErrorBoundary = Sentry.ErrorBoundary;
