# Rank-Aware Security Advisor Chatbot

## 📖 Project Description

This project is an AI-powered Security Advisor Chatbot designed to interactively educate users on cybersecurity best practices. It utilizes a Large Language Model (LLM) with Retrieval-Augmented Generation (RAG) to provide accurate, context-aware advice. The chatbot features a gamified progression system where users gain Experience Points (XP) and advance through ranks, unlocking access to more advanced security topics.

### Key Features
- **Interactive Chat Interface:** Users can ask security-related questions in natural language.
- **Rank-Based Progression:** A system of ranks and XP (from "Security Novice" to "Security Master") to motivate learning.
- **Topic Gating:** Access to advanced topics is restricted by the user's rank, ensuring a structured learning path.
- **Retrieval-Augmented Generation (RAG):** The chatbot uses a knowledge base built from your own PDF documents to provide accurate and reliable answers, reducing hallucinations.
- **PDF Document Processing:** Automatically processes your own security documents (e.g., company policies, NIST guidelines) to build the chatbot's knowledge base.
- **Interactive Quizzes:** The chatbot generates follow-up questions to test user understanding and award XP for correct answers.

---

## 🛠️ Installation and Setup

Follow these steps to get the project running on your local machine.

**1. Clone the Repository**
```bash
git clone https://github.com/diyarrr/security_chatbot.git
cd security_chatbot
```

**2. Create virtual environment**
Macos/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Run the setup script**
```bash
python setup.py
```

If you are running this first time, it will create the .env file under the config folder and will ask you to replace the placeholder openai key with the actual key. Then you can press enter and continue with the setup.

**5. Start the backend server**
```bash
python src/backend/app.py
```

**6. Run the frontend**
```bash
cd src/frontend-vite
npm install
npm run dev
```

Now you can go to localhost:3000 and interact with the application


## 📁 File Overview

Here is a more detailed breakdown of the key files and their purpose in the project:

---

### `setup.py`

- **Purpose:** Orchestrates the setup process; run once to prepare the environment.
- **Key Functions:**
  - `main()`: The main entry point that coordinates setup tasks.
  - `setup_pdf_processing()`: Converts PDFs into text for the knowledge base and populates ChromaDB.
  - Also creates `.env` and runs other utility functions.

---

### `src/backend/app.py`

- **Purpose:** Core backend server using Flask.
- **Key Functions:**
  - `login()`: Manages user authentication and session creation.
  - `chat()`: Handles chat questions, topic access, AI response, and quiz generation.
  - `quiz()`: Evaluates quiz answers, updates XP and rank, and returns results.

---

### `src/backend/chatbot.py`

- **Purpose:** Encapsulates AI logic and LLM interactions.
- **Key Class:** `SecurityChatbot`
  - `__init__(self, retriever)`: Initializes with a ChromaDB retriever.
  - `check_topic_access(self, query, user_rank)`: Validates if user has rank to access topic.
  - `generate_response(self, query, user_rank)`: Builds prompts and fetches AI response.
  - `generate_followup_question(self, answer)`: Creates multiple-choice quizzes from answers.

---

### `src/backend/retriever.py`

- **Purpose:** Manages ChromaDB and document embedding.
- **Key Class:** `DocumentRetriever`
  - `__init__(self, db_directory)`: Connects to ChromaDB on disk.
  - `add_document(self, doc_path, doc_id)`: Converts text into vectors and stores them.
  - `query_documents(self, query, n_results=3)`: Retrieves top-matching chunks based on query.

---

### `src/backend/models.py`

- **Purpose:** Defines the user data model.
- **Key Class:** `User`
  - `__init__(self, user_id)`: Initializes user with 0 XP and rank 1.
  - `add_xp(self, points)`: Adjusts XP and evaluates for promotion.
  - `update_rank(self)`: Updates user rank based on XP.
  - `to_dict(self)`: Converts user data to dictionary format for API responses.

---

### `src/frontend-vite/src/main.js`

- **Purpose:** Handles frontend logic and user interactions.
- **Key Functions:**
  - `handleLogin()`: Sends login request and shows chat on success.
  - `sendMessage()`: Sends user input to backend and renders response.
  - `handleQuizAnswer()`: Submits quiz answers, updates UI and user XP.
  - `updateUserInfoDisplay()`: Refreshes rank and XP display.

---

## 🤝 Acknowledgements

- **Course:** CSE473 - Network and Information Security  
- **Instructor:** Dr. Salih Sarp  
- **Collaborators:** Diyar İsi, Mehmet Mahir Kayadelen


