# Hotel Management AI Agent

## Objective
Build an AI Agent for a Hotel Management System that will have the power to answer the
queries of the customers about the hotel, room availability, contact number and the facilities
provided by the hotel.

## Features of AI Agent
1. Room Availability Check:
    - Allow users to get information about the number of rooms available in the Hotel.
2. Price Listing:
    - Allow users to know the prices of the hotel rooms of different categories.
3. Guest Services:
    - Provide information about hotel amenities, nearby attractions.
    - Facilitate room service requests, housekeeping, or maintenance queries.
4. Check-in/Check-out:
    - Support seamless check-in and check-out processes and timings
5. Feedback and Support:
    - Gather feedback from guests and handle support inquiries efficiently.

## Techstack
- Python 
- Langchain
- FastAPI
- ChromaDB

## Knowledge Base
The knowledge base will contain information in a Directory of PDFs or a Word Documents which will be
queried for information retrieval.
The knowledge base will contain information like room availability details, check-in and
check-out details, facilities provided by the hotel, and different services for the guests.

## AI Models(LLMs)
Google Gemini-pro LLM model has been used as this model is free to use.

## Embedding Model
The embedding model used is Google's GenerativeAI Embeddinggs.

## API Endpoints
- Upload
    - **Method**: `POST`
    - **URL**: `/upload`
    - **Parameters**: `UploadFile` type is accepted to upload the file
    - **Output**: For successful execution of users -  `File Stored successfully and Agent Successfully initialized` is returned.
    - **Description**: Takes up File and store it to chromadb database, and initializes the Agent.

- Ask Query
    - **Method**: `POST`
    - **URL**: `/askquery`
    - **Parameters**: `questions` which takes the query
    - **Output**: For successful execution the answer will be returned
    - **Description**: Takes up the query and searches for the corresponding query in database, google search, or api search.


## Installation and Executation
### Clone the Project Repository
Clone the repository or download the project files. Navigate to the project directory by using:
    
```bash
git clone https://github.com/souravbiswas19/Hotel-Management-AI-Agent.git
```

Go inside the `Hotel-Management-AI-Agent` directory.
```bash
cd Hotel-Management-AI-Agent
```

### Setup Python Virtual Environment
To set up the project environment, follow these steps:

1. Ensure you have Python 3.11.8 installed. This project has been run on `Python 3.11.8`. Download the python 3.11.8 from here: [Python 3.11](https://www.python.org/downloads/release/python-3118/)

Direct download link of Python 3.11.8: [Click to download from here](https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe)

2. Create a virtual environment using `venv`.

    ```bash
    python -m venv <virtual-environment-name>
    ```

3. Actiavte the virtual environment using:
    
    A. **Git Bash** - Navigate to the folder containing the virtual environment in Git Bash and run the command.
    ```bash
    source ./<virtual-environment-name>/Scripts/activate
    ``` 
    
    B. **Command-prompt** - Navigate to the folder containing the virtual environment in Command-Prompt and run the command.
    ```bash
    <virtual-environment-name>\Scripts\activate.bat
    ``` 
        
    C. **Powershell** - Navigate to the folder containing the virtual environment in Powershell and run the command.
    ```bash
    <virtual-environment-name>\Scripts\activate.psl
    ```

4.  Install the dependencies listed in requirements.txt using pip:

    ```bash
    pip install -r requirements.txt
    ```

5. Setting up the `.env` file is provided in the `.env.examples` file in the Project directory. Assign your GOOGLE_API_KEY save the `.env.examples` file as `.env` file only. If you don't have a GOOGLE_API_KEY generate one from here [Google API Key Documentation](https://makersuite.google.com/app/apikey)

    ```bash
    GOOGLE_API_KEY = "<YOUR GOOGLE API KEY>"
    LANGCHAIN_TRACING_V2=true
    LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
    LANGCHAIN_API_KEY="<your-api-key>"
    LANGCHAIN_PROJECT=""
    ```

6. Setup the LangSmith by visiting this website and login - [LangSmith](https://smith.langchain.com/)
    
    **A.** *Create a New Project*
    ![Image 1](/logos/Screenshot%20(51).png)

    ![Image 2](/logos/Screenshot%20(50).png)

    **B.** *Select that new project*
    ![Image 3](/logos/Screenshot%20(53).png)

    **C.** *Select that `Setup` Menu under the project menu*
    ![Image 4](/logos/Screenshot%20(54).png)

    **D.** *Copy this code and paste in `.env` file*
    ![Image 5](/logos/Screenshot%20(55).png)

    **E.** *Go to `Setting`*
    ![Image 6](/logos/Screenshot%20(57).png)

    **F.** *Create an API Key and paste in `LANGCHAIN_API_KEY` variable in the .env file*
    ![Image 7](/logos/Screenshot%20(56).png)

7. `START THE SERVER` - To run the `Hotel-Management-AI-Agent` system, execute the following command in the Git bash/Command Prompt/Powershell by activating the environment as mentioned above:

    ```bash
    uvicorn main:app --reload
    ```

# You are ready to test the API Endpoints!