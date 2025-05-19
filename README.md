# Candata Data Generator

A modern web application for generating custom datasets using AI. Built with FastAPI and CrewAI.

## Features

- Beautiful, animated user interface
- AI-powered dataset generation
- Customizable number of rows
- Optional backstory for context
- JSON dataset download
- Real-time feedback and loading states

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd candata-generator
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory and add your API keys:
```
GEMINI_API_KEY=your_gemini_api_key
SERPER_API_KEY=your_serper_api_key
```

5. Run the application:
```bash
python run.py
```

The application will be available at `http://localhost:8000`

## Usage

1. Open your web browser and navigate to `http://localhost:8000`
2. Enter the number of rows you want in your dataset
3. Provide a prompt describing the kind of data you need
4. Optionally, add a backstory for more context
5. Click "Generate Dataset"
6. Once generated, click the download button to get your JSON dataset

## Technologies Used

- FastAPI
- CrewAI
- TailwindCSS
- Animate.css
- Google Gemini API
- SerperDev API

## License

MIT License 