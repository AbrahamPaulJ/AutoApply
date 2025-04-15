import json

# Load resume data from resume.txt
with open("resume.txt", "r", encoding="utf-8") as f:
    resume = json.load(f)

# Fields to remove from each work entry
fields_to_remove = ["name", "location", "description"]

# Remove specified fields from the "work" section
for job in resume.get("work", []):
    for field in fields_to_remove:
        job.pop(field, None)

# Write the cleaned data to clres.txt
with open("clres.txt", "w", encoding="utf-8") as f:
    json.dump(resume, f, indent=2, ensure_ascii=False)

print("clres.txt created successfully with 'name', 'location', and 'description' removed from work entries.")
