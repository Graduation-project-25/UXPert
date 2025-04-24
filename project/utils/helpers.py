import json
import re
from json.decoder import JSONDecodeError

def clean_prefix(text):
    """Remove numeric prefixes like '0:' or '1:' from text."""
    return re.sub(r'^\d+:\s*', '', str(text))

def extract_json_from_response(text):
    """Robust JSON extraction that handles truncated responses"""
    text = text.strip()
    
    # First try parsing directly
    try:
        return json.loads(text)
    except JSONDecodeError as e:
        pass
        
    # Try to find complete JSON object
    try:
        json_str = re.search(r'\{.*\}', text, re.DOTALL)
        if json_str:
            open_braces = json_str.group().count('{')
            close_braces = json_str.group().count('}')
            
            if open_braces > close_braces:
                fixed_json = json_str.group() + '}' * (open_braces - close_braces)
                return json.loads(fixed_json)
            elif close_braces > open_braces:
                fixed_json = '{' * (close_braces - open_braces) + json_str.group()
                return json.loads(fixed_json)
            return json.loads(json_str.group())
    except json.JSONDecodeError:
        pass
        
    # Try extracting from markdown code blocks
    try:
        json_match = re.search(r'```(?:json)?\n(.*?)\n```', text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1))
    except JSONDecodeError:
        pass
        
    # Final fallback - try parsing as much as possible
    try:
        for i in range(len(text), 0, -1):
            try:
                return json.loads(text[:i])
            except JSONDecodeError:
                continue
    except Exception:
        pass
        
    raise ValueError(f"Could not extract valid JSON from response. Content:\n{text[:500]}...")