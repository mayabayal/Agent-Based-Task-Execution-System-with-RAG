import streamlit as st
import openai
import requests
from serpapi import GoogleSearch
from urllib.parse import urlencode

# Initialize OpenAI API
openai.api_key = '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'  # Replace with your actual API key

# API keys for external services
serpapi_key = '41a351d1f820a6c6fa8f0d4e4242c722dc02bb4a0d2e6ba056876d7ad9d5aaf1'  # Replace with your actual SerpAPI key
youtube_api_key = 'AIzaSyAQ1PF_d6elVZawYuCKYwBRzh9MvHw9WFI'  # Replace with your actual YouTube API key

# Function to perform a Google search using SerpAPI
def search_google(query: str) -> str:
    try:
        params = {
            "q": query,
            "api_key": serpapi_key,
            "num": 10  # Retrieve the top 10 results
        }
        search = GoogleSearch(params)
        results = search.get_dict()

        # Extract and format results
        links = []
        for result in results.get('organic_results', []):
            title = result.get('title')
            link = result.get('link')
            snippet = result.get('snippet', '')
            links.append(f"Title: {title}\nSnippet: {snippet}\nURL: {link}\n")

        return "Google Search Results:\n" + "\n".join(links)
    except Exception as e:
        return f"Error performing Google search: {e}"

# Function to search YouTube videos
def analyze_youtube_video(query: str) -> str:
    try:
        params = {
            "part": "snippet",
            "q": query,
            "key": youtube_api_key,
            "type": "video",
            "maxResults": 5
        }
        url = f"https://www.googleapis.com/youtube/v3/search?{urlencode(params)}"
        response = requests.get(url)
        response.raise_for_status()
        video_results = response.json()

        # Extract and format results
        videos = []
        for item in video_results.get('items', []):
            title = item['snippet']['title']
            description = item['snippet']['description']
            video_id = item['id']['videoId']
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            videos.append(f"Title: {title}\nDescription: {description}\nURL: {video_url}\n")

        return "YouTube Video Results:\n" + "\n".join(videos)
    except requests.exceptions.RequestException as e:
        return f"Error performing YouTube video search: {e}"

# Function to perform a web search and summarize using OpenAI
def perform_google_search(query: str) -> str:
    prompt = (
        f"Conduct a detailed web research on '{query}'. Summarize the key findings, "
        "including any relevant news articles, research papers, and other resources."
    )
    return llm_generate(prompt)

# Function to provide legal advice using LLM
def provide_legal_advice(query: str) -> str:
    prompt = f"As a legal expert, provide detailed advice on: {query}"
    return llm_generate(prompt)

# Function to provide medical advice using LLM
def provide_medical_advice(query: str) -> str:
    prompt = f"As a medical professional, give comprehensive insights on: {query}"
    return llm_generate(prompt)

# Function to interact with OpenAI's GPT-4 or GPT-3.5 Turbo model using chat
def llm_generate(prompt: str) -> str:
    response = openai.ChatCompletion.create(
        model="gpt-4",  # Use the chat model (gpt-3.5-turbo or gpt-4)
        messages=[
            {"role": "system", "content": "You are a knowledgeable expert."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=300,
        temperature=0.7  # Adjust temperature for creativity
    )
    return response.choices[0].message['content'].strip()

# Base class for all agents
class Agent:
    def __init__(self, name: str, task_function):
        self.name = name
        self.task_function = task_function
    
    def perform_task(self, task_detail: str) -> str:
        result = self.task_function(task_detail)
        st.write(f"{self.name}: {result}")
        return result

# Coordinator that manages task execution
class TaskCoordinator:
    def __init__(self, task_description: str):
        self.task_description = task_description
        self.agents = []
        self.task_map = {
            "GoogleSearch": search_google,
            "YouTubeVideo": analyze_youtube_video,
            "LegalAdvisor": provide_legal_advice,
            "MedicalAdvisor": provide_medical_advice
        }

    def setup_agents(self):
        # Determine required agents based on the task description
        if "google" in self.task_description.lower() or "search" in self.task_description.lower():
            self.agents.append(Agent("GoogleSearch", self.task_map["GoogleSearch"]))
        if "youtube" in self.task_description.lower() or "video" in self.task_description.lower():
            self.agents.append(Agent("YouTubeVideo", self.task_map["YouTubeVideo"]))
        if "legal" in self.task_description.lower() or "law" in self.task_description.lower():
            self.agents.append(Agent("LegalAdvisor", self.task_map["LegalAdvisor"]))
        if "medical" in self.task_description.lower() or "health" in self.task_description.lower():
            self.agents.append(Agent("MedicalAdvisor", self.task_map["MedicalAdvisor"]))

    def execute_task(self) -> str:
        st.write("Coordinator: Starting task execution.")
        task_result = self.task_description

        for agent in self.agents:
            task_result = agent.perform_task(task_result)

        st.write("Coordinator: Task execution completed.")
        return task_result

# Streamlit frontend
st.title("Agent-Based Task Execution System with RAG")

task_description = st.text_input("Enter a task description:", "Research the latest legal developments in privacy law and find relevant YouTube videos.")

if st.button("Execute Task"):
    coordinator = TaskCoordinator(task_description)
    coordinator.setup_agents()
    final_output = coordinator.execute_task()
    st.subheader("Final Output")
    st.write(final_output)
