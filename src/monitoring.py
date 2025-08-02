"""
Production Monitoring for Fantasy AI
Elite developers monitor everything
"""

import time
import logging
from datetime import datetime
from typing import Dict, Any
import json
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MetricsCollector:
    """Collect and track application metrics"""
    
    def __init__(self):
        self.metrics = {
            "oauth_attempts": 0,
            "oauth_success": 0,
            "oauth_failures": 0,
            "api_requests": 0,
            "api_errors": 0,
            "response_times": [],
            "active_users": set(),
            "daily_stats": {}
        }
    
    def track_oauth_attempt(self, success: bool, user_id: str = None):
        """Track OAuth login attempts"""
        self.metrics["oauth_attempts"] += 1
        
        if success:
            self.metrics["oauth_success"] += 1
            if user_id:
                self.metrics["active_users"].add(user_id)
        else:
            self.metrics["oauth_failures"] += 1
        
        logger.info(f"OAuth attempt: {'success' if success else 'failure'}")
    
    def track_api_request(self, endpoint: str, response_time: float, status_code: int):
        """Track API request metrics"""
        self.metrics["api_requests"] += 1
        self.metrics["response_times"].append(response_time)
        
        if status_code >= 400:
            self.metrics["api_errors"] += 1
        
        # Keep only last 1000 response times
        if len(self.metrics["response_times"]) > 1000:
            self.metrics["response_times"] = self.metrics["response_times"][-1000:]
        
        logger.info(f"API request to {endpoint}: {status_code} in {response_time:.2f}ms")
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get current metrics summary"""
        avg_response_time = (
            sum(self.metrics["response_times"]) / len(self.metrics["response_times"])
            if self.metrics["response_times"] else 0
        )
        
        return {
            "oauth_success_rate": (
                self.metrics["oauth_success"] / self.metrics["oauth_attempts"] * 100
                if self.metrics["oauth_attempts"] > 0 else 0
            ),
            "total_api_requests": self.metrics["api_requests"],
            "api_error_rate": (
                self.metrics["api_errors"] / self.metrics["api_requests"] * 100
                if self.metrics["api_requests"] > 0 else 0
            ),
            "avg_response_time_ms": avg_response_time,
            "active_users_count": len(self.metrics["active_users"]),
            "uptime_hours": (time.time() - startup_time) / 3600
        }
    
    def export_metrics(self, filepath: str = "metrics.json"):
        """Export metrics to file"""
        with open(filepath, 'w') as f:
            json.dump(self.get_metrics_summary(), f, indent=2)

# Global metrics collector
metrics = MetricsCollector()
startup_time = time.time()

# Middleware for FastAPI
from fastapi import Request
import time as time_module

async def metrics_middleware(request: Request, call_next):
    """Track all API requests"""
    start_time = time_module.time()
    
    response = await call_next(request)
    
    process_time = (time_module.time() - start_time) * 1000  # Convert to ms
    metrics.track_api_request(
        endpoint=request.url.path,
        response_time=process_time,
        status_code=response.status_code
    )
    
    # Add custom headers
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-Server-Name"] = "fantasy-ai-production"
    
    return response

# Health check endpoint data
def get_health_status():
    """Get application health status"""
    metrics_summary = metrics.get_metrics_summary()
    
    # Determine health status
    if metrics_summary["api_error_rate"] > 10:
        status = "degraded"
    elif metrics_summary["avg_response_time_ms"] > 1000:
        status = "slow"
    else:
        status = "healthy"
    
    return {
        "status": status,
        "timestamp": datetime.utcnow().isoformat(),
        "metrics": metrics_summary,
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "environment": os.getenv("ENVIRONMENT", "development")
    }