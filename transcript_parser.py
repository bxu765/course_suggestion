from pypdf import PdfReader
import json
import sys

with open('desc.json', 'r') as f:
    courses_data = json.load(f)

reader = PdfReader(sys.argv[1])
text = reader.pages[0].extract_text().split('\n')
text = [t.split(' ')[:2] for t in text]
taken_courses = []
for t in text:
    # t[0] is course code (e.g., "CS"), t[1] is course number (e.g., "1110")
    if len(t) >= 2 and t[0] in courses_data and t[1] in courses_data[t[0]]:
        course_id = t[0] + t[1]  # Combine into format like "CS1110"
        taken_courses.append(course_id)

# Save taken courses to a JSON file for use in find_similar.py
with open('taken_courses.json', 'w') as f:
    json.dump({'taken_courses': taken_courses}, f, indent=2)

print(f"Extracted {len(taken_courses)} courses from transcript:")
print(taken_courses)