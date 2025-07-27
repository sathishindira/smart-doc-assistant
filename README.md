# smart-doc-assistant
🤖 AI-powered document assistant that transforms PDFs and Confluence pages into intelligent design documents using RAG (Retrieval-Augmented Generation). Built with LangChain, Streamlit, and FAISS.

> Transform your scattered PDFs and Confluence pages into intelligent, contextual design documents using RAG (Retrieval-Augmented Generation)

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![LangChain](https://img.shields.io/badge/LangChain-0.1+-green.svg)](https://langchain.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🎯 What Does This Do?

Ever wished you could ask your documentation questions and get intelligent answers? Or automatically generate comprehensive design documents based on your existing knowledge base? This AI-powered document assistant does exactly that!

**Key Features:**
- 📄 **PDF Integration**: Upload and search through PDF documents
- 🌐 **Confluence Integration**: Connect to your Confluence spaces
- 🤖 **AI-Powered Search**: Find relevant information across all your docs
- 📋 **Smart Design Documents**: Generate comprehensive technical design documents
- 🔍 **Contextual Answers**: Get answers backed by your actual documentation

## 🚀 Quick Start

### 🎯 Recommended: Jupyter Notebook Approach
```bash
git clone https://github.com/sathishindira/smart-doc-assistant.git
cd smart-doc-assistant
pip install -r requirements.txt
jupyter notebook AI_Document_Assistant.ipynb
```

**Then run the cells in order:**
1. **Cell 1**: Install packages
2. **Cell 2**: Setup environment  
3. **Cell 3**: Configure Confluence (optional)
4. **Cell 4**: Initialize document processor
5. **Cell 5**: Setup design document generator
6. **Cell 6**: Launch Streamlit web interface

### ⚡ Alternative: Standalone Web App
```bash
python setup.py
streamlit run streamlit_app_fixed.py
```

## 📁 Project Structure

```
smart-doc-assistant/
├── 📓 Jupyter Notebooks
│   ├── AI_Document_Assistant.ipynb           # 🌟 Main notebook (START HERE)
├── 🐍 Python Components (extracted from notebooks)
│   ├── 01_setup_installation.py                   # Package installation
│   ├── 02_basic_setup.py                          # Environment setup
│   ├── 03_extract_confluence.py                   # Confluence integration
│   ├── 04_unified_processor.py                    # Document processing
│   ├── 05_design_doc_generator.py                 # AI document generation
│   ├── 06_streamlit_app.py                        # Web interface
│   ├── 07_main_runner.py                          # Application runner
│   └── 08_test_system.py                          # System testing
├── ⚙️ Setup & Configuration
│   ├── setup.py                                   # Automated setup
│   ├── requirements.txt                           # All dependencies
│   └── .env.example                               # Environment template
└──  README.md                                  # This file

```

## 🛠️ How It Works

### 1. Document Ingestion
- **PDFs**: Upload documents through the web interface
- **Confluence**: Connect using API tokens to ingest pages
- **Processing**: Documents are chunked and embedded using sentence transformers

### 2. Intelligent Search
- **Vector Search**: Uses FAISS for similarity search
- **Contextual Retrieval**: Finds relevant content across all document types
- **Source Attribution**: Shows exactly which documents informed each answer

### 3. Design Document Generation
- **RAG-Powered**: Uses retrieved content to generate contextual documents
- **Comprehensive Structure**: 13 detailed sections covering all aspects
- **Technical Analysis**: Extracts requirements, technologies, and patterns from your docs

## 🎮 Usage Examples

### Basic Document Search
```python
from unified_processor_fast import UnifiedDataProcessor

processor = UnifiedDataProcessor()
processor.add_pdf_documents(['my_document.pdf'])
results = processor.search_documents('authentication requirements')
```

### Generate Design Document
```python
from design_doc_generator import DesignDocumentGenerator

generator = DesignDocumentGenerator()
result = generator.generate_design_document(
    "User Authentication System with OAuth2 Integration"
)
print(result['document'])
```

### Web Interface
```bash
streamlit run streamlit_app.py
```
Then navigate to `http://localhost:8501`

## 🔧 Configuration

### Environment Variables
Create a `.env` file:
```env
# Confluence (Optional)
CONFLUENCE_URL=https://your-domain.atlassian.net
CONFLUENCE_USERNAME=your-email@domain.com
CONFLUENCE_API_TOKEN=your-api-token

# AWS (Optional - for enhanced AI features)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_DEFAULT_REGION=us-east-1
```

## 📊 Features in Detail

### 🔍 Smart Search
- **Multi-source**: Search across PDFs and Confluence simultaneously
- **Relevance Scoring**: Results ranked by similarity
- **Source Attribution**: See exactly which document provided each answer
- **Content Preview**: Quick preview of relevant sections

### 📋 Design Document Generation
- **13 Comprehensive Sections**: From overview to risk assessment
- **RAG-Enhanced**: Uses your actual documentation as context
- **Technical Analysis**: Extracts technologies, requirements, and patterns
- **Professional Format**: Ready-to-use technical documentation

### 🌐 Web Interface
- **User-Friendly**: Clean, intuitive Streamlit interface
- **Real-time Processing**: Upload and process documents instantly
- **Interactive Search**: Query your knowledge base interactively
- **Document Download**: Export generated documents as Markdown

## 🚀 Advanced Usage

### Batch Processing
```python
# Process multiple PDFs
processor.add_pdf_documents([
    'architecture_guide.pdf',
    'api_documentation.pdf',
    'security_policies.pdf'
])

# Ingest multiple Confluence pages
processor.add_confluence_documents([
    '123456789',  # Page ID 1
    '987654321',  # Page ID 2
])
```

### Custom Templates
```python
# Customize design document generation
generator = DesignDocumentGenerator()
result = generator.generate_design_document(
    user_request="Microservices Architecture",
    title="Custom Design Document Title"
)
```

## 🧪 Testing

Run the test suite:
```bash
python 08_test_system.py
```

Test individual components:
```python
# Test document processing
from unified_processor_fast import UnifiedDataProcessor
processor = UnifiedDataProcessor()

# Test design generation
from design_doc_generator import DesignDocumentGenerator
generator = DesignDocumentGenerator()
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **LangChain** for the RAG framework
- **Streamlit** for the amazing web interface
- **Sentence Transformers** for embeddings
- **FAISS** for vector search
- **Atlassian** for Confluence API

## 📞 Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/sathishindira/smart-doc-assistant/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/sathishindira/smart-doc-assistant/discussions)
- 📧 **Email**: sathishcitmech@gmail.com

---

**Made with ❤️ by developers, for developers**

*Transform your documentation workflow today!*