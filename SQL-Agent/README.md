

# 🛢️ SQL Agent – Agno POC

This is a small Proof-of-Concept (POC) application demonstrating how to build an interactive SQL Agent using the [`agno`](https://github.com/agnodice/agno) library, powered by Azure OpenAI, with a Streamlit-based UI.

The agent allows users to ask natural language questions about a MySQL database and receive contextual answers by executing appropriate SQL queries behind the scenes.

---

## 📸 Demo Video

> https://github.com/user-attachments/assets/e3fc981f-df1d-47bb-8c55-4b317270d813




## 📌 Features

* 🔍 **Natural Language Querying**: Ask questions about your MySQL database in plain English.
* ⚡ **LLM-powered Agent**: Uses `AzureOpenAI` via `agno` to interpret and generate SQL queries.
* 🧰 **Tool Integration**: Employs `SQLTools` from Agno to connect and query MySQL.
* 🖥️ **Streamlit UI**: Lightweight and interactive frontend with customizable CSS.
* 🔒 **Secure Config**: Loads credentials via a configuration module.

---

## 🧠 How It Works

1. The agent is initialized with:

   * `AzureOpenAI` as the model backend.
   * `SQLTools` for database interaction.
2. Users enter a natural language question.
3. The agent translates it into SQL, executes it, and returns the result.
4. Optionally, the agent exposes tool usage details for debugging.

---

## 🧱 Project Structure

```
.
├── config.py          # Configuration file for environment variables (DB credentials, API key)
├── style.py           # Custom CSS for Streamlit app
├── main.py            # Main Streamlit app (provided above)
└── requirements.txt   # Python dependencies 
```

---

## ⚙️ Setup Instructions

### 1. 🔧 Prerequisites

* Python 3.9+
* MySQL Server running locally
* Azure OpenAI resource (API key and endpoint)
* [Streamlit](https://streamlit.io/)
* [`agno`](https://pypi.org/project/agno/)

### 2. 🛠️ Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. 🔑 Set Up Configuration

In `config.py`, define:

```python
class Config:
    MY_SQL_PASS = "<your_mysql_password>"
    MY_SQL_DATABASE_NAME = "<your_database>"
    AZURE_OPENAI_API_KEY = "<your_azure_api_key>"
    AZURE_OPENAI_ENDPOINT = "<your_azure_endpoint>"
```

### 4. 🚀 Run the App

```bash
streamlit run app.py
```
---


## 🧪 Notes

* Currently uses non-streaming mode (`stream=False`). You can enable streaming by uncommenting the relevant code block.
* Be cautious about exposing sensitive database data depending on the use-case.

---


