	import os
import sys
import argparse
import textwrap
import re

try:
    import openai
except ImportError:
    openai = None

def _get_openai_api_key():
    """Retrieve OpenAI API key from environment variables."""
    return os.getenv("OPENAI_API_KEY")

def _review_with_openai(code: str) -> str:
    """Send code to OpenAI ChatCompletion and return suggestions.
    Raises RuntimeError if the library or API key is unavailable.
    """
    if openai is None:
        raise RuntimeError("OpenAI library not installed.")
    api_key = _get_openai_api_key()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable not set.")
    openai.api_key = api_key
    prompt = (
        "You are a Python code reviewer. Provide a concise list of improvements, "
        "style suggestions, and potential bugs for the following code. Return only "
        "the suggestions in plain text.\n\n```python\n{code}\n```"
    )
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=500,
    )
    return response.choices[0].message.content.strip()

def _heuristic_review(code: str) -> str:
    """Fallback reviewer that uses simple regex‑based heuristics."""
    suggestions = []
    if len(code) > 1000:
        suggestions.append("Consider splitting large file into modules.")
    if re.search(r'\bprint\s*\(', code):
        suggestions.append("Remove or replace print statements with logging.")
    if re.search(r'if\s+__name__\s*==\s*[\'\"]__main__[\'\"]\s*:', code) is None:
        suggestions.append("Add an entry‑point guard (if __name__ == '__main__') if script is executable.")
    functions = re.findall(r'def\s+(\w+)\s*\(.*?\):', code)
    for func in functions:
        # Check for a docstring directly after the function definition
        pattern = rf'def\s+{func}\s*\(.*?\):\s*\n\s+"""'
        if not re.search(pattern, code):
            suggestions.append(f"Add docstring to function '{func}'.")
    return "\n".join(suggestions) if suggestions else "No obvious issues detected."

def review_code(code: str) -> str:
    """Try OpenAI review first, fall back to heuristic if any error occurs."""
    try:
        return _review_with_openai(code)
    except Exception:
        return _heuristic_review(code)

def _load_code(path: str) -> str:
    """Read file content with UTF‑8 encoding."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def main():
    parser = argparse.ArgumentParser(description="AI‑powered Python code reviewer.")
    parser.add_argument("path", nargs="?", help="Path to Python file to review.")
    args = parser.parse_args()

    if args.path:
        if not os.path.isfile(args.path):
            print(f"Error: File '{args.path}' not found.", file=sys.stderr)
            sys.exit(1)
        code = _load_code(args.path)
    else:
        # Minimal inline example when no file is supplied
        code = textwrap.dedent('''
            def add(a, b):
                return a + b
            print(add(2, 3))
        ''')
        print("No file provided. Reviewing sample code.")

    print("=== Review ===")
    print(review_code(code))

if __name__ == "__main__":
    main()
