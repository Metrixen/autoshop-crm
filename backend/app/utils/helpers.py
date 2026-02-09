import secrets
import string
import phonenumbers
from typing import Optional


def generate_password(length: int = 8) -> str:
    """Generate a random password"""
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password


def validate_phone_number(phone: str, country_code: str = "BG") -> Optional[str]:
    """
    Validate and format phone number
    Returns formatted phone number or None if invalid
    """
    try:
        parsed = phonenumbers.parse(phone, country_code)
        if phonenumbers.is_valid_number(parsed):
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        return None
    except phonenumbers.NumberParseException:
        return None


def format_bulgarian_phone(phone: str) -> str:
    """
    Format Bulgarian phone number for display
    +359888123456 -> +359 888 123 456
    """
    if phone.startswith("+359"):
        return f"+359 {phone[4:7]} {phone[7:10]} {phone[10:]}"
    return phone
