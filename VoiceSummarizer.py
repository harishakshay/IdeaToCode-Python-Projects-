	import argparse
import os
import sys

# Speech-to-text
try:
    import speech_recognition as sr
except ImportError:
    sys.stderr.write('Missing dependency: speech_recognition. Install with pip install SpeechRecognition\n')
    sys.exit(1)

# Summarization (HuggingFace Transformers)
try:
    from transformers import pipeline
except ImportError:
    sys.stderr.write('Missing dependency: transformers. Install with pip install transformers\n')
    sys.exit(1)

def transcribe_audio(audio_path: str) -> str:
    """Convert an audio file to plain text using Google Web Speech API.
    Supports WAV, AIFF, FLAC formats. Returns the recognized text.
    """
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio_data = recognizer.record(source)
    try:
        # Uses the free Google Web Speech API (requires internet)
        return recognizer.recognize_google(audio_data)
    except sr.UnknownValueError:
        return "[Unintelligible speech]"
    except sr.RequestError as e:
        sys.stderr.write(f"Speech recognition service error: {e}\n")
        return ""

def summarize_text(text: str, max_length: int = 130, min_length: int = 30) -> str:
    """Summarize a block of text using a pretrained transformer model.
    The function lazily loads the summarization pipeline on first call.
    """
    # Load a lightweight summarization model; change model name for better quality.
    summarizer = summarize_text.summarizer if hasattr(summarize_text, 'summarizer') else None
    if summarizer is None:
        summarizer = pipeline('summarization', model='sshleifer/distilbart-cnn-12-6')
        summarize_text.summarizer = summarizer
    # Transformers expects a list of strings.
    summary = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
    return summary[0]['summary_text']

def main():
    parser = argparse.ArgumentParser(description='Convert voice recordings to summarized text.')
    parser.add_argument('audio_file', nargs='?', help='Path to the input audio file (wav, flac, aiff).')
    args = parser.parse_args()

    if not args.audio_file:
        sys.stderr.write('No audio file provided. Use: python VoiceSummarizer.py path/to/audio.wav\n')
        sys.exit(1)

    if not os.path.isfile(args.audio_file):
        sys.stderr.write(f'File not found: {args.audio_file}\n')
        sys.exit(1)

    print('Transcribing audio...')
    transcript = transcribe_audio(args.audio_file)
    if not transcript:
        sys.stderr.write('Transcription failed or returned empty text.\n')
        sys.exit(1)
    print('--- Transcript ---')
    print(transcript)
    print('\nSummarizing transcript...')
    summary = summarize_text(transcript)
    print('--- Summary ---')
    print(summary)

if __name__ == "__main__":
    main()
