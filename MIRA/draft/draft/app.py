import os
import pandas as pd
import random
from sentence_transformers import SentenceTransformer
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv

# Load environment variables
load_dotenv("path_to_your_env")  # Ensure your .env contains "OPENAI_API_KEY"

# Initialize Sentence Transformer model for embeddings
embed_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# Flag to choose between OpenAI and Ollama
USE_OPENAI = False

# Initialize the language model based on the flag
if USE_OPENAI:
    llm = ChatOpenAI(model="gpt-3.5-turbo")
else:
    llm = ChatOllama(model="mistral")

# Embedding tool class
class EmbeddingTool:
    def _init_(self, model):
        self.model = model

    def _call_(self, text):
        return self.model.encode(text)

# Scoring tool class
class ScoringTool:
    def _init_(self, llm):
        self.llm = llm

    def _call_(self, inputs):
        candidate_section = inputs.get("candidate_section")
        expert_section = inputs.get("expert_section")
        job_description = inputs.get("job_description", "")

        score_prompt = ChatPromptTemplate.from_template(
            "On a scale of 1 to 10, rate the relevance of the expert skills in relation to the provided section. "
            "Provide a detailed rationale for the score based on the skills listed below.\n\n"
            "Average Candidate Skills: {candidate_section}\n\n"
            "Expert Skills: {expert_section}\n\n"
            "Job Description: {job_description}\n\n"
            "Provide the numerical score (e.g., 8/10) followed by a detailed explanation."
        )

        llm_input = {
            "candidate_section": candidate_section,
            "expert_section": expert_section,
            "job_description": job_description,
        }

        score_chain = (
            {
                "candidate_section": RunnablePassthrough(),
                "expert_section": RunnablePassthrough(),
                "job_description": RunnablePassthrough(),
            }
            | score_prompt
            | self.llm
            | StrOutputParser()
        )

        llm_score = score_chain.invoke(llm_input)
        return llm_score

def parse_llm_score(score_text):
    """Parse LLM's score, handling both integers and floats, and extract explanation."""
    try:
        # Handle scores with decimals (e.g., 7.5/10)
        score_parts = score_text.split('/')
        score = float(score_parts[0].strip())  # Convert to float to handle decimal scores
        explanation = score_parts[1].strip() if len(score_parts) > 1 else "No explanation provided."
        return score, explanation
    except ValueError as e:
        print(f"Error parsing LLM score: {e}")
        return 0, "Error occurred during parsing."

def calculate_relevance(
    candidate_section,
    expert_section,
    job_description,
    weight_candidates=0.5,
    weight_jd=0.5,
    weight_similarity=0.5,
    embed_tool=None,
    scoring_tool=None,
):
    candidate_embedding = embed_tool(candidate_section)
    expert_embedding = embed_tool(expert_section)
    jd_embedding = embed_tool(job_description)

    # Cosine similarity scores
    similarity_score_candidate = cosine_similarity([candidate_embedding], [expert_embedding])[0][0]
    similarity_score_jd = cosine_similarity([jd_embedding], [expert_embedding])[0][0]

    # LLM scoring
    try:
        llm_score_candidate = scoring_tool(
            {"candidate_section": candidate_section, "expert_section": expert_section}
        )
        score_candidate, explanation_candidate = parse_llm_score(llm_score_candidate)

        llm_score_jd = scoring_tool(
            {"candidate_section": job_description, "expert_section": expert_section}
        )
        score_jd, explanation_jd = parse_llm_score(llm_score_jd)
    except Exception as e:
        print(f"Error in LLM scoring: {e}")
        score_candidate, explanation_candidate = 0, "Error occurred during scoring."
        score_jd, explanation_jd = 0, "Error occurred during scoring."

    # Weighted final scores
    final_candidate_score = (
        weight_similarity * similarity_score_candidate * 10 + weight_candidates * score_candidate
    )
    final_jd_score = (
        weight_similarity * similarity_score_jd * 10 + weight_jd * score_jd
    )

    final_score = (final_candidate_score + final_jd_score) / 2

    return {
        "similarity_candidate": similarity_score_candidate * 10,
        "similarity_jd": similarity_score_jd * 10,
        "candidate_score": final_candidate_score,
        "jd_score": final_jd_score,
        "final_score": final_score,
        "explanation_candidate": explanation_candidate,
        "explanation_jd": explanation_jd,
    }

# Create tools
embed_tool = EmbeddingTool(embed_model)
scoring_tool = ScoringTool(llm)

# Reading the combined candidate CSV file
candidate_csv_path = 'resume/candidates_combined.csv'
candidate_df = pd.read_csv(candidate_csv_path)

# Job Description
job_description = "Expert needed in AI, Robotics, and Data Analysis with strong experience in Project Management and SolidWorks."

# Calculate overall skillset of candidates
average_skills = candidate_df['Resume Content'].apply(lambda x: x.split(', '))
combined_skills = ", ".join(average_skills.explode().unique())

# Processing experts and calculating relevancy scores
experts_dir = 'resume/experts'
relevancy_scores = []
for file_name in os.listdir(experts_dir):
    if file_name.endswith('.csv'):
        file_path = os.path.join(experts_dir, file_name)
        try:
            expert_df = pd.read_csv(file_path)
            expert_section = expert_df['Resume Content'].iloc[0]  # Get the content from the first row

            # Calculate relevance scores
            result = calculate_relevance(
                candidate_section=combined_skills,
                expert_section=expert_section,
                job_description=job_description,
                embed_tool=embed_tool,
                scoring_tool=scoring_tool,
            )

            relevancy_scores.append({
                'Expert Name': file_name.replace('.csv', ''),
                'Similarity Score with Candidate Skills': result['similarity_candidate'],
                'Similarity Score with Job Description': result['similarity_jd'],
                'Candidate Score': result['candidate_score'],
                'JD Score': result['jd_score'],
                'Final Score': result['final_score'],
                'Explanation (Candidate)': result['explanation_candidate'],
                'Explanation (JD)': result['explanation_jd']
            })
        except Exception as e:
            print(f"Error processing {file_name}: {e}")

# Save the results to a CSV
relevancy_df = pd.DataFrame(relevancy_scores)
relevancy_df.to_csv('resume/expert_relevancy_scores.csv', index=False)
print("Relevancy scores for experts have been saved.")