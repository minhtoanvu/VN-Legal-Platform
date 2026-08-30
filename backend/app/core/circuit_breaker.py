import time
import logging
from enum import Enum
from typing import Callable, Any
import asyncio

log = logging.getLogger(__name__)

class CircuitState(Enum):
    CLOSED = "CLOSED"      # Bình thường
    OPEN = "OPEN"          # Ngắt mạch
    HALF_OPEN = "HALF_OPEN"# Thử lại

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0

    def _update_state(self):
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                log.info("CircuitBreaker chuyển sang trạng thái HALF_OPEN")

    def record_success(self):
        self.failure_count = 0
        if self.state != CircuitState.CLOSED:
            log.info("CircuitBreaker chuyển sang trạng thái CLOSED (Đã phục hồi)")
        self.state = CircuitState.CLOSED

    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        log.warning(f"CircuitBreaker ghi nhận lỗi ({self.failure_count}/{self.failure_threshold})")
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            log.error(f"CircuitBreaker NGẮT MẠCH (OPEN). Tạm dừng {self.recovery_timeout}s.")

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        self._update_state()

        if self.state == CircuitState.OPEN:
            raise Exception("CircuitBreaker is OPEN: Dịch vụ đang bị gián đoạn.")

        try:
            result = await func(*args, **kwargs)
            self.record_success()
            return result
        except Exception as e:
            self.record_failure()
            raise e

# Singleton instance for LLM (Gemini)
llm_circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=60)
