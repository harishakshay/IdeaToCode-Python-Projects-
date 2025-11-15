	import re
import datetime
from collections import Counter, defaultdict

# Minimal stopword list for demonstration
STOPWORDS = {
    "the", "and", "for", "with", "that", "this", "from", "are", "was", "were",
    "is", "in", "on", "at", "by", "to", "a", "an", "of", "or", "as", "it",
    "i", "you", "we", "they", "he", "she", "but", "not", "be", "have", "has"
}

def preprocess(text):
    """Lowercase, extract alphabetic words longer than one character, remove stopwords."""
    text = text.lower()
    words = re.findall(r"\b[a-z]{2,}\b", text)
    return [w for w in words if w not in STOPWORDS]

def aggregate_by_day(posts):
    """Group word counts by posting date (ISO 8601 timestamp expected)."""
    day_counts = defaultdict(Counter)
    for p in posts:
        dt = datetime.datetime.fromisoformat(p["timestamp"])
        day = dt.date()
        words = preprocess(p["text"])
        day_counts[day].update(words)
    return day_counts

def compute_trends(day_counts, top_n=5, min_count=2, ratio_threshold=1.5):
    """Identify terms whose frequency increased sharply compared to the previous day."""
    if len(day_counts) < 2:
        return []
    sorted_days = sorted(day_counts.keys())
    recent = day_counts[sorted_days[-1]]
    previous = day_counts[sorted_days[-2]]
    trends = []
    for term, cnt in recent.items():
        if cnt < min_count:
            continue
        prev_cnt = previous.get(term, 0)
        ratio = cnt / (prev_cnt + 1)  # +1 avoids division by zero
        if ratio >= ratio_threshold:
            trends.append((term, cnt, ratio))
    trends.sort(key=lambda x: x[2], reverse=True)
    return trends[:top_n]

def detect_trends(posts, top_n=5):
    """High‑level API: feed raw posts and get trending terms."""
    day_counts = aggregate_by_day(posts)
    return compute_trends(day_counts, top_n=top_n)

def main():
    # Minimal inline sample mimicking Twitter/Reddit posts
    sample_posts = [
        {"text": "Python is awesome! #coding", "timestamp": "2025-11-13T10:15:00"},
        {"text": "I love machine learning with Python.", "timestamp": "2025-11-13T12:30:00"},
        {"text": "Check out the new AI model release.", "timestamp": "2025-11-14T09:00:00"},
        {"text": "AI is transforming the industry.", "timestamp": "2025-11-14T11:45:00"},
        {"text": "Python libraries make data science easy.", "timestamp": "2025-11-14T14:20:00"},
        {"text": "Deep learning breakthroughs in AI.", "timestamp": "2025-11-14T16:05:00"},
        {"text": "Just tried a new Python package for NLP.", "timestamp": "2025-11-14T18:30:00"},
    ]
    trends = detect_trends(sample_posts, top_n=5)
    if trends:
        print("Trending terms:")
        for term, count, ratio in trends:
            print(f"{term}: count={count}, increase_factor={ratio:.2f}")
    else:
        print("No significant trends detected.")

if __name__ == "__main__":
    main()
