	import os
import sys
import json
import openai
from pathlib import Path
from typing import List, Tuple

try:
    from PyPDF2 import PdfReader
except ImportError:
    print('PyPDF2 is required. Install with "pip install PyPDF2"')
    sys.exit(1)

# Ensure OpenAI API key is set
openai.api_key = os.getenv('OPENAI_API_KEY')
if not openai.api_key:
    print('Error: OPENAI_API_KEY environment variable not set.')
    sys.exit(1)

MAX_TOKENS = 500  # Rough token limit per chunk for context
MODEL = 'gpt-3.5-turbo'

def read_pdf(pdf_path: str) -> str:
    """Extract raw text from a PDF file."""
    reader = PdfReader(pdf_path)
    text_parts = []
    for page in reader.pages:
        try:
            text_parts.append(page.extract_text() or "")
        except Exception:
            continue
    return "\n".join(text_parts)

def chunk_text(text: str, max_tokens: int = MAX_TOKENS) -> List[str]:
    """Split text into roughly max_tokens sized chunks.
    This simplistic splitter uses paragraph boundaries.
    """
    # Approximate tokens by word count / 0.75 (average English word ~0.75 token)
    words_per_chunk = int(max_tokens * 0.75)
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    chunks = []
    current = []
    current_len = 0
    for para in paragraphs:
        para_len = len(para.split())
        if current_len + para_len > words_per_chunk and current:
            chunks.append('\n\n'.join(current))
            current = []
            current_len = 0
        current.append(para)
        current_len += para_len
    if current:
        chunks.append('\n\n'.join(current))
    return chunks

def embed_chunks(chunks: List[str]) -> List[Tuple[str, List[float]]]:
    """Create embeddings for each chunk using OpenAI embeddings API.
    Returns list of (chunk_text, embedding_vector).
    """
    embeddings = []
    for chunk in chunks:
        resp = openai.Embedding.create(model='text-embedding-ada-002', input=chunk)
        embeddings.append((chunk, resp['data'][0]['embedding']))
    return embeddings

def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Compute cosine similarity between two vectors."""
    import math
    dot = sum(x*y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x*x for x in a))
    norm_b = math.sqrt(sum(x*x for x in b))
    return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0

def retrieve_relevant_chunks(query: str, embedded_chunks: List[Tuple[str, List[float]]], top_k: int = 3) -> List[str]:
    """Return the top_k most relevant chunk texts for a query."""
    query_emb = openai.Embedding.create(model='text-embedding-ada-002', input=query)['data'][0]['embedding']
    scored = [(cosine_similarity(query_emb, emb), txt) for txt, emb in embedded_chunks]
    scored.sort(key=lambda x: x[0], reverse=True)
    return [txt for _, txt in scored[:top_k]]

def answer_question(question: str, context_chunks: List[str]) -> str:
    """Ask the LLM to answer using provided context."""
    system_prompt = (
        "You are an assistant that answers questions based on the provided PDF content. "
        "Use only the supplied context and do not fabricate information."
    )
    user_prompt = f"Context:\n{\"\n---\n\".join(context_chunks)}\n\nQuestion: {question}"
    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.0,
        max_tokens=500,
    )
    return response['choices'][0]['message']['content'].strip()

def main():
    if len(sys.argv) < 2:
        print('Usage: python ChatPDF.py <path_to_pdf>')
        sys.exit(1)
    pdf_path = sys.argv[1]
    if not Path(pdf_path).is_file():
        print(f'Error: File not found – {pdf_path}')
        sys.exit(1)
    print('Extracting text from PDF...')
    raw_text = read_pdf(pdf_path)
    if not raw_text.strip():
        print('No extractable text found in the PDF.')
        sys.exit(1)
    print('Chunking text...')
    chunks = chunk_text(raw_text)
    print(f'Created {len(chunks)} chunks. Generating embeddings (this may take a while)...')
    embedded_chunks = embed_chunks(chunks)
    print('Ready! You can now ask questions about the document. Type "exit" to quit.')
    while True:
        try:
            question = input('\nYour question: ').strip()
        except (EOFError, KeyboardInterrupt):
            print('\nExiting.')
            break
        if not question or question.lower() in {'exit', 'quit'}:
            print('Goodbye.')
            break
        relevant = retrieve_relevant_chunks(question, embedded_chunks)
        answer = answer_question(question, relevant)
        print('\nAnswer:', answer)

if __name__ == '__main__':
    main()
