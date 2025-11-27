	import sys
import re
import logging
from collections import Counter
from typing import List, Tuple

# Third‑party imports – optional, with graceful fallback
try:
    from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
except ImportError:
    YouTubeTranscriptApi = None
    TranscriptsDisabled = Exception
    NoTranscriptFound = Exception

try:
    import nltk
    from nltk.corpus import stopwords
except ImportError:
    nltk = None
    stopwords = None

try:
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.decomposition import LatentDirichletAllocation
except ImportError:
    CountVectorizer = None
    LatentDirichletAllocation = None

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def ensure_nltk_resources() -> None:
    """Download required NLTK data if missing."""
    if nltk is None:
        logging.error("NLTK is not installed. Run 'pip install nltk' and retry.")
        sys.exit(1)
    try:
        stopwords.words('english')
    except LookupError:
        nltk.download('stopwords')

def fetch_captions(video_id: str) -> List[dict]:
    """Retrieve transcript entries for a YouTube video.

    Args:
        video_id: YouTube video identifier (e.g., 'dQw4w9WgXcQ')
    Returns:
        List of transcript dicts with 'text' and timestamps.
    """
    if YouTubeTranscriptApi is None:
        logging.error("youtube_transcript_api not installed. Run 'pip install youtube-transcript-api'.")
        sys.exit(1)
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        logging.info(f"Fetched {len(transcript)} caption segments.")
        return transcript
    except (TranscriptsDisabled, NoTranscriptFound) as e:
        logging.error(f"Captions unavailable for video {video_id}: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Failed to fetch captions: {e}")
        sys.exit(1)

def preprocess_text(text: str, stop_words: set) -> List[str]:
    """Tokenize, lower‑case, remove punctuation and stop‑words.

    Returns a list of clean tokens.
    """
    # Remove non‑alphabetic characters
    cleaned = re.sub(r"[^a-zA-Z\s]", " ", text)
    tokens = cleaned.lower().split()
    tokens = [t for t in tokens if t not in stop_words and len(t) > 1]
    return tokens

def get_word_frequencies(tokens: List[str]) -> Counter:
    """Count token occurrences."""
    return Counter(tokens)

def extract_topics(docs: List[str], n_topics: int = 3, n_top_words: int = 5) -> List[Tuple[int, List[str]]]:
    """Simple LDA topic extraction.

    Returns a list of (topic_index, top_words) tuples.
    """
    if CountVectorizer is None or LatentDirichletAllocation is None:
        logging.error("scikit-learn is required for topic modeling. Install with 'pip install scikit-learn'.")
        sys.exit(1)
    vectorizer = CountVectorizer(max_df=0.95, min_df=2, stop_words='english')
    dtm = vectorizer.fit_transform(docs)
    lda = LatentDirichletAllocation(n_components=n_topics, random_state=42)
    lda.fit(dtm)
    topics = []
    vocab = vectorizer.get_feature_names_out()
    for idx, topic in enumerate(lda.components_):
        top_indices = topic.argsort()[-n_top_words:][::-1]
        top_words = [vocab[i] for i in top_indices]
        topics.append((idx, top_words))
    return topics

def summarize_captions(transcript: List[dict]) -> Tuple[Counter, List[Tuple[int, List[str]]]]:
    """Generate word frequencies and topics from a transcript.
    """
    ensure_nltk_resources()
    stop_words = set(stopwords.words('english'))
    # Concatenate all caption texts
    full_text = " ".join(entry['text'] for entry in transcript)
    tokens = preprocess_text(full_text, stop_words)
    freq = get_word_frequencies(tokens)
    # For topic modeling we keep raw sentences (still filtered by stop‑words via vectorizer)
    sentences = [entry['text'] for entry in transcript]
    topics = extract_topics(sentences)
    return freq, topics

def pretty_print_frequencies(freq: Counter, top_n: int = 20) -> None:
    """Print the most common words."""
    print("\nTop word frequencies:")
    for word, count in freq.most_common(top_n):
        print(f"{word:<15} {count}")

def pretty_print_topics(topics: List[Tuple[int, List[str]]]) -> None:
    """Display extracted topics."""
    print("\nExtracted topics:")
    for idx, words in topics:
        print(f"Topic {idx + 1}: {', '.join(words)}")

def main() -> None:
    """Entry point.
    Accepts a YouTube video ID as a command‑line argument; falls back to a demo video.
    """
    demo_video = "dQw4w9WgXcQ"  # Rick Astley – never hurts as a placeholder
    video_id = sys.argv[1] if len(sys.argv) > 1 else demo_video
    logging.info(f"Analyzing video ID: {video_id}")
    transcript = fetch_captions(video_id)
    freq, topics = summarize_captions(transcript)
    pretty_print_frequencies(freq)
    pretty_print_topics(topics)

if __name__ == "__main__":
    main()
