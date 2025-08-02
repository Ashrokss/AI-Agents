# Multi-Agent QA Automation App with FRD Generation

This is a Streamlit-based web application that leverages large language models and browser automation to:

* Perform Quality Assurance Testing for a given Application.
* Generate **Functional Requirement Documents (FRDs)** from GitHub repositories.
* Automatically generate **test plans and test cases** from functional requirements.
* Execute tests in a real browser using an intelligent **Browser Agent**.
* Display test plans, test cases, and execution results in a clean UI.

## Demo :
https://github.com/user-attachments/assets/6280f147-9e8f-4dbb-b8cc-36edde6a2bdd



## Setup Guide :

Step 1 : Browser Use requires Python 3.11 or higher.
```
uv venv --python 3.11
```

Step 2 :  Installing playwright & Browser Use.

```
uv pip install browser-use
uv run playwright install
```

Step 3 : Install other dependencies  
```
uv pip install -r requirements.txt
```

See the reference documentation : https://docs.browser-use.com/quickstart

## Features

### 1. QA Automation

* Input URL of the application to be tested.
* Upload a `.txt` file containing functional requirements.
* The system reads the requirements and:

  * Generates a test plan and test cases in markdown table format.
  * Produces detailed, structured test cases.
  * Executes test cases using a browser agent powered by LangChain + Azure OpenAI + `browser_use`.
  * Displays results with pass/fail status, description, and execution logs.

### 2. FRD Generation

* Input a GitHub repository URL.
* The system analyzes the source code and automatically generates a full FRD including:

  * Purpose
  * Functional overview
  * Functional and non-functional requirements
  * Error handling
  * Sample use cases

### 3. Feedback Analysis (critique Agent)
* Input the application URL and upload an FRD file.
* The system will:

  * Analyze whether the application fulfills the listed requirements.
  * For each functional requirement, determine if it is fully, partially, or not fulfilled.
  * Provide a critique, observations, and suggestions for improvement.
  * Output a detailed feedback report and structured JSON.

## Technologies Used

* **Streamlit** for UI
* **Azure OpenAI** for test generation and natural language understanding
* **LangChain** for LLM agent orchestration
* **browser\_use** for executing test cases in a real browser environment
* **ModelContextProtocol (MCP)** for filesystem communication
* **Pydantic** for data validation

## File Structure

```
fs_files/
├── FRD_requirements.txt         # Uploaded functional requirements
├── test_plan.md                 # Generated test plan
├── test_cases.md                # Generated test cases
├── test_execution_results.json  # Execution results (structured)
├── FRD_generated.txt            # Human-readable FRD
├── frd_output.json              # Structured FRD JSON
├── critic_results.txt           # Human-readable critique report
├── critique_output.json         # Structured feedback JSON

```

## How It Works

### QA Automation Flow:

1. User uploads `FRD_requirements.txt`and enters the URL of the application.
2. Agent 1 (Test Plan Generator) creates `test_plan.md` and `test_cases.md`.
3. Agent 2 (Browser Agent) reads test cases,test plan and executes them using a real browser.
4. Execution results are saved and shown in the UI.

### FRD Generation Flow:

1. User provides a GitHub repo URL.
2. A browser agent navigates to the repo, reads the code, and composes a well-structured FRD using predefined sections.
3. Outputs are saved as both structured JSON and readable text.

### Feedback Generation Flow:

1. User provides application URL and the FRD.
2. A browser agent navigates to the app url, reads the FRD, and composes a well-structured Feedback report against the FRD provided.
3. Outputs are saved as both structured JSON and readable text.


### Demo Application for QA Testing : 
1. https://demo.playwright.dev/todomvc/
2. https://www.saucedemo.com/

### Demo Github URL for FRD generation:
1. https://github.com/Ashrokss/AI-Agents/tree/main/SQL-Agent
2. https://github.com/Ashrokss/AI-Agents/tree/main/Finance%20Agent

### Demo file for Feedback generation:

1. Navigate to the FRD folder and use the `crtic_todo_frd.txt`

