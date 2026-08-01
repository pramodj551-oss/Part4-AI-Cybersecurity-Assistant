# 🛡️ AI-Powered Cybersecurity Incident Assistant (RAG)

**Part 4 – End-to-End Applied AI & ML Capstone Project**

An intelligent Retrieval-Augmented Generation (RAG) assistant that helps cybersecurity analysts search incidents, retrieve Standard Operating Procedures (SOPs), answer security-related questions, and provide context-aware responses using a locally-hosted Large Language Model (via Ollama) and a FAISS vector database.

---

## 📌 Project Overview

The AI-Powered Cybersecurity Incident Assistant combines Machine Learning, Retrieval-Augmented Generation (RAG), vector search, and Large Language Models to help Security Operations Center (SOC) analysts investigate incidents faster and more accurately.

Rather than relying solely on the LLM's internal knowledge, the assistant retrieves relevant information from a cybersecurity knowledge base — incident history, SOPs, and FAQs — before generating a response. This grounds every answer in your organization's own documentation, reducing hallucinations and improving answer relevance.

---

## 🎯 Project Objectives

- Build an end-to-end RAG pipeline
- Retrieve relevant cybersecurity knowledge
- Answer SOC analyst questions
- Recommend Standard Operating Procedures (SOPs)
- Search historical incidents
- Reduce LLM hallucinations
- Provide source-aware responses
- Deliver an interactive Streamlit chatbot

---

## 🚀 Key Features

- AI-powered cybersecurity assistant
- Retrieval-Augmented Generation (RAG)
- Vector similarity search (FAISS)
- Knowledge base search
- SOP retrieval
- Incident search
- Interactive Streamlit chat interface
- Conversation history
- Modular, extensible architecture
- Runs entirely locally via Ollama — no data leaves your machine

---

## 🏗️ Architecture

```text
User Question
      │
      ▼
Streamlit Chat Interface
      │
      ▼
Retriever
      │
      ▼
Vector Database (FAISS)
      │
      ▼
Relevant Documents
      │
      ▼
Prompt Builder
      │
      ▼
Large Language Model (Ollama)
      │
      ▼
AI Response + Sources
```

---

## 📁 Project Structure

```text
Part4-AI-Cybersecurity-Assistant/
│
├── app.py
├── requirements.txt
├── README.md
├── LICENSE
├── CHANGELOG.md
├── .gitignore
│
├── config/
│   └── config.py
│
├── data/
│   ├── cybersecurity_incidents.csv
│   ├── faq.csv
│   ├── sop_documents/
│   └── knowledge_base/
│
├── prompts/
│   └── system_prompt.txt
│
├── vectorstore/
│
├── models/
│
├── src/
│   ├── data_loader.py
│   ├── document_loader.py
│   ├── text_splitter.py
│   ├── embeddings.py
│   ├── vector_store.py
│   ├── retriever.py
│   ├── llm.py
│   ├── rag_pipeline.py
│   ├── response_generator.py
│   └── utils.py
│
├── pages/
│   ├── Chat.py
│   ├── Knowledge_Base.py
│   ├── Incident_Search.py
│   └── Settings.py
│
├── assets/
└── logs/
```

---

## 🛠️ Technology Stack

- Python 3.10+
- Streamlit
- LangChain
- FAISS
- Hugging Face Sentence Transformers (embeddings)
- Ollama (local LLM serving, via OpenAI-compatible API)
- Pandas / NumPy
- Scikit-learn
- Plotly
- Joblib

---

## ▶️ Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/Part4-AI-Cybersecurity-Assistant.git
cd Part4-AI-Cybersecurity-Assistant
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up Ollama

This project uses [Ollama](https://ollama.com) to serve the LLM locally.

```bash
ollama pull <your-model-name>
ollama serve
```

Make sure `LLM_MODEL` in `config/config.py` exactly matches the model name shown by `ollama list`, and that `API_BASE_URL` points at your local Ollama server's OpenAI-compatible endpoint.

### 4. Build the knowledge base

On first run, the app loads documents from `data/`, chunks them, generates embeddings, and builds the FAISS index. This step requires internet access the first time, to download the embedding model.

### 5. Run the application

```bash
streamlit run app.py
```

---

## 📌 Project Workflow

1. Load cybersecurity knowledge base (incidents, SOPs, FAQs)
2. Split documents into chunks
3. Generate embeddings
4. Build FAISS vector index
5. Retrieve relevant documents for a query
6. Build a contextual prompt
7. Generate an AI response via the local LLM
8. Display the answer alongside its retrieved sources

---

## 🧭 Project Status

This is an actively developed capstone project. The core RAG pipeline (retrieval → prompting → generation) is functional end-to-end. Known areas still being hardened:

- Error handling for missing/uninitialized vector index
- Graceful fallback when retrieval returns no relevant documents
- Consistent success/error response schema across the pipeline
- Live system health checks (LLM reachability, index status) on the home page

See `CHANGELOG.md` for details as these are addressed.

---

## 🔮 Future Enhancements

- Hybrid search (keyword + vector)
- Multi-document RAG
- Conversation memory
- Explainable AI
- Authentication
- Docker support
- REST API
- Cloud deployment
- Model monitoring
- Multi-LLM provider support

---

## 📄 License

This project is licensed under the MIT License.

---

## 👨‍💻 Author

**Pramod Prakash Jadhav**
AI/ML Developer | SOC & Cybersecurity Professional

---

## ⭐ Version

Version 4.0
