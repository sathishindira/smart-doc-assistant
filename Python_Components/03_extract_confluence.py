from atlassian import Confluence
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
import os
import traceback
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()

class ConfluenceProcessor:
    def __init__(self):
        self.confluence = None
        self.available = False
        self.error_message = None
        
        # FIXED: Proper validation of Confluence credentials
        confluence_url = os.getenv('CONFLUENCE_URL', '').strip()
        confluence_username = os.getenv('CONFLUENCE_USERNAME', '').strip()
        confluence_token = os.getenv('CONFLUENCE_API_TOKEN', '').strip()
        
        if not confluence_url or not confluence_username or not confluence_token:
            self.error_message = 'Missing Confluence credentials (URL, USERNAME, or API_TOKEN)'
            print(f'Confluence not configured: {self.error_message}')
            return
        
        try:
            self.confluence = Confluence(
                url=confluence_url,
                username=confluence_username,
                password=confluence_token
            )
            
            # FIXED: Test actual connection
            test_result = self.confluence.get_all_spaces(start=0, limit=1)
            if test_result:
                self.available = True
                self.embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
                print('Confluence connection verified')
            else:
                self.error_message = 'Unable to fetch spaces - check permissions'
                print(f'Confluence test failed: {self.error_message}')
        except Exception as e:
            self.error_message = f'Connection failed: {str(e)}'
            print(f'Confluence connection error: {self.error_message}')
    
    def get_connection_status(self):
        return {
            'available': self.available,
            'error': self.error_message,
            'url': os.getenv('CONFLUENCE_URL', 'Not set'),
            'username': os.getenv('CONFLUENCE_USERNAME', 'Not set')
        }
    
    def clean_html_content(self, html_content):
        if not html_content:
            return ''
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            for script in soup(['script', 'style']):
                script.decompose()
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split('  '))
            text = ' '.join(chunk for chunk in chunks if chunk)
            return text
        except Exception as e:
            print(f'Error cleaning HTML: {e}')
            return str(html_content)[:1000]
    
    def get_page_content(self, page_id):
        if not self.available:
            return None
        try:
            page = self.confluence.get_page_by_id(page_id, expand='body.storage,version,space')
            title = page['title']
            content = page['body']['storage']['value']
            space_key = page['space']['key']
            clean_content = self.clean_html_content(content)
            return {
                'title': title,
                'content': clean_content,
                'page_id': page_id,
                'space_key': space_key,
                'url': f"{os.getenv('CONFLUENCE_URL')}/pages/viewpage.action?pageId={page_id}"
            }
        except Exception as e:
            print(f'Error fetching page {page_id}: {str(e)}')
            return None
    
    def process_confluence_to_vectorstore(self, page_ids=None, chunk_size=500):
        if not self.available:
            print(f'Confluence not available: {self.error_message}')
            return None
        
        documents = []
        if page_ids:
            for page_id in page_ids:
                page_data = self.get_page_content(page_id)
                if page_data:
                    doc = Document(
                        page_content=f"Title: {page_data['title']}\n\n{page_data['content']}",
                        metadata={
                            'source': 'confluence',
                            'title': page_data['title'],
                            'page_id': page_data['page_id'],
                            'space_key': page_data['space_key'],
                            'url': page_data['url']
                        }
                    )
                    documents.append(doc)
        
        if not documents:
            print('No documents found to process')
            return None
        
        print(f'Loaded {len(documents)} documents from Confluence')
        splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=100)
        chunks = splitter.split_documents(documents)
        print(f'Split into {len(chunks)} chunks.')
        vectorstore = FAISS.from_documents(chunks, self.embeddings)
        print('Stored Confluence chunks in FAISS vector store.')
        return vectorstore