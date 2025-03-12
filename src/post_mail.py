import re
import time
import requests

MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds
REQUEST_TIMEOUT = 7  # seconds

def extract_email(text: str):
    """Deprecated"""
    email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    matches = re.findall(email_regex, text)
    unique_emails = list(set(matches))
    if 'info@woodxel.com' in unique_emails:
        unique_emails.remove('info@woodxel.com')
    return unique_emails if unique_emails else []

def send_email_to_api(email: str) -> bool:
    """Send email to WordPress endpoint with error handling and retries"""
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post("https://store.woodxel.com/wp-json/custom/v1/save-email",
                                    json={"email": email}, timeout=REQUEST_TIMEOUT)
            if response.status_code == 200:
                return True
                
            # Retry on server errors
            if 500 <= response.status_code < 600:
                raise requests.exceptions.RetryError(f"Server error: {response.status_code}")
            return False
        except requests.RequestException as e:
            if attempt == MAX_RETRIES - 1:
                print(f"Email API failed after {MAX_RETRIES} attempts: {str(e)}")
                return False
            time.sleep(RETRY_DELAY * (attempt + 1))
    return False