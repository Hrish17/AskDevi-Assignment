import json
import os
import faiss
from datetime import datetime
import numpy as np
from sentence_transformers import SentenceTransformer

# Constants
CHUNKS_FILE = os.path.join("data", "bphs_chunks.json")
INDEX_FILE = os.path.join("data", "faiss_index.bin")
EMBEDDINGS_FILE = os.path.join("data", "bphs_embeddings.npy")

# Load sentence transformer model
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')


def load_chunks():
    with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def embed_chunks(chunks):
    texts = [chunk["content"] for chunk in chunks]
    embeddings = model.encode(texts, convert_to_numpy=True)
    return embeddings


def build_faiss_index(embeddings):
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    return index


def save_index(index, path):
    faiss.write_index(index, path)


def load_index(path):
    return faiss.read_index(path)


def save_embeddings(embeddings, path):
    np.save(path, embeddings)


def load_embeddings(path):
    return np.load(path)


def prepare_index():
    chunks = load_chunks()

    if os.path.exists(INDEX_FILE) and os.path.exists(EMBEDDINGS_FILE):
        index = load_index(INDEX_FILE)
    else:
        embeddings = embed_chunks(chunks)
        index = build_faiss_index(embeddings)
        save_index(index, INDEX_FILE)
        save_embeddings(embeddings, EMBEDDINGS_FILE)

    return chunks, index


def retrieve_chunks(question, k=3):
    chunks, index = prepare_index()

    # Embed the user query
    question_embedding = model.encode([question], convert_to_numpy=True)

    # Retrieve top-k
    distances, indices = index.search(question_embedding, k)
    relevant_chunks = [chunks[i] for i in indices[0]]

    return relevant_chunks


def build_prompt(user_question, birth_details, chunks):
    # Parse date_of_birth if it's a string
    dob = birth_details.date_of_birth
    if isinstance(dob, str):
        dob = datetime.strptime(dob, "%Y-%m-%d").date()

    tob = birth_details.time_of_birth
    # similarly parse time_of_birth if string
    if isinstance(tob, str):
        tob = datetime.strptime(tob, "%H:%M:%S").time()

    location = birth_details.place_of_birth
    astro_details = birth_details.rashi_report

    birth_info = (
        f"Date of Birth: {dob.day:02d}/{dob.month:02d}/{dob.year}, "
        f"Time: {tob.hour:02d}:{tob.minute:02d}, "
        f"Location: {location}, Timezone=5.5, "
        f"Astrological Details: {astro_details}.\n"
    )

    chunks_text = "\n\n".join(
        [f"Chapter {chunk['chapter']}: {chunk['content']}" for chunk in chunks])

    prompt = (
        f"You are Devi, a wise astrologer. Here is the user's birth chart:\n{birth_info}\n\n"
        f"The user asks: \"{user_question}\"\n\n"
        f"Refer to the following classical astrology text excerpts for guidance:\n\n{chunks_text}\n\n"
        f"Based on these excerpts and the user's chart, provide an insightful response in clear language."
        f"Just give the answer without any additional information or data. Don't say birth chart or chart or anything else. The answer shouldn't look like you're analysing the charts or planets. Don't use planets name. Limit your answer to 50-70 words.\n\n"
        f"Give general answers. Don't use astrological terms. Speak in humane way.\n\n"
    )

    return prompt
