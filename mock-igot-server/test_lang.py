import json, sys
sys.stdout.reconfigure(encoding='utf-8')
with open('courses.json', encoding='utf-8') as f:
    courses = json.load(f)
for c in courses[:20]:
    lang = c.get('language', c.get('languages', 'Unknown'))
    print(f\"ID: {c.get('identifier')} | Lang: {lang} | Name: {c.get('name')}\")
