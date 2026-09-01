# 🔐 Cybersecurity Analytics Platform - Integration Guide

## Overview

This document outlines how **Part 4 (AI Cybersecurity Assistant)** integrates with the other components of the complete cybersecurity analytics platform.

---

## 🏗️ Complete System Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                   CYBERSECURITY ANALYTICS PLATFORM                       │
│                                                                          │
│  Data Pipeline → ML Pipeline → Visualization + Intelligence             │
└──────────────────────────────────────────────────────────────────────────┘

PART 1: Data Pipeline (Foundation)
├─ Real-time KPI tracking
├─ Incident data collection
├─ 7-day trend analysis
├─ SQLite + JSON storage
└─ Output: cybersecurity_incidents.csv, kpi_metrics.json

        │
        ▼

PART 2: ML Pipeline (Intelligence)
├─ Data preprocessing & feature engineering
├─ Model training (classification, anomaly detection)
├─ Prediction generation
├─ Model evaluation & metrics
└─ Output: trained_model.pkl, predictions.csv, embeddings.json

        │
        ├─────────────────┬──────────────────┐
        │                 │                  │
        ▼                 ▼                  ▼
    PART 3:         PART 4:            PART 4:
    Dashboard       RAG Assistant      Incident Search
    (Visualization) (Chat + QA)        (Vector Search)
    
    • Incident Viz   • Chat Interface   • Semantic Search
    • Trend Charts   • RAG Pipeline     • Similar Incidents
    • Predictions    • SOP Retrieval    • Pattern Detection
    • ML Metrics     • Knowledge Base   • Recommendations
```

---

## 🔄 Data Integration Points

### **Part 1 → Part 4 Connection**

**What Part 1 Provides:**
- `cybersecurity_incidents.csv` - Historical incident records
- `kpi_metrics.json` - Aggregated KPI data with trends
- `sop_documents/` - Standard Operating Procedures
- `faq.json` - Frequently Asked Questions

**How Part 4 Uses It:**
```python
# Load incident data for knowledge base
incidents_df = pd.read_csv('data/cybersecurity_incidents.csv')

# Extract text for FAISS indexing
incident_texts = incidents_df['description'].tolist()

# Build embeddings and vector index
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectorstore = FAISS.from_texts(incident_texts, embeddings)

# Store for RAG retrieval
vectorstore.save_local("vectorstore/incidents_index")
```

### **Part 2 → Part 4 Connection**

**What Part 2 Provides:**
- `trained_model.pkl` - Trained classification model
- `feature_names.json` - Feature engineering metadata
- `model_metrics.json` - Model performance scores
- `predictions.csv` - Sample predictions with confidence scores

**How Part 4 Uses It:**
```python
# Load trained model for context-aware responses
model = joblib.load('models/trained_model.pkl')

# Use predictions for incident severity in search
predictions_df = pd.read_csv('data/predictions.csv')

# Enhance RAG responses with ML confidence scores
def get_incident_with_confidence(incident_id):
    prediction = predictions_df[predictions_df['id'] == incident_id]
    return {
        'incident': incident_data,
        'severity': prediction['predicted_severity'],
        'confidence': prediction['confidence_score']
    }
```

---

## 📂 Directory Structure for Integration

```
Part4-AI-Cybersecurity-Assistant/
├── data/
│   ├── cybersecurity_incidents.csv          # From Part 1
│   ├── kpi_metrics.json                     # From Part 1
│   ├── predictions.csv                      # From Part 2
│   ├── model_metrics.json                   # From Part 2
│   ├── sop_documents/
│   │   └── *.pdf, *.txt                     # SOPs from Part 1
│   └── knowledge_base/
│       ├── incidents/
│       ├── sops/
│       ├── faq/
│       └── procedures/
│
├── vectorstore/
│   ├── incidents_index/                     # FAISS index
│   ├── sop_index/                           # SOP embeddings
│   └── faq_index/                           # FAQ embeddings
│
├── models/
│   ├── trained_model.pkl                    # From Part 2
│   ├── feature_scaler.pkl                   # From Part 2
│   └── embeddings/
│       └── embedding_model.bin              # HF embeddings
│
└── src/
    ├── integrations/
    │   ├── part1_loader.py                  # Load Part 1 data
    │   ├── part2_loader.py                  # Load Part 2 models
    │   └── part3_sync.py                    # Sync with Part 3
    └── ...
```

---

## 🔧 Setup Instructions for Integration

### **Step 1: Data Pipeline Setup**

```bash
# Clone Part 1 repository
git clone https://github.com/pramodj551-oss/Part1-Cybersecurity-Data-Pipeline.git ../Part1-Data-Pipeline

# Run Part 1 to generate data
cd ../Part1-Data-Pipeline
python main.py

# Output files will be in:
# - cybersecurity_incidents.csv
# - kpi_metrics.json
```

### **Step 2: ML Pipeline Setup**

```bash
# Clone Part 2 repository
git clone https://github.com/pramodj551-oss/Part2-Cybersecurity-ML-Pipeline.git ../Part2-ML-Pipeline

# Run Part 2 to generate models
cd ../Part2-ML-Pipeline
python train.py

# Output files will be in:
# - models/trained_model.pkl
# - data/predictions.csv
```

### **Step 3: Copy Artifacts to Part 4**

```bash
# Copy incident data
cp ../Part1-Data-Pipeline/data/cybersecurity_incidents.csv ./data/

# Copy KPI metrics
cp ../Part1-Data-Pipeline/data/kpi_metrics.json ./data/

# Copy trained model
cp ../Part2-ML-Pipeline/models/trained_model.pkl ./models/

# Copy predictions
cp ../Part2-ML-Pipeline/data/predictions.csv ./data/
```

### **Step 4: Build Knowledge Base**

```bash
# Initialize the RAG knowledge base (automatic on first run)
streamlit run app.py

# Or manually build:
python src/vector_store.py --build-index
```

---

## 🔄 Data Synchronization Strategy

### **Automated Sync (Recommended)**

```python
# Create sync_repos.py
import os
import shutil
import subprocess
from datetime import datetime

class RepositorySync:
    def __init__(self, part4_path, part1_path, part2_path):
        self.part4_path = part4_path
        self.part1_path = part1_path
        self.part2_path = part2_path
    
    def sync_part1_data(self):
        """Copy data from Part 1"""
        files_to_sync = [
            'cybersecurity_incidents.csv',
            'kpi_metrics.json',
            'sop_documents/',
        ]
        
        for file in files_to_sync:
            src = os.path.join(self.part1_path, 'data', file)
            dst = os.path.join(self.part4_path, 'data', file)
            
            if os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dst)
        
        print(f"[{datetime.now()}] Part 1 data synced")
    
    def sync_part2_models(self):
        """Copy models from Part 2"""
        files_to_sync = [
            'trained_model.pkl',
            'feature_scaler.pkl',
        ]
        
        for file in files_to_sync:
            src = os.path.join(self.part2_path, 'models', file)
            dst = os.path.join(self.part4_path, 'models', file)
            shutil.copy2(src, dst)
        
        # Also sync predictions
        src = os.path.join(self.part2_path, 'data', 'predictions.csv')
        dst = os.path.join(self.part4_path, 'data', 'predictions.csv')
        shutil.copy2(src, dst)
        
        print(f"[{datetime.now()}] Part 2 models synced")
    
    def rebuild_indices(self):
        """Rebuild FAISS indices after data sync"""
        import subprocess
        subprocess.run(['python', 'src/vector_store.py', '--rebuild'], cwd=self.part4_path)
        print(f"[{datetime.now()}] Vector indices rebuilt")

# Usage
if __name__ == "__main__":
    syncer = RepositorySync(
        part4_path='.',
        part1_path='../Part1-Cybersecurity-Data-Pipeline',
        part2_path='../Part2-Cybersecurity-ML-Pipeline'
    )
    
    syncer.sync_part1_data()
    syncer.sync_part2_models()
    syncer.rebuild_indices()
```

---

## 📊 API Contracts

### **Data Schema: Incidents**

```python
# From Part 1 → Part 4
incident_schema = {
    'id': str,                          # Unique identifier
    'timestamp': datetime,              # When incident occurred
    'description': str,                 # Incident description
    'severity': str,                    # Low | Medium | High | Critical
    'source': str,                      # Detection source
    'indicators': List[str],            # IoCs, signatures, patterns
    'actions_taken': List[str],         # Response actions
    'resolution_time': float,           # Minutes to resolve
    'status': str,                      # Open | Resolved | Escalated
}

# From Part 2 → Part 4
prediction_schema = {
    'incident_id': str,
    'predicted_severity': str,
    'confidence_score': float,          # 0.0 - 1.0
    'predicted_resolution_time': float, # Hours
    'recommended_actions': List[str],
}
```

### **API Endpoints (Future REST API)**

```
GET  /api/v1/incidents              # List all incidents
GET  /api/v1/incidents/{id}         # Get specific incident
GET  /api/v1/incidents/search       # Search incidents
POST /api/v1/chat                   # RAG chat endpoint
GET  /api/v1/knowledge-base         # Browse knowledge base
GET  /api/v1/sops                   # Standard procedures
GET  /api/v1/predictions/{incident_id}  # Get ML predictions
```

---

## 🐳 Docker Compose for Multi-Repository Development

```yaml
# docker-compose.yml
version: '3.8'

services:
  part1-data-pipeline:
    build: ../Part1-Cybersecurity-Data-Pipeline
    container_name: cyber-data-pipeline
    volumes:
      - shared_data:/data
    environment:
      - DATA_OUTPUT_PATH=/data
    command: python main.py

  part2-ml-pipeline:
    build: ../Part2-Cybersecurity-ML-Pipeline
    container_name: cyber-ml-pipeline
    depends_on:
      - part1-data-pipeline
    volumes:
      - shared_data:/data
      - shared_models:/models
    environment:
      - DATA_PATH=/data
      - MODEL_OUTPUT_PATH=/models
    command: python train.py

  part3-dashboard:
    build: ../Part3-Cybersecurity-Dashboard
    container_name: cyber-dashboard
    ports:
      - "8501:8501"
    depends_on:
      - part2-ml-pipeline
    volumes:
      - shared_data:/data
      - shared_models:/models
    environment:
      - DATA_PATH=/data
      - MODEL_PATH=/models

  part4-rag-assistant:
    build: .
    container_name: cyber-rag-assistant
    ports:
      - "8502:8502"
    depends_on:
      - part1-data-pipeline
      - part2-ml-pipeline
    volumes:
      - shared_data:/data
      - shared_models:/models
      - ./vectorstore:/vectorstore
    environment:
      - DATA_PATH=/data
      - MODEL_PATH=/models
      - OLLAMA_API_BASE=http://ollama:11434
    command: streamlit run app.py --server.port=8502

  ollama:
    image: ollama/ollama:latest
    container_name: ollama-server
    ports:
      - "11434:11434"
    environment:
      - OLLAMA_MODELS=/models
    volumes:
      - ollama_data:/root/.ollama

volumes:
  shared_data:
  shared_models:
  ollama_data:
```

### **Run All Components:**
```bash
docker-compose up -d

# Access applications:
# Part 3 Dashboard: http://localhost:8501
# Part 4 RAG Assistant: http://localhost:8502
# Ollama API: http://localhost:11434
```

---

## 🧪 Testing Integration

### **End-to-End Test**

```bash
#!/bin/bash
# test_integration.sh

echo "Testing Part 1: Data Pipeline..."
cd ../Part1-Cybersecurity-Data-Pipeline
python -m pytest tests/ -v

echo "Testing Part 2: ML Pipeline..."
cd ../Part2-Cybersecurity-ML-Pipeline
python -m pytest tests/ -v

echo "Testing Part 4: RAG Assistant..."
cd ../Part4-AI-Cybersecurity-Assistant
python -m pytest tests/ -v

echo "Testing data flow..."
python tests/test_integration.py

echo "✅ All integration tests passed!"
```

---

## 📈 Performance Optimization

### **FAISS Index Optimization**

```python
# Tune FAISS for better performance
from faiss import read_index, write_index, IndexRefine

# For small indices (<10K docs), use flat index (exact search)
index = faiss.IndexFlatL2(embedding_dim)

# For large indices (>10K docs), use IVF (faster approximate search)
quantizer = faiss.IndexFlatL2(embedding_dim)
index = faiss.IndexIVFFlat(quantizer, embedding_dim, nlist=100)

# Save optimized index
faiss.write_index(index, 'vectorstore/optimized_index.faiss')
```

---

## 🔐 Security Considerations

1. **Data Privacy**: All data stays local (Ollama LLM runs locally)
2. **Access Control**: Use GitHub secrets for API keys
3. **Data Validation**: Validate all inputs from Part 1/2
4. **Audit Logging**: Log all RAG retrievals and responses
5. **Incident Anonymization**: Remove PII before embedding

---

## 📚 Additional Resources

- Part 1 Repo: https://github.com/pramodj551-oss/Part1-Cybersecurity-Data-Pipeline
- Part 2 Repo: https://github.com/pramodj551-oss/Part2-Cybersecurity-ML-Pipeline
- Part 3 Repo: https://github.com/pramodj551-oss/Part3-Cybersecurity-Dashboard
- Ollama Docs: https://ollama.com
- FAISS Docs: https://github.com/facebookresearch/faiss

---

## 🤝 Contributing

See each repository's CONTRIBUTING.md for contribution guidelines.

---

**Last Updated:** September 1, 2026  
**Maintained by:** Pramod Prakash Jadhav
