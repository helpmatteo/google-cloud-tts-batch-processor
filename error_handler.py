#!/usr/bin/env python3
"""
Advanced Error Handling for TTS Batch Processor
Includes circuit breaker pattern, retry mechanisms, and error recovery
"""

import time
import logging
from functools import wraps
from typing import Callable, Any, Dict, Optional, List
from dataclasses import dataclass
from enum import Enum
import threading

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "CLOSED"      # Normal operation
    OPEN = "OPEN"          # Circuit is open, requests fail fast
    HALF_OPEN = "HALF_OPEN"  # Testing if service is back

@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker"""
    failure_threshold: int = 5
    recovery_timeout: float = 60.0
    expected_exception: type = Exception
    monitor_interval: float = 10.0

class CircuitBreaker:
    """Circuit breaker pattern implementation"""
    
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
        self.lock = threading.Lock()
        self.monitor_thread = None
        self._start_monitoring()
    
    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return self.call(func, *args, **kwargs)
        return wrapper
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.config.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                logger.info("Circuit breaker transitioning to HALF_OPEN")
            else:
                raise CircuitBreakerOpenException("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.config.expected_exception as e:
            self._on_failure(e)
            raise
    
    def _on_success(self):
        """Handle successful execution"""
        with self.lock:
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
                logger.info("Circuit breaker transitioning to CLOSED")
            self.failure_count = 0
    
    def _on_failure(self, exception: Exception):
        """Handle failed execution"""
        with self.lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.config.failure_threshold:
                self.state = CircuitState.OPEN
                logger.warning(f"Circuit breaker opened after {self.failure_count} failures")
    
    def _start_monitoring(self):
        """Start monitoring thread"""
        def monitor():
            while True:
                time.sleep(self.config.monitor_interval)
                self._log_status()
        
        self.monitor_thread = threading.Thread(target=monitor, daemon=True)
        self.monitor_thread.start()
    
    def _log_status(self):
        """Log current circuit breaker status"""
        logger.debug(f"Circuit breaker status: {self.state.value}, "
                    f"failures: {self.failure_count}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current circuit breaker status"""
        return {
            'state': self.state.value,
            'failure_count': self.failure_count,
            'last_failure_time': self.last_failure_time,
            'config': {
                'failure_threshold': self.config.failure_threshold,
                'recovery_timeout': self.config.recovery_timeout
            }
        }

class CircuitBreakerOpenException(Exception):
    """Exception raised when circuit breaker is open"""
    pass

class RetryConfig:
    """Configuration for retry mechanism"""
    
    def __init__(self, 
                 max_attempts: int = 3,
                 base_delay: float = 1.0,
                 max_delay: float = 60.0,
                 exponential_base: float = 2.0,
                 jitter: bool = True):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter

def retry_with_backoff(config: RetryConfig):
    """Retry decorator with exponential backoff"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(config.max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt == config.max_attempts - 1:
                        logger.error(f"Final attempt failed: {e}")
                        raise
                    
                    # Calculate delay with exponential backoff
                    delay = min(
                        config.base_delay * (config.exponential_base ** attempt),
                        config.max_delay
                    )
                    
                    # Add jitter if enabled
                    if config.jitter:
                        import random
                        delay *= (0.5 + random.random() * 0.5)
                    
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. "
                                 f"Retrying in {delay:.2f}s...")
                    time.sleep(delay)
            
            raise last_exception
        return wrapper
    return decorator

class ErrorHandler:
    """Main error handler class"""
    
    def __init__(self):
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.error_stats: Dict[str, Dict] = {}
        self.lock = threading.Lock()
    
    def get_circuit_breaker(self, name: str, config: Optional[CircuitBreakerConfig] = None) -> CircuitBreaker:
        """Get or create a circuit breaker"""
        if name not in self.circuit_breakers:
            if config is None:
                config = CircuitBreakerConfig()
            self.circuit_breakers[name] = CircuitBreaker(config)
        return self.circuit_breakers[name]
    
    def record_error(self, error_type: str, error: Exception, context: Dict = None):
        """Record error statistics"""
        with self.lock:
            if error_type not in self.error_stats:
                self.error_stats[error_type] = {
                    'count': 0,
                    'last_occurrence': None,
                    'errors': []
                }
            
            stats = self.error_stats[error_type]
            stats['count'] += 1
            stats['last_occurrence'] = time.time()
            stats['errors'].append({
                'timestamp': time.time(),
                'error': str(error),
                'context': context or {}
            })
            
            # Keep only last 100 errors
            if len(stats['errors']) > 100:
                stats['errors'] = stats['errors'][-100:]
    
    def get_error_stats(self) -> Dict[str, Dict]:
        """Get error statistics"""
        with self.lock:
            return self.error_stats.copy()
    
    def get_circuit_breaker_stats(self) -> Dict[str, Dict]:
        """Get circuit breaker statistics"""
        return {name: cb.get_status() for name, cb in self.circuit_breakers.items()}
    
    def reset_circuit_breaker(self, name: str):
        """Reset a circuit breaker"""
        if name in self.circuit_breakers:
            with self.circuit_breakers[name].lock:
                self.circuit_breakers[name].state = CircuitState.CLOSED
                self.circuit_breakers[name].failure_count = 0
                self.circuit_breakers[name].last_failure_time = None
            logger.info(f"Circuit breaker '{name}' reset")

# Global error handler instance
error_handler = ErrorHandler()

def handle_tts_errors(func: Callable) -> Callable:
    """Decorator to handle TTS-specific errors"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_type = type(e).__name__
            error_handler.record_error(error_type, e, {
                'function': func.__name__,
                'args': str(args),
                'kwargs': str(kwargs)
            })
            raise
    return wrapper

def safe_tts_call(func: Callable, *args, **kwargs) -> Any:
    """Safely call TTS function with error handling"""
    circuit_breaker = error_handler.get_circuit_breaker('tts_api')
    
    @retry_with_backoff(RetryConfig(max_attempts=3, base_delay=1.0))
    @circuit_breaker
    @handle_tts_errors
    def safe_func():
        return func(*args, **kwargs)
    
    return safe_func()
