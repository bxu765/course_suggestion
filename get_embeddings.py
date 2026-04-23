import json
import numpy as np
from sentence_transformers import SentenceTransformer

# Load the pre-trained model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Load course descriptions
with open('desc.json', 'r') as f:
    courses_data = json.load(f)

# Flatten the data structure and filter out "-" descriptions
courses = []
descriptions = []

for subject, courses_dict in courses_data.items():
    for course_num, description in courses_dict.items():
        # Skip courses with "-" as description (no actual description)
        if description.strip() == "-":
            continue
        course_id = f"{subject}{course_num}"
        courses.append(course_id)
        descriptions.append(description)

print(f"Loaded {len(courses)} courses (excluded courses with no description)")

# Generate embeddings for all courses
print("Generating embeddings for all courses...")
course_embeddings = model.encode(descriptions, show_progress_bar=True)

# Save embeddings and course metadata
np.save('course_embeddings.npy', course_embeddings)
with open('course_ids.json', 'w') as f:
    json.dump({
        'courses': courses,
        'descriptions': descriptions
    }, f, indent=4)

print(f"Saved {len(courses)} embeddings to course_embeddings.npy")
print(f"Saved course metadata to course_ids.json")
