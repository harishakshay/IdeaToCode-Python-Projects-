	import re

class EmailSorter:
    def __init__(self, rules=None):
        # Default keyword rules for each category
        self.rules = rules or {
            "work": [r"meeting", r"project", r"deadline", r"client"],
            "promo": [r"sale", r"discount", r"offer", r"free"],
            "personal": [r"family", r"party", r"birthday", r"catch up"]
        }
        # Pre‑compile regex patterns for speed
        self.compiled = {cat: [re.compile(p, re.I) for p in pats] for cat, pats in self.rules.items()}

    def classify(self, email):
        """Return the category that best matches the email.
        email is a dict with 'subject' and 'body' keys.
        """
        text = f"{email.get('subject', '')} {email.get('body', '')}".lower()
        scores = {cat: 0 for cat in self.rules}
        for cat, patterns in self.compiled.items():
            for pat in patterns:
                if pat.search(text):
                    scores[cat] += 1
        # Choose category with highest score, fallback to 'uncategorized'
        best = max(scores, key=scores.get)
        return best if scores[best] > 0 else "uncategorized"

    def batch_classify(self, emails):
        return [{**email, "category": self.classify(email)} for email in emails]

def main():
    sample_emails = [
        {"subject": "Project deadline approaching", "body": "Please review the latest updates."},
        {"subject": "Huge discount on shoes!", "body": "Get 50% off today only."},
        {"subject": "Family reunion this weekend", "body": "Looking forward to seeing everyone."},
        {"subject": "Random newsletter", "body": "Just some news you might like."}
    ]
    sorter = EmailSorter()
    classified = sorter.batch_classify(sample_emails)
    for email in classified:
        print(f"Subject: {email['subject']}\nCategory: {email['category']}\n")

if __name__ == "__main__":
    main()
