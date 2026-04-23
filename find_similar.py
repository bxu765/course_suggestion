import json
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Load the pre-trained model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Load pre-computed embeddings and course metadata
course_embeddings = np.load('course_embeddings.npy')
with open('course_ids.json', 'r') as f:
    data = json.load(f)
    courses = data['courses']
    descriptions = data['descriptions']

# Load taken courses if available
taken_courses = set()
try:
    with open('taken_courses.json', 'r') as f:
        taken_data = json.load(f)
        taken_courses = set(taken_data.get('taken_courses', []))
except FileNotFoundError:
    pass

print(f"Loaded embeddings for {len(courses)} courses")
if taken_courses:
    print(f"Excluding {len(taken_courses)} courses already taken: {', '.join(sorted(taken_courses))}")

def find_similar_courses(interests: str, top_k: int = 5) -> list:
    """
    Find the most similar courses to a given string of interests.
    Excludes courses that have already been taken.
    
    Args:
        interests: A string describing interests/topics
        top_k: Number of top similar courses to return
    
    Returns:
        List of tuples (course_id, similarity_score, description)
    """
    # Generate embedding for the interests string
    interest_embedding = model.encode([interests])[0]
    
    # Calculate cosine similarity with all courses
    similarities = cosine_similarity([interest_embedding], course_embeddings)[0]
    
    # Get indices sorted by similarity
    sorted_indices = np.argsort(similarities)[::-1]
    
    # Create results, skipping taken courses
    results = []
    for idx in sorted_indices:
        if courses[idx] not in taken_courses:
            results.append({
                'course_id': courses[idx],
                'similarity': float(similarities[idx]),
                'description': descriptions[idx]
            })
        if len(results) >= top_k:
            break
    
    return results

if __name__ == "__main__":
    # Example usage
    interests = input("Enter your interests: ")
    
    print(f"\nSearching for courses similar to: '{interests}'\n")
    similar = find_similar_courses(interests, top_k=5)
    
    for i, result in enumerate(similar, 1):
        print(f"{i}. {result['course_id']} (similarity: {result['similarity']:.4f})")
        print(f"   {result['description']}\n")
