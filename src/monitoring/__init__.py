# Monitoring Module

# Try to import Sentry, but gracefully handle if not available
try:
    from src.monitoring.sentry_init import (
        init_sentry,
        capture_message,
        capture_exception,
        set_user_context,
        set_context,
        set_tag,
    )
    __all__ = [
        "init_sentry",
        "capture_message",
        "capture_exception",
        "set_user_context",
        "set_context",
        "set_tag",
    ]
except ImportError:
    # Sentry SDK not available, provide stub implementations
    def init_sentry(*args, **kwargs):
        pass

    def capture_message(*args, **kwargs):
        pass

    def capture_exception(*args, **kwargs):
        pass

    def set_user_context(*args, **kwargs):
        pass

    def set_context(*args, **kwargs):
        pass

    def set_tag(*args, **kwargs):
        pass

    __all__ = [
        "init_sentry",
        "capture_message",
        "capture_exception",
        "set_user_context",
        "set_context",
        "set_tag",
    ]
