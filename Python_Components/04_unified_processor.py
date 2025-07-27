from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from extract_confluence import ConfluenceProcessor
import os
import traceback
import sys

class UnifiedDataProcessor:
    def __init__(self, vector_store_path='./vector_store/'):
        self.vector_store_path = vector_store_path
        self.embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
        self.confluence_processor = ConfluenceProcessor()
        self.vectorstore = None
        os.makedirs(vector_store_path, exist_ok=True)
        self.load_existing_vectorstore()
    
    def load_existing_vectorstore(self):
        try:
            if os.path.exists(os.path.join(self.vector_store_path, 'index.faiss')):
                self.vectorstore = FAISS.load_local(
                    self.vector_store_path,
                    embeddings=self.embeddings,
                    allow_dangerous_deserialization=True
                )
                print('Loaded existing vector store')
            else:
                print('No existing vector store found')
        except Exception as e:
            print(f'Error loading existing vector store: {str(e)}')
            traceback.print_exc()
    
    def add_pdf_documents(self, pdf_paths, chunk_size=500):
        all_documents = []
        if isinstance(pdf_paths, str):
            pdf_paths = [pdf_paths]
        
        for pdf_path in pdf_paths:
            try:
                loader = PyPDFLoader(pdf_path)
                documents = loader.load()
                
                # FIXED: Enhanced metadata for better search results
                for i, doc in enumerate(documents):
                    doc.metadata['source'] = 'pdf'
                    doc.metadata['file_path'] = pdf_path
                    doc.metadata['file_name'] = os.path.basename(pdf_path)
                    doc.metadata['title'] = os.path.splitext(os.path.basename(pdf_path))[0]
                    doc.metadata['page'] = i + 1
                    doc.metadata['total_pages'] = len(documents)
                    
                    # Ensure content is meaningful
                    if not doc.page_content or len(doc.page_content.strip()) < 10:
                        doc.page_content = f'Content from {doc.metadata["title"]} - Page {doc.metadata["page"]}'
                
                all_documents.extend(documents)
                print(f'Loaded {len(documents)} pages from {os.path.basename(pdf_path)}')
            except Exception as e:
                print(f'Error processing PDF {pdf_path}: {str(e)}')
                traceback.print_exc()
        
        if all_documents:
            self._add_documents_to_vectorstore(all_documents, chunk_size)
    
    def add_confluence_documents(self, page_ids=None, chunk_size=500):
        try:
            confluence_vectorstore = self.confluence_processor.process_confluence_to_vectorstore(
                page_ids=page_ids, chunk_size=chunk_size
            )
            if confluence_vectorstore:
                if self.vectorstore is None:
                    self.vectorstore = confluence_vectorstore
                else:
                    self.vectorstore.merge_from(confluence_vectorstore)
                self.save_vectorstore()
                print('Successfully added Confluence documents to vector store')
            else:
                print('Failed to process Confluence documents')
        except Exception as e:
            print(f'Error adding Confluence documents: {str(e)}')
            traceback.print_exc()
    
    def _add_documents_to_vectorstore(self, documents, chunk_size):
        try:
            splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=100)
            chunks = splitter.split_documents(documents)
            print(f'Split into {len(chunks)} chunks.')
            
            if self.vectorstore is None:
                self.vectorstore = FAISS.from_documents(chunks, self.embeddings)
            else:
                new_vectorstore = FAISS.from_documents(chunks, self.embeddings)
                self.vectorstore.merge_from(new_vectorstore)
            
            self.save_vectorstore()
            print('Added documents to unified vector store.')
        except Exception as e:
            print(f'Error adding documents to vector store: {str(e)}')
            traceback.print_exc()
    
    def save_vectorstore(self):
        try:
            if self.vectorstore:
                self.vectorstore.save_local(self.vector_store_path)
                print(f'Vector store saved to {self.vector_store_path}')
        except Exception as e:
            print(f'Error saving vector store: {str(e)}')
            traceback.print_exc()
    
    def get_vectorstore(self):
        return self.vectorstore
    
    # FIXED: Enhanced search with proper error handling and source information
    def search_documents(self, query, k=5):
        if self.vectorstore is None:
            print('No vector store available')
            return []
        
        if not query or not query.strip():
            print('Empty query provided')
            return []
        
        try:
            print(f'Searching for: "{query}" (k={k})')
            results = self.vectorstore.similarity_search_with_score(query, k=k)
            print(f'Found {len(results)} results')
            
            # FIXED: Enhanced result formatting with source information
            formatted_results = []
            for doc, score in results:
                # Ensure all metadata fields exist
                metadata = doc.metadata.copy()
                metadata.setdefault('title', 'Unknown Document')
                metadata.setdefault('source', 'unknown')
                metadata.setdefault('file_name', 'Unknown File')
                
                formatted_results.append((doc, score))
            
            return formatted_results
        except Exception as e:
            print(f'Error searching documents: {str(e)}')
            print(f'Vector store type: {type(self.vectorstore)}')
            print(f'Query type: {type(query)}, length: {len(query) if query else 0}')
            traceback.print_exc()
            return []
    
    def get_confluence_status(self):
        return self.confluence_processor.get_connection_status()