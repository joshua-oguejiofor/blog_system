import re

import bleach

"""Best places to sanitize are user generated input"""
def sanitize_input_data(value):
    return bleach.clean(value, strip= True)
    



def valid_username(value: str) -> str:
        """Validate username format (allow letters, numbers or underscore)."""

        if not re.fullmatch(r"[A-Za-z0-9_]+", value):
            raise ValueError("Field for surname and other name must be letters, no sapce in between each name")
        
        return value.lower()



def format_field(value):
        if isinstance(value, str): #for all strings, avoide crash for integer
            return value.strip().lower()
        return value


    