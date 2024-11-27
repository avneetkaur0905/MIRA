import os
import pandas as pd
import pdfplumber

# Paths to the resumes
candidates_dir = 'resume/candidates'
experts_dir = 'resume/experts'

# Function to extract text from a PDF
def extract_text_from_pdf(file_path):
    with pdfplumber.open(file_path) as pdf:
        text = ''
        for page in pdf.pages:
            text += page.extract_text() if page.extract_text() else ''
        return text

# Convert candidate resumes to a CSV file
candidate_data = []
for file_name in os.listdir(candidates_dir):
    if file_name.endswith('.pdf'):
        file_path = os.path.join(candidates_dir, file_name)
        text = extract_text_from_pdf(file_path)
        candidate_data.append({'Name': file_name.replace('.pdf', ''), 'Resume Content': text})

# Create a DataFrame and save as CSV
candidate_df = pd.DataFrame(candidate_data)
candidate_csv_path = 'resume/candidates_combined.csv'
candidate_df.to_csv(candidate_csv_path, index=False)

# Convert expert resumes to individual CSV files
for file_name in os.listdir(experts_dir):
    if file_name.endswith('.pdf'):
        file_path = os.path.join(experts_dir, file_name)
        text = extract_text_from_pdf(file_path)
        expert_df = pd.DataFrame([{'Name': file_name.replace('.pdf', ''), 'Resume Content': text}])
        expert_csv_path = f'resume/experts/{file_name.replace(".pdf", ".csv")}'
        expert_df.to_csv(expert_csv_path, index=False)

print("CSV files generated successfully.")