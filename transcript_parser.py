from pypdf import PdfReader
import json
import sys

with open('desc.json', 'r') as f:
    courses_data = json.load(f)

reader = PdfReader(sys.argv[1] )
text = reader.pages[0].extract_text().split('\n')
text = [t.split(' ')[:2] for t in text]
taken_courses = set()
for t in text:
    if t[0] in courses_data:
        taken_courses |= {tuple(t)}
print(taken_courses)

# not sure how to feed this info to the llm