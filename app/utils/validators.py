from datetime import datetime

def validate_string(value, field_name, max_length, allow_empty=False):
    if not isinstance(value, str):
        return False, f"{field_name} must be a string"
    if not allow_empty and not value.strip():
        return False, f"{field_name} cannot be empty"
    if len(value) > max_length:
        return False, f"{field_name} exceeds maximum length of {max_length}"
    return True, ""

def validate_integer(value, field_name, min_value=None):
    try:
        val = int(value)
        if min_value is not None and val < min_value:
            return False, f"{field_name} must be at least {min_value}"
        return True, ""
    except (ValueError, TypeError):
        return False, f"{field_name} must be a valid integer"

def validate_datetime(value, field_name):
    try:
        datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        return True, ""
    except (ValueError, TypeError):
        return False, f"{field_name} must be in format YYYY-MM-DD HH:MM:SS"