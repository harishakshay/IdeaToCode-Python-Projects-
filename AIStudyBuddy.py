	import re
import random
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize

# Ensure required NLTK data is available without verbose output
nltk.download('punkt', quiet=True)

class AIStudyBuddy:
    @staticmethod
    def _extract_terms_definitions(text):
        """Extract "Term: Definition" or "Term - Definition" pairs from raw notes."""
        pattern = re.compile(r'^\s*([A-Za-z][A-Za-z0-9\s]+?)\s*[-:]\s*(.+)$', re.MULTILINE)
        return pattern.findall(text)

    @staticmethod
    def generate_flashcards(text):
        """Return a list of flashcards. Each card is a dict with 'front' and 'back'."""
        pairs = AIStudyBuddy._extract_terms_definitions(text)
        if pairs:
            return [{'front': term.strip(), 'back': definition.strip()} for term, definition in pairs]
        # Fallback: treat each sentence as a card, using the first capitalized word as the term
        flashcards = []
        for sent in sent_tokenize(text):
            words = word_tokenize(sent)
            capitals = [w for w in words if w[0].isupper() and w.isalpha()]
            if capitals:
                flashcards.append({'front': capitals[0], 'back': sent.strip()})
        return flashcards

    @staticmethod
    def generate_quiz(text, num_questions=3):
        """Create simple fill‑in‑the‑blank questions from the notes.
        Returns a list of dicts with 'question' and 'answer'."""
        sentences = sent_tokenize(text)
        random.shuffle(sentences)
        questions = []
        for sent in sentences:
            if len(questions) >= num_questions:
                break
            words = word_tokenize(sent)
            candidates = [w for w in words if w[0].isupper() and w.isalpha()]
            if not candidates:
                continue
            term = random.choice(candidates)
            blank = '_' * len(term)
            q_text = sent.replace(term, blank, 1)
            questions.append({'question': q_text, 'answer': term})
        return questions

def main():
    sample_notes = """
    Photosynthesis: The process by which green plants use sunlight to synthesize foods from carbon dioxide and water.
    Mitochondria - The powerhouse of the cell, generating ATP through respiration.
    Newton's First Law: An object at rest stays at rest unless acted upon by an external force.
    The capital of France is Paris.
    Water's chemical formula is H2O.
    """
    buddy = AIStudyBuddy()
    flashcards = buddy.generate_flashcards(sample_notes)
    quiz = buddy.generate_quiz(sample_notes, num_questions=5)

    print("=== Flashcards ===")
    for i, fc in enumerate(flashcards, 1):
        print(f"{i}. Front: {fc['front']}\n   Back: {fc['back']}\n")

    print("=== Quiz Questions ===")
    for i, q in enumerate(quiz, 1):
        print(f"{i}. {q['question']}")
        print(f"   Answer: {q['answer']}\n")

if __name__ == "__main__":
    main()
