"""
Yahoo Fantasy Sports API Exception Classes
Comprehensive error handling for Yahoo API operations
"""

from typing import Optional, Dict, Any


class YahooFantasyError(Exception):
    """Base exception for Yahoo Fantasy API errors"""
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class YahooAuthenticationError(YahooFantasyError):
    """Authentication related errors"""
    
    def __init__(self, message: str = "Authentication failed", **kwargs):
        if 'error_code' not in kwargs:
            kwargs['error_code'] = "AUTH_ERROR"
        super().__init__(message, **kwargs)


class YahooTokenExpiredError(YahooAuthenticationError):
    """Access token has expired"""
    
    def __init__(self, message: str = "Access token has expired", **kwargs):
        kwargs['error_code'] = "TOKEN_EXPIRED"
        super().__init__(message, **kwargs)


class YahooInvalidTokenError(YahooAuthenticationError):
    """Invalid or malformed token"""
    
    def __init__(self, message: str = "Invalid access token", **kwargs):
        kwargs['error_code'] = "INVALID_TOKEN"
        super().__init__(message, **kwargs)


class YahooAuthorizationError(YahooFantasyError):
    """Authorization related errors (403)"""
    
    def __init__(self, message: str = "Not authorized to access this resource", **kwargs):
        super().__init__(message, error_code="AUTHORIZATION_ERROR", **kwargs)


class YahooResourceNotFoundError(YahooFantasyError):
    """Resource not found (404)"""
    
    def __init__(self, resource_type: str, resource_id: str, **kwargs):
        message = f"{resource_type} with ID {resource_id} not found"
        super().__init__(message, error_code="NOT_FOUND", **kwargs)
        self.resource_type = resource_type
        self.resource_id = resource_id


class YahooRateLimitError(YahooFantasyError):
    """Rate limit exceeded"""
    
    def __init__(self, retry_after: Optional[int] = None, **kwargs):
        message = "Rate limit exceeded"
        if retry_after:
            message += f". Retry after {retry_after} seconds"
        super().__init__(message, error_code="RATE_LIMIT", **kwargs)
        self.retry_after = retry_after


class YahooServerError(YahooFantasyError):
    """Server error (5xx)"""
    
    def __init__(self, status_code: int, message: str = "Yahoo server error", **kwargs):
        super().__init__(message, error_code="SERVER_ERROR", **kwargs)
        self.status_code = status_code


class YahooBadRequestError(YahooFantasyError):
    """Bad request (400)"""
    
    def __init__(self, message: str = "Invalid request parameters", **kwargs):
        super().__init__(message, error_code="BAD_REQUEST", **kwargs)


class YahooInvalidParameterError(YahooBadRequestError):
    """Invalid parameter in request"""
    
    def __init__(self, parameter: str, value: Any, message: Optional[str] = None, **kwargs):
        if not message:
            message = f"Invalid value '{value}' for parameter '{parameter}'"
        super().__init__(message, **kwargs)
        self.parameter = parameter
        self.value = value


class YahooTransactionError(YahooFantasyError):
    """Transaction related errors"""
    
    def __init__(self, message: str = "Transaction failed", **kwargs):
        if 'error_code' not in kwargs:
            kwargs['error_code'] = "TRANSACTION_ERROR"
        super().__init__(message, **kwargs)


class YahooInvalidTransactionError(YahooTransactionError):
    """Invalid transaction attempt"""
    
    def __init__(self, reason: str, **kwargs):
        message = f"Invalid transaction: {reason}"
        kwargs['error_code'] = "INVALID_TRANSACTION"
        super().__init__(message, **kwargs)
        self.reason = reason


class YahooRosterError(YahooFantasyError):
    """Roster related errors"""
    
    def __init__(self, message: str = "Roster operation failed", **kwargs):
        if 'error_code' not in kwargs:
            kwargs['error_code'] = "ROSTER_ERROR"
        super().__init__(message, **kwargs)


class YahooInvalidRosterPositionError(YahooRosterError):
    """Invalid roster position"""
    
    def __init__(self, player_name: str, position: str, **kwargs):
        message = f"Cannot place {player_name} in position {position}"
        kwargs['error_code'] = "INVALID_POSITION"
        super().__init__(message, **kwargs)
        self.player_name = player_name
        self.position = position


class YahooNetworkError(YahooFantasyError):
    """Network related errors"""
    
    def __init__(self, message: str = "Network error occurred", **kwargs):
        if 'error_code' not in kwargs:
            kwargs['error_code'] = "NETWORK_ERROR"
        super().__init__(message, **kwargs)


class YahooTimeoutError(YahooNetworkError):
    """Request timeout"""
    
    def __init__(self, timeout: int, **kwargs):
        message = f"Request timed out after {timeout} seconds"
        kwargs['error_code'] = "TIMEOUT"
        super().__init__(message, **kwargs)
        self.timeout = timeout


class YahooParsingError(YahooFantasyError):
    """Error parsing API response"""
    
    def __init__(self, message: str = "Failed to parse API response", **kwargs):
        super().__init__(message, error_code="PARSING_ERROR", **kwargs)


class YahooInvalidResponseError(YahooParsingError):
    """Invalid or unexpected response format"""
    
    def __init__(self, expected: str, received: str, **kwargs):
        message = f"Expected {expected} in response, but received {received}"
        super().__init__(message, **kwargs)
        self.expected = expected
        self.received = received


class YahooConfigurationError(YahooFantasyError):
    """Configuration related errors"""
    
    def __init__(self, message: str = "Invalid configuration", **kwargs):
        super().__init__(message, error_code="CONFIG_ERROR", **kwargs)


class YahooMissingCredentialsError(YahooConfigurationError):
    """Missing required credentials"""
    
    def __init__(self, credential: str, **kwargs):
        message = f"Missing required credential: {credential}"
        super().__init__(message, **kwargs)
        self.credential = credential


# Error handler utility
class YahooErrorHandler:
    """Utility class for handling Yahoo API errors"""
    
    @staticmethod
    def handle_http_error(status_code: int, response_text: str, url: str) -> YahooFantasyError:
        """Convert HTTP error to appropriate exception"""
        
        # Try to extract error details from response
        error_details = {}
        error_message = f"HTTP {status_code} error"
        
        try:
            import json
            response_data = json.loads(response_text)
            if 'error' in response_data:
                error_details = response_data['error']
                error_message = error_details.get('description', error_message)
        except:
            # If we can't parse JSON, use raw text
            error_message = response_text[:200] if response_text else error_message
            
        # Map status codes to exceptions
        if status_code == 401:
            # Check if it's specifically a token expiration
            if 'token' in error_message.lower() and 'expired' in error_message.lower():
                return YahooTokenExpiredError(details={'url': url, 'response': error_details})
            return YahooAuthenticationError(error_message, details={'url': url, 'response': error_details})
            
        elif status_code == 403:
            return YahooAuthorizationError(error_message, details={'url': url, 'response': error_details})
            
        elif status_code == 404:
            # Try to extract resource info from URL
            parts = url.split('/')
            resource_type = "Resource"
            resource_id = "unknown"
            
            if len(parts) >= 2:
                resource_type = parts[-2]
                resource_id = parts[-1].split('?')[0]
                
            return YahooResourceNotFoundError(resource_type, resource_id, details={'url': url})
            
        elif status_code == 429:
            # Try to get retry-after header
            retry_after = error_details.get('retry_after')
            return YahooRateLimitError(retry_after, details={'url': url, 'response': error_details})
            
        elif status_code == 400:
            return YahooBadRequestError(error_message, details={'url': url, 'response': error_details})
            
        elif 500 <= status_code < 600:
            return YahooServerError(status_code, error_message, details={'url': url, 'response': error_details})
            
        else:
            return YahooFantasyError(
                f"Unexpected HTTP {status_code}: {error_message}",
                error_code=f"HTTP_{status_code}",
                details={'url': url, 'response': error_details}
            )
            
    @staticmethod
    def handle_transaction_error(error_type: str, details: Dict[str, Any]) -> YahooTransactionError:
        """Handle transaction-specific errors"""
        
        error_map = {
            'player_locked': "Player is locked and cannot be dropped",
            'player_undroppable': "Player is undroppable",
            'roster_full': "Roster position is full",
            'invalid_position': "Player is not eligible for this position",
            'waiver_priority': "Insufficient waiver priority",
            'faab_insufficient': "Insufficient FAAB budget",
            'trade_deadline': "Trade deadline has passed",
            'trade_invalid': "Invalid trade proposal",
            'player_unavailable': "Player is not available",
            'duplicate_player': "Player is already on your roster"
        }
        
        reason = error_map.get(error_type, error_type)
        return YahooInvalidTransactionError(reason, details=details)
        
    @staticmethod
    def is_retryable(error: YahooFantasyError) -> bool:
        """Check if error is retryable"""
        
        # Rate limit errors are retryable after delay
        if isinstance(error, YahooRateLimitError):
            return True
            
        # Server errors are often temporary
        if isinstance(error, YahooServerError):
            return error.status_code not in [501, 505]  # Not implemented, HTTP version not supported
            
        # Network timeouts are retryable
        if isinstance(error, YahooTimeoutError):
            return True
            
        # Token expiration requires refresh, not retry
        if isinstance(error, YahooTokenExpiredError):
            return False
            
        # Most other errors are not retryable
        return False