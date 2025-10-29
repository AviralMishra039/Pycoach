#  PyCoach: Adaptive RAG-Powered Python Tutor

**PyCoach** is a proof-of-concept application demonstrating a personalized **Retrieval-Augmented Generation (RAG)** system that leverages **User Modeling** and **Adaptive Prompting** to create an intelligent tutoring platform for **Python programming**.

The tutor employs a **Socratic teaching style**, dynamically adjusting its complexity based on the learner’s self-selected level.  
This project showcases robust **LangChain Expression Language (LCEL)** chains, **hybrid LLM deployment**, and **containerized architecture** using **Docker**.

---

## ✨ Core Innovations & Technology Stack

| **Feature** | **Concept Implemented** | **Why It Was Used (Value Proposition)** |
|--------------|--------------------------|-----------------------------------------|
| **Adaptive Prompting** | Level-Based Socratic Method | The tutor’s system prompt strictly enforces the “Explain First, Then Ask” rule, with complexity tailored to Beginner, Intermediate, or Expert levels — creating genuine scaffolding. |
| **High-Performance RAG** | BGE Embeddings & Optimized Retrieval | Achieves fast and accurate retrieval using local **BAAI/bge-small-en-v1.5** embeddings on a specialized knowledge base, ensuring grounded responses. |
| **Hybrid LLM Backend** | Cloud & Local Deployment | Offers two distinct options — **low-latency Gemini API** and **zero-cost, private Ollama/Llama 3** local deployment — maximizing flexibility and privacy. |
| **Architecture** | Dockerized Microservices (FastAPI/Streamlit) | Ensures one-click deployment and reliable, isolated environments for the backend, frontend, and the Ollama service. |
| **User Modeling** | Level Control & Status Dashboard | Provides transparent visibility into the current adaptive level, topic coverage, and next steps, removing reliance on mock score systems. |

---

##  RAG Design Decision (Optimization Note)

The application was initially designed with a **Cross-Encoder Reranker** to improve retrieval precision.  
However, evaluation showed that the **latency** introduced by the large reranker model outweighed the minimal accuracy gain from the already high-performing **BGE embeddings**.

 Therefore, the final architecture uses **direct BGE retrieval** (`k=5` chunks) for **maximum speed and efficiency**.

---

##  Architecture and Components

PyCoach is organized into **three containerized services**, managed by `docker-compose.yml`:

| **Component** | **Description** | **Technologies** |
|----------------|-----------------|------------------|
| **backend** | FastAPI application coordinating RAG and Adaptive Logic. Handles `ChatRequest`, loads appropriate LLM, builds LCEL chain, and manages conversational history. | FastAPI, Uvicorn, LangChain (0.1.0), ChromaDB, ChatGoogleGenerativeAI, ChatOllama |
| **frontend** | Streamlit user interface managing session state, secure API key input, chat interface, and adaptive level selector. | Streamlit, Pandas (for data visualization) |
| **ollama** | Local service providing Llama 3 API, isolated via Docker for backend access over internal network. | Ollama, Llama 3 |

---

##  Security and Dependency Management

- **API Key Security:**  
  The insecure *Server Key* option has been removed.  
  All Gemini API usage requires the user to input their **personal key** securely via the Streamlit sidebar, protecting developer credentials.

- **Version Control:**  
  Uses a fixed `langchain==0.1.0` dependency stack (documented in `requirements.txt`), allowing robust custom logic (e.g., manual reranker implementation) without risk from breaking changes.

- **.gitignore Configuration:**  
  The `.env` file containing secrets is **explicitly excluded** from version control.

---

##  Setup and Installation (One-Click Deployment)

The entire system runs inside **Docker containers** — no manual dependency setup required.

### 🧩 Prerequisites
- **Docker Desktop** (or Docker Engine) installed and running.

---

### 🏗️ Installation Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/YourUsername/PyCoach.git
   cd PyCoach
2. **Prepare Course Materials**

  	Place your Python reference documents (PDFs, Markdown, or text files) into the local directory:
	```bash
	course_materials/
	```
3. **Authentication** 

	 Create a file named .env in the root directory and add your Gemini API Key:	
	```bash
	GEMINI_API_KEY="YOUR_API_KEY_HERE"
	```

4. **Build the Application Stack (Mandatory First Run)**

	This builds the Docker images, installs all necessary RAG libraries (unstructured, libgl1, etc.), and starts the services.
	```bash
	docker compose up --build -d
	```
	(Wait for this process to complete before moving to Step 5).	
5. **Build and Index the RAG Pipeline (MANDATORY)**

	Since the vector database (chroma_data) starts empty, you must run the indexing script inside the running backend container once.

	```bash
	docker compose exec backend python backend/rag_pipeline.py
	```
	Then, restart the backend to load the newly created vector store:
	```bash
	docker compose restart backend
	```

6. **Access the Application**
Open your browser and navigate to:

	 http://localhost:8501

7. When Finished
	Safely stop all services and free up resources:
	```bash
	docker compose down
	```
---
## Tech Stack Overview

 Backend: FastAPI, LangChain (LCEL), ChromaDB

 Frontend: Streamlit

Local Model Hosting: Ollama (Llama 3)

Cloud Model Option: Gemini API

Containerization: Docker & Docker Compose

Embeddings: BAAI/bge-small-en-v1.5 

---
## **Important Note on Local LLM (Ollama)**
### Due to frequent dependency conflicts and stability issues when running heavy local LLM services within a unified Docker Compose network Ollama has been removed from the primary docker-compose.yml file.
### The local Ollama implementation mentioned previously  (or available in the main.py code in gitignore file) is for local demonstration only and is not configured for deployment or user consumption in the current Dockerized stack. Users must provide a valid GEMINI_API_KEY to run the project.


## Author: Aviral Mishra 



## License: [MIT](https://github.com/AviralMishra039/Pycoach/blob/main/LICENSE)