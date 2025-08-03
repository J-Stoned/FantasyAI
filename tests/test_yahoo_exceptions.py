"""
Unit tests for Yahoo Fantasy API exception handling
"""

import pytest
from src.yahoo_wrapper.exceptions import (
    YahooFantasyError,
    YahooAuthenticationError,
    YahooTokenExpiredError,
    YahooInvalidTokenError,
    YahooAuthorizationError,
    YahooResourceNotFoundError,
    YahooRateLimitError,
    YahooServerError,
    YahooBadRequestError,
    YahooInvalidParameterError,
    YahooTransactionError,
    YahooInvalidTransactionError,
    YahooRosterError,
    YahooInvalidRosterPositionError,
    YahooNetworkError,
    YahooTimeoutError,
    YahooParsingError,
    YahooInvalidResponseError,
    YahooConfigurationError,
    YahooMissingCredentialsError,
    YahooErrorHandler
)


class TestYahooExceptions:
    """Test Yahoo Fantasy API exceptions"""
    
    def test_base_exception(self):
        """Test base YahooFantasyError"""
        error = YahooFantasyError("Test error", error_code="TEST_ERROR", details={"key": "value"})
        
        assert str(error) == "Test error"
        assert error.error_code == "TEST_ERROR"
        assert error.details["key"] == "value"
    
    def test_authentication_errors(self):
        """Test authentication-related errors"""
        # Base auth error
        error = YahooAuthenticationError()
        assert error.error_code == "AUTH_ERROR"
        
        # Token expired
        error = YahooTokenExpiredError()
        assert error.error_code == "TOKEN_EXPIRED"
        assert "expired" in str(error).lower()
        
        # Invalid token
        error = YahooInvalidTokenError()
        assert error.error_code == "INVALID_TOKEN"
        assert "invalid" in str(error).lower()
    
    def test_authorization_error(self):
        """Test authorization error"""
        error = YahooAuthorizationError()
        assert error.error_code == "AUTHORIZATION_ERROR"
        assert "not authorized" in str(error).lower()
    
    def test_resource_not_found_error(self):
        """Test resource not found error"""
        error = YahooResourceNotFoundError("league", "nfl.l.12345")
        
        assert error.error_code == "NOT_FOUND"
        assert error.resource_type == "league"
        assert error.resource_id == "nfl.l.12345"
        assert "league with ID nfl.l.12345 not found" in str(error)
    
    def test_rate_limit_error(self):
        """Test rate limit error"""
        # Without retry_after
        error = YahooRateLimitError()
        assert error.error_code == "RATE_LIMIT"
        assert error.retry_after is None
        
        # With retry_after
        error = YahooRateLimitError(retry_after=60)
        assert error.retry_after == 60
        assert "Retry after 60 seconds" in str(error)
    
    def test_server_error(self):
        """Test server error"""
        error = YahooServerError(500, "Internal server error")
        
        assert error.error_code == "SERVER_ERROR"
        assert error.status_code == 500
        assert "Internal server error" in str(error)
    
    def test_bad_request_errors(self):
        """Test bad request errors"""
        # Base bad request
        error = YahooBadRequestError()
        assert error.error_code == "BAD_REQUEST"
        
        # Invalid parameter
        error = YahooInvalidParameterError("position", "XYZ")
        assert error.parameter == "position"
        assert error.value == "XYZ"
        assert "Invalid value 'XYZ' for parameter 'position'" in str(error)
    
    def test_transaction_errors(self):
        """Test transaction-related errors"""
        # Base transaction error
        error = YahooTransactionError()
        assert error.error_code == "TRANSACTION_ERROR"
        
        # Invalid transaction
        error = YahooInvalidTransactionError("Player is undroppable")
        assert error.reason == "Player is undroppable"
        assert "Invalid transaction: Player is undroppable" in str(error)
    
    def test_roster_errors(self):
        """Test roster-related errors"""
        # Base roster error
        error = YahooRosterError()
        assert error.error_code == "ROSTER_ERROR"
        
        # Invalid roster position
        error = YahooInvalidRosterPositionError("Patrick Mahomes", "RB")
        assert error.player_name == "Patrick Mahomes"
        assert error.position == "RB"
        assert "Cannot place Patrick Mahomes in position RB" in str(error)
    
    def test_network_errors(self):
        """Test network-related errors"""
        # Base network error
        error = YahooNetworkError()
        assert error.error_code == "NETWORK_ERROR"
        
        # Timeout error
        error = YahooTimeoutError(30)
        assert error.error_code == "TIMEOUT"
        assert error.timeout == 30
        assert "Request timed out after 30 seconds" in str(error)
    
    def test_parsing_errors(self):
        """Test parsing-related errors"""
        # Base parsing error
        error = YahooParsingError()
        assert error.error_code == "PARSING_ERROR"
        
        # Invalid response format
        error = YahooInvalidResponseError("dict", "list")
        assert error.expected == "dict"
        assert error.received == "list"
        assert "Expected dict in response, but received list" in str(error)
    
    def test_configuration_errors(self):
        """Test configuration-related errors"""
        # Base config error
        error = YahooConfigurationError()
        assert error.error_code == "CONFIG_ERROR"
        
        # Missing credentials
        error = YahooMissingCredentialsError("client_id")
        assert error.credential == "client_id"
        assert "Missing required credential: client_id" in str(error)


class TestYahooErrorHandler:
    """Test Yahoo error handler utility"""
    
    def test_handle_401_token_expired(self):
        """Test handling 401 with token expiration"""
        error = YahooErrorHandler.handle_http_error(
            401,
            '{"error": {"description": "Token has expired"}}',
            "https://api.yahoo.com/test"
        )
        
        assert isinstance(error, YahooTokenExpiredError)
        assert error.details["url"] == "https://api.yahoo.com/test"
    
    def test_handle_401_general(self):
        """Test handling general 401 error"""
        error = YahooErrorHandler.handle_http_error(
            401,
            '{"error": {"description": "Unauthorized"}}',
            "https://api.yahoo.com/test"
        )
        
        assert isinstance(error, YahooAuthenticationError)
        assert not isinstance(error, YahooTokenExpiredError)
    
    def test_handle_403(self):
        """Test handling 403 forbidden"""
        error = YahooErrorHandler.handle_http_error(
            403,
            '{"error": {"description": "Forbidden"}}',
            "https://api.yahoo.com/test"
        )
        
        assert isinstance(error, YahooAuthorizationError)
    
    def test_handle_404(self):
        """Test handling 404 not found"""
        error = YahooErrorHandler.handle_http_error(
            404,
            "",
            "https://api.yahoo.com/league/nfl.l.12345"
        )
        
        assert isinstance(error, YahooResourceNotFoundError)
        assert error.resource_type == "league"
        assert error.resource_id == "nfl.l.12345"
    
    def test_handle_429(self):
        """Test handling 429 rate limit"""
        error = YahooErrorHandler.handle_http_error(
            429,
            '{"error": {"retry_after": 60}}',
            "https://api.yahoo.com/test"
        )
        
        assert isinstance(error, YahooRateLimitError)
        assert error.retry_after == 60
    
    def test_handle_400(self):
        """Test handling 400 bad request"""
        error = YahooErrorHandler.handle_http_error(
            400,
            '{"error": {"description": "Invalid parameter"}}',
            "https://api.yahoo.com/test"
        )
        
        assert isinstance(error, YahooBadRequestError)
    
    def test_handle_500_errors(self):
        """Test handling 5xx server errors"""
        # 500
        error = YahooErrorHandler.handle_http_error(
            500,
            "Internal server error",
            "https://api.yahoo.com/test"
        )
        
        assert isinstance(error, YahooServerError)
        assert error.status_code == 500
        
        # 503
        error = YahooErrorHandler.handle_http_error(
            503,
            "Service unavailable",
            "https://api.yahoo.com/test"
        )
        
        assert isinstance(error, YahooServerError)
        assert error.status_code == 503
    
    def test_handle_unknown_error(self):
        """Test handling unknown HTTP error"""
        error = YahooErrorHandler.handle_http_error(
            418,
            "I'm a teapot",
            "https://api.yahoo.com/test"
        )
        
        assert isinstance(error, YahooFantasyError)
        assert error.error_code == "HTTP_418"
    
    def test_handle_transaction_errors(self):
        """Test handling transaction-specific errors"""
        # Player locked
        error = YahooErrorHandler.handle_transaction_error(
            "player_locked",
            {"player_id": "12345"}
        )
        
        assert isinstance(error, YahooInvalidTransactionError)
        assert "locked" in error.reason
        
        # Insufficient FAAB
        error = YahooErrorHandler.handle_transaction_error(
            "faab_insufficient",
            {"bid": 50, "balance": 25}
        )
        
        assert isinstance(error, YahooInvalidTransactionError)
        assert "FAAB" in error.reason
        
        # Unknown error type
        error = YahooErrorHandler.handle_transaction_error(
            "unknown_error",
            {}
        )
        
        assert isinstance(error, YahooInvalidTransactionError)
        assert error.reason == "unknown_error"
    
    def test_is_retryable(self):
        """Test retryable error detection"""
        # Rate limit - retryable
        error = YahooRateLimitError()
        assert YahooErrorHandler.is_retryable(error) is True
        
        # Server error - retryable
        error = YahooServerError(500)
        assert YahooErrorHandler.is_retryable(error) is True
        
        # Not implemented - not retryable
        error = YahooServerError(501)
        assert YahooErrorHandler.is_retryable(error) is False
        
        # Timeout - retryable
        error = YahooTimeoutError(30)
        assert YahooErrorHandler.is_retryable(error) is True
        
        # Token expired - not retryable (needs refresh)
        error = YahooTokenExpiredError()
        assert YahooErrorHandler.is_retryable(error) is False
        
        # Bad request - not retryable
        error = YahooBadRequestError()
        assert YahooErrorHandler.is_retryable(error) is False
    
    def test_error_with_non_json_response(self):
        """Test error handling with non-JSON response"""
        error = YahooErrorHandler.handle_http_error(
            500,
            "<html><body>Server Error</body></html>",
            "https://api.yahoo.com/test"
        )
        
        assert isinstance(error, YahooServerError)
        assert "<html>" in error.message


if __name__ == "__main__":
    pytest.main([__file__, "-v"])