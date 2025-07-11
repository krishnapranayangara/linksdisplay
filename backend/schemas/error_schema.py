"""
Marshmallow schemas for Error model serialization and validation.
"""
from marshmallow import Schema, fields, validate


class ErrorSchema(Schema):
    """
    Schema for Error model serialization.
    
    This schema handles the conversion of Error model instances
    to and from JSON for API responses.
    """
    id = fields.Int(dump_only=True)
    method = fields.Str(required=True, validate=validate.OneOf(['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS']))
    endpoint = fields.Str(required=True)
    request_data = fields.Dict(allow_none=True)
    request_params = fields.Dict(allow_none=True)
    request_headers = fields.Dict(allow_none=True)
    client_ip = fields.Str(allow_none=True)
    user_agent = fields.Str(allow_none=True)
    status_code = fields.Int(required=True, validate=validate.Range(min=100, max=599))
    response_data = fields.Dict(allow_none=True)
    error_message = fields.Str(allow_none=True)
    error_type = fields.Str(allow_none=True)
    request_time = fields.DateTime(dump_only=True)
    response_time = fields.DateTime(allow_none=True)
    duration_ms = fields.Int(allow_none=True, validate=validate.Range(min=0))
    session_id = fields.Str(allow_none=True)
    user_id = fields.Int(allow_none=True)


class ErrorListSchema(Schema):
    """
    Schema for listing multiple error logs.
    """
    errors = fields.Nested(ErrorSchema, many=True)
    total = fields.Int()
    page = fields.Int()
    per_page = fields.Int()


class ErrorFilterSchema(Schema):
    """
    Schema for filtering error logs.
    """
    method = fields.Str(validate=validate.OneOf(['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS']))
    endpoint = fields.Str()
    status_code = fields.Int(validate=validate.Range(min=100, max=599))
    error_type = fields.Str()
    start_date = fields.DateTime()
    end_date = fields.DateTime()
    page = fields.Int(validate=validate.Range(min=1), missing=1)
    per_page = fields.Int(validate=validate.Range(min=1, max=100), missing=50) 