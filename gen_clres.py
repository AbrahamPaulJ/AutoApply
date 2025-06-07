import json
import os

user = "abraham"  

# Define paths relative to the user folder
folder_path = os.path.join("Users", user)
resume_path = os.path.join(folder_path, "resume.txt")
clres_path = os.path.join(folder_path, "clres.txt")

# Load resume data
with open(resume_path, "r", encoding="utf-8") as f:
    resume = json.load(f)

# Fields to remove from each work entry
fields_to_remove = ["name", "location", "description"]

# Remove specified fields from the "work" section
for job in resume.get("work", []):
    for field in fields_to_remove:
        job.pop(field, None)

# Write the cleaned data
with open(clres_path, "w", encoding="utf-8") as f:
    json.dump(resume, f, indent=2, ensure_ascii=False)

print(f"{clres_path} created successfully with 'name', 'location', and 'description' removed from work entries.")
