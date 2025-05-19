from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from crewai import Agent, Task, Crew, LLM
from crewai_tools import SerperDevTool
from typing import Optional
import json
import os
import shutil
from dotenv import load_dotenv
import requests
import pandas as pd

load_dotenv()

# Configure API keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

# Initialize tools
serper_tool = SerperDevTool(api_key=SERPER_API_KEY)

# Initialize the LLM
llm = LLM(
    model="gemini/gemini-2.0-flash",
    temperature=0.7,
    api_key=GEMINI_API_KEY,
    provider="google"
)

# Clean up existing datasets
def cleanup_datasets():
    datasets_dir = "static/datasets"
    if os.path.exists(datasets_dir):
        try:
            shutil.rmtree(datasets_dir)
            print("Cleaned up existing datasets directory")
        except Exception as e:
            print(f"Error cleaning up datasets: {e}")
    os.makedirs(datasets_dir, exist_ok=True)
    print("Created fresh datasets directory")

# Clean up on startup
cleanup_datasets()

app = FastAPI(title="Candata Dataset Generator")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_root():
    return FileResponse("static/index.html")

class DatasetRequest(BaseModel):
    num_rows: int
    prompt: str
    backstory: Optional[str] = None

@app.post("/generate-dataset")
async def generate_dataset(request: DatasetRequest):
    try:
        # Create the Data Analyst agent
        data_analyst = Agent(
            role="Principal Data Architect",
            goal="Deeply understand dataset requirements and translate them into precise, structured data specifications",
            backstory=(
                "You are a world-renowned Data Architect with 15+ years of experience working with Fortune 500 companies. "
                "You have an innate ability to deconstruct vague prompts into clear data models. "
                "You're obsessed with clarity, structure, and creating the blueprint for perfectly aligned datasets. "
                "You lead with insight and always bring structure to chaos. The team relies on your deep analytical thinking "
                "to decide what columns and types of data are truly meaningful."
            ),
            verbose=True,
            allow_delegation=True,
            llm=llm,
            tools=[serper_tool]
        )

        # Create the Data Generator agent
        data_generator = Agent(
            role="Elite Synthetic Data Engineer",
            goal="Generate hyper-realistic, high-quality synthetic datasets that align perfectly with the specified goals",
            backstory=(
                "You are an elite Synthetic Data Engineer, trusted by the top AI research labs to generate training data "
                "that powers cutting-edge models. Your data generation skills are second to none — realistic, clean, and always on point. "
                "You've generated datasets for autonomous vehicles, finance, healthcare, and more. You understand the power of data and treat it "
                "as a foundational layer of innovation. Your job is to create not just rows, but valuable information that makes models smarter."
            ),
            verbose=True,
            tools=[serper_tool],
            allow_delegation=True,
            llm=llm
        )

        # Create tasks
        analysis_task = Task(
            description=f"Analyze the following requirements and determine the necessary columns for the dataset:\n"
                       f"Number of rows: {request.num_rows}\n"
                       f"Prompt: {request.prompt}\n"
                       f"Backstory: {request.backstory if request.backstory else 'Not provided'}\n\n"
                       f"Use the search tool to find relevant industry standards and best practices for similar datasets.",
            agent=data_analyst,
            expected_output="A detailed specification of the dataset structure including column names, data types, and any constraints or relationships between columns."
        )

        generation_task = Task(
            description=f"Generate a dataset with {request.num_rows} rows based on the analysis.\n"
                       f"Use the search tool to find real-world examples and ensure the data is realistic and up-to-date.",
            agent=data_generator,
            expected_output=f"A JSON array containing {request.num_rows} objects, each representing a row in the dataset with realistic data values."
        )

        # Create and execute the crew
        crew = Crew(
            agents=[data_analyst, data_generator],
            tasks=[analysis_task, generation_task],
            verbose=True
        )
        
        result = crew.kickoff()
        print("Crew result:", result)  # Debug log
        
        # Convert CrewOutput to string and then parse as JSON
        if isinstance(result, str):
            try:
                # Remove any markdown code block markers
                cleaned_result = result.replace('```json', '').replace('```', '').strip()
                dataset = json.loads(cleaned_result)
                print("Parsed dataset:", dataset)  # Debug log
            except json.JSONDecodeError as e:
                print("JSON decode error:", e)  # Debug log
                dataset = result
        else:
            dataset = str(result)
        
        # Save the generated dataset
        dataset_path = f"static/datasets/dataset_{request.num_rows}.json"
        os.makedirs(os.path.dirname(dataset_path), exist_ok=True)
        
        with open(dataset_path, "w") as f:
            if isinstance(dataset, (dict, list)):
                json.dump(dataset, f, indent=2)
            else:
                f.write(dataset)
        
        # Create preview data using pandas
        if isinstance(dataset, (dict, list)):
            df = pd.DataFrame(dataset)
            preview_data = df.head().to_dict(orient='records')
            print("Preview data:", preview_data)  # Debug log
        else:
            preview_data = str(dataset)[:500] + "..."
        
        response_data = {
            "status": "success",
            "message": "Dataset generated successfully",
            "download_url": f"/static/datasets/dataset_{request.num_rows}.json",
            "preview_data": preview_data
        }
        print("Response data:", response_data)  # Debug log
        
        return JSONResponse(response_data)
        
    except Exception as e:
        print("Error:", str(e))  # Debug log
        raise HTTPException(status_code=500, detail=str(e))
