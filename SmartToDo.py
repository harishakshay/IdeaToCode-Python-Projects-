	import re
from datetime import datetime, timedelta

try:
    import dateparser
except ImportError:
    dateparser = None

class SmartToDoParser:
    """Parse natural language into structured to‑do items."""
    def __init__(self):
        self.pattern = re.compile(r'(?P<action>.+?)(?:\s+by\s+(?P<date>.+))?$', re.IGNORECASE)

    def _parse_date(self, text):
        if not text:
            return None
        if dateparser:
            dt = dateparser.parse(text, settings={'RETURN_AS_TIMEZONE_AWARE': False})
            return dt
        lowered = text.lower()
        if 'tomorrow' in lowered:
            return datetime.now() + timedelta(days=1)
        if 'today' in lowered:
            return datetime.now()
        return None

    def parse(self, text):
        """Return a list with a single to‑do dict for the given text."""
        match = self.pattern.match(text.strip())
        if not match:
            return []
        action = match.group('action').strip()
        raw_date = match.group('date')
        due = self._parse_date(raw_date)
        todo = {
            'title': action,
            'due': due.isoformat() if due else None
        }
        return [todo]

def main():
    parser = SmartToDoParser()
    samples = [
        "Buy milk by tomorrow evening",
        "Finish the quarterly report by 2024-05-01",
        "Call Alice"
    ]
    for s in samples:
        todos = parser.parse(s)
        print(f"Input: {s}")
        for t in todos:
            print(f"  -> {t}")
        print()

if __name__ == "__main__":
    main()
