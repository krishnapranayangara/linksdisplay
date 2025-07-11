"""
Custom exceptions for the Link Organizer application.
"""


class ValidationError(Exception):
    """
    Raised when data validation fails.
    
    This exception is used when input data doesn't meet
    the required format or constraints.
    """
    pass


class DatabaseError(Exception):
    """
    Raised when database operations fail.
    
    This exception is used when database queries or
    operations encounter errors.
    """
    pass


class NotFoundError(Exception):
    """
    Raised when a requested resource is not found.
    
    This exception is used when trying to retrieve
    a resource that doesn't exist in the database.
    """
    pass


class ConflictError(Exception):
    """
    Raised when there's a conflict with existing data.
    
    This exception is used when trying to create
    a resource that already exists or conflicts with
    existing data.
    """
    pass


class AuthenticationError(Exception):
    """
    Raised when authentication fails.
    
    This exception is used when user authentication
    or authorization fails.
    """
    pass


class RateLimitError(Exception):
    """
    Raised when rate limiting is exceeded.
    
    This exception is used when API rate limits
    are exceeded.
    """
    pass 