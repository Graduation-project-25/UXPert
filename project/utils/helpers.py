import json
import re
from json.decoder import JSONDecodeError

def clean_prefix(text):
    """Remove numeric prefixes like '0:' or '1:' from text."""
    return re.sub(r'^\d+:\s*', '', str(text))

def extract_json_from_response(text):
    """Robust JSON extraction that handles truncated responses"""
    text = text.strip()
    print(f"Attempting to parse JSON of length: {len(text)}")

    # First try parsing directly
    try:
        return json.loads(text)
    except JSONDecodeError as e:
        print(f"Direct JSON parse failed: {str(e)}")

    # Try to find complete JSON object
    try:
        json_str = re.search(r'\{.*\}', text, re.DOTALL)
        if json_str:
            json_text = json_str.group()
            open_braces = json_text.count('{')
            close_braces = json_text.count('}')
            
            # Attempt to fix unbalanced braces
            if open_braces > close_braces:
                json_text += '}' * (open_braces - close_braces)
            elif close_braces > open_braces:
                json_text = '{' * (close_braces - open_braces) + json_text
            
            try:
                return json.loads(json_text)
            except JSONDecodeError as e:
                print(f"Balanced JSON parse failed: {str(e)}")
    except Exception as e:
        print(f"Regex JSON extraction failed: {str(e)}")

    # Try extracting from markdown code blocks
    try:
        json_match = re.search(r'```(?:json)?\n(.*?)\n```', text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1))
    except JSONDecodeError as e:
        print(f"Markdown JSON parse failed: {str(e)}")

    # Fallback: Attempt to parse partial JSON
    try:
        for i in range(len(text), 0, -1):
            try:
                return json.loads(text[:i] + '}' * text[:i].count('{'))
            except JSONDecodeError:
                continue
    except Exception as e:
        print(f"Partial JSON parse failed: {str(e)}")

    # If all else fails, return a minimal valid JSON with error info
    error_json = {
        "status": "error",
        "message": "Failed to parse JSON response",
        "partial_content": text[:500] + "..." if len(text) > 500 else text
    }
    print(f"Returning fallback JSON: {json.dumps(error_json)[:100]}...")
    return error_json