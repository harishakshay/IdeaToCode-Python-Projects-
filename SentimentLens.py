	import argparse
import json
import sys
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

def ensure_vader():
    """Ensure the VADER lexicon is downloaded."""
    try:
        nltk.data.find('sentiment/vader_lexicon.zip')
    except LookupError:
        nltk.download('vader_lexicon')

def analyze_sentiment(text, analyzer):
    """Return sentiment label and scores for a given text."""
    scores = analyzer.polarity_scores(text)
    compound = scores['compound']
    if compound >= 0.05:
        label = 'positive'
    elif compound <= -0.05:
        label = 'negative'
    else:
        label = 'neutral'
    return {'text': text, 'label': label, 'scores': scores}

def load_texts_from_file(path):
    """Read non‑empty lines from a file as separate texts."""
    with open(path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def main():
    parser = argparse.ArgumentParser(description='SentimentLens - simple sentiment analysis using VADER')
    parser.add_argument('-f', '--file', help='Path to a text file with one review/tweet per line')
    args = parser.parse_args()
    ensure_vader()
    analyzer = SentimentIntensityAnalyzer()
    if args.file:
        texts = load_texts_from_file(args.file)
    else:
        # Minimal inline sample data
        texts = [
            "I love this product! It works great.",
            "Terrible experience, will not buy again.",
            "It's okay, nothing special."
        ]
    results = [analyze_sentiment(t, analyzer) for t in texts]
    print(json.dumps(results, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
