	import os, sys
from typing import List, Dict, Tuple

try:
    from sentence_transformers import SentenceTransformer, util
except ImportError:
    sys.exit("Please install sentence-transformers: pip install sentence-transformers")

class ResumeRanker:
    """Rank resumes against a job description using sentence embeddings."""
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        # Load a lightweight transformer model for semantic similarity
        self.model = SentenceTransformer(model_name)

    def embed(self, texts: List[str]):
        # Encode a list of texts to tensors
        return self.model.encode(texts, convert_to_tensor=True)

    def rank(self, job_desc: str, resumes: List[Dict[str, str]], top_k: int = None) -> List[Tuple[Dict[str, str], float]]:
        job_emb = self.embed([job_desc])[0]
        resume_texts = [r["text"] for r in resumes]
        resume_embs = self.embed(resume_texts)
        scores = util.cos_sim(job_emb, resume_embs)[0]
        scored = [(resumes[i], float(scores[i])) for i in range(len(resumes))]
        scored.sort(key=lambda x: x[1], reverse=True)
        if top_k:
            scored = scored[:top_k]
        return scored

def main():
    job_description = "We need a data scientist with experience in Python, machine learning, and data visualization."
    resumes = [
        {"name": "Alice", "text": "Data scientist proficient in Python, machine learning, and Tableau."},
        {"name": "Bob", "text": "Software engineer with Java and C++ experience, no ML."},
        {"name": "Carol", "text": "Experienced data analyst skilled in Python, data visualization, and statistical modeling."},
    ]
    ranker = ResumeRanker()
    ranked = ranker.rank(job_description, resumes)
    print("Resume ranking:")
    for i, (resume, score) in enumerate(ranked, 1):
        print(f"{i}. {resume['name']} - similarity: {score:.4f}")

if __name__ == "__main__":
    main()
