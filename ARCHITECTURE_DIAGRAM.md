# Smart Document Assistant - Architecture Diagram

## System Architecture

```
                    Smart Document Assistant Architecture
                    =====================================

┌─────────────────────────────────────────────────────────────────────────────┐
│                              INPUT LAYER                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐        │
│  │   PDF Upload    │    │   Confluence     │    │   Streamlit     │        │
│  │   Processing    │    │   Integration    │    │   Web UI        │        │
│  └─────────────────┘    └──────────────────┘    └─────────────────┘        │
│           │                        │                        │               │
└───────────┼────────────────────────┼────────────────────────┼───────────────┘
            │                        │                        │
            ▼                        ▼                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PROCESSING LAYER                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐        │
│  │   Document      │    │   Text Chunking  │    │   Embedding     │        │
│  │   Extraction    │───▶│   & Splitting    │───▶│   Generation    │        │
│  └─────────────────┘    └──────────────────┘    └─────────────────┘        │
│           │                        │                        │               │
└───────────┼────────────────────────┼────────────────────────┼───────────────┘
            │                        │                        │
            ▼                        ▼                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            STORAGE LAYER                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐        │
│  │   Vector Store  │    │   Metadata       │    │   Source        │        │
│  │   (FAISS)       │    │   Storage        │    │   Attribution   │        │
│  └─────────────────┘    └──────────────────┘    └─────────────────┘        │
│           │                        │                        │               │
└───────────┼────────────────────────┼────────────────────────┼───────────────┘
            │                        │                        │
            ▼                        ▼                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          INTELLIGENCE LAYER                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐        │
│  │   Similarity    │    │   RAG Engine     │    │   Design Doc    │        │
│  │   Search        │───▶│   & Context      │───▶│   Generator     │        │
│  └─────────────────┘    └──────────────────┘    └─────────────────┘        │
│           │                        │                        │               │
└───────────┼────────────────────────┼────────────────────────┼───────────────┘
            │                        │                        │
            ▼                        ▼                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            OUTPUT LAYER                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐        │
│  │   Search        │    │   Design         │    │   Source        │        │
│  │   Results       │    │   Documents      │    │   References    │        │
│  └─────────────────┘    └──────────────────┘    └─────────────────┘        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow

```
User Input → Document Processing → Vector Storage → Intelligent Search → Generated Output

1. User uploads PDFs or connects Confluence
2. Documents are chunked and embedded
3. Embeddings stored in FAISS vector database
4. User queries trigger similarity search
5. Relevant chunks retrieved with context
6. RAG engine generates contextual responses
7. Design documents created with source attribution
```

## Technology Stack

```
Frontend:           Streamlit
Document Processing: LangChain, PyMuPDF
Embeddings:         Sentence Transformers
Vector Store:       FAISS
Integration:        Atlassian Python API
AI Generation:      RAG with LangChain
Development:        Jupyter Notebooks
```

## Key Features

- **Multi-Source Integration**: PDFs + Confluence
- **Intelligent Search**: Vector similarity with relevance scoring
- **Contextual Generation**: RAG-powered design documents
- **Source Attribution**: Track which documents inform each response
- **Real-time Processing**: Upload and query instantly
- **Web Interface**: User-friendly Streamlit dashboard