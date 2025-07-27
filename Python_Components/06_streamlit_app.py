import streamlit as st
import os
import sys
import tempfile
import traceback
from io import BytesIO
import pandas as pd
from datetime import datetime
import json

# Import our modules with fallback handling
try:
    from unified_processor_fixed import UnifiedDataProcessor
except ImportError:
    try:
        from unified_processor import UnifiedDataProcessor
    except ImportError:
        from unified_processor_fast import UnifiedDataProcessor

try:
    from design_doc_generator_fixed import DesignDocumentGenerator
except ImportError:
    from design_doc_generator import DesignDocumentGenerator

try:
    from extract_confluence_fixed import ConfluenceProcessor
except ImportError:
    from extract_confluence import ConfluenceProcessor

st.set_page_config(
    page_title='AI Document Assistant (FIXED)',
    page_icon='📚',
    layout='wide',
    initial_sidebar_state='expanded'
)

@st.cache_resource
def initialize_processor():
    return UnifiedDataProcessor()

@st.cache_resource
def initialize_confluence():
    return ConfluenceProcessor()

def initialize_doc_generator():
    try:
        return DesignDocumentGenerator()
    except Exception as e:
        st.session_state.doc_generator_error = str(e)
        return None

# Initialize components
if 'processor' not in st.session_state:
    st.session_state.processor = initialize_processor()

if 'confluence_processor' not in st.session_state:
    st.session_state.confluence_processor = initialize_confluence()

# Header
st.title('📚 AI Document Assistant (FIXED)')
st.markdown('**RAG System with Enhanced PDF and Confluence Integration**')

# Sidebar - System Status
with st.sidebar:
    st.title('🔧 System Status')
    
    # Vector store status
    vectorstore = st.session_state.processor.get_vectorstore()
    has_documents = vectorstore is not None
    
    if has_documents:
        try:
            doc_count = vectorstore.index.ntotal if hasattr(vectorstore, 'index') else 'unknown'
            st.success(f'✅ Vector Store: {doc_count} vectors')
        except:
            st.success('✅ Vector Store: Active')
    else:
        st.warning('⚠️ No documents loaded')
    
    # Confluence status
    confluence_status = st.session_state.processor.get_confluence_status()
    if confluence_status['available']:
        st.success(f'✅ Confluence: Connected')
    else:
        st.error(f'❌ Confluence: {confluence_status["error"]}')

# Main content tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(['🔍 Query Documents', '📄 Upload PDFs', '🌐 Confluence Integration', '📋 Generate Design Doc', '🧪 System Test'])

# Query Documents tab
with tab1:
    st.header('🔍 Query Your Documents')
    
    if not has_documents:
        st.warning('⚠️ No documents available. Please upload PDFs or ingest Confluence data first.')
    else:
        col1, col2 = st.columns([3, 1])
        with col1:
            query = st.text_input('Enter your question:', placeholder='What would you like to know?')
        with col2:
            k_results = st.slider('Results:', 1, 10, 5)
        
        if st.button('🔍 Search', type='primary', use_container_width=True):
            if query:
                with st.spinner('🔍 Searching documents...'):
                    try:
                        results = st.session_state.processor.search_documents(query, k=k_results)
                        
                        if results:
                            st.success(f'✅ Found {len(results)} relevant results')
                            
                            for i, (doc, score) in enumerate(results, 1):
                                with st.expander(f'📄 Result {i} - Relevance Score: {score:.4f}'):
                                    col1, col2 = st.columns([1, 1])
                                    
                                    with col1:
                                        st.markdown(f'**Source:** {doc.metadata.get("source", "unknown")}')
                                        st.markdown(f'**Title:** {doc.metadata.get("title", "Unknown")}')
                                        if doc.metadata.get('page'):
                                            st.markdown(f'**Page:** {doc.metadata.get("page")}')
                                    
                                    with col2:
                                        if doc.metadata.get('url'):
                                            st.markdown(f'**URL:** [Link]({doc.metadata.get("url")})')
                                        if doc.metadata.get('file_name'):
                                            st.markdown(f'**File:** {doc.metadata.get("file_name")}')
                                    
                                    st.markdown('**Content:**')
                                    st.text_area('Content', doc.page_content, height=150, key=f'content_{i}', label_visibility='collapsed')
                        else:
                            st.warning('❌ No relevant results found')
                    except Exception as e:
                        st.error(f'❌ Search error: {str(e)}')
                        st.code(traceback.format_exc())
            else:
                st.warning('⚠️ Please enter a search query')

# Upload PDFs tab
with tab2:
    st.header('📄 Upload PDF Documents')
    
    uploaded_files = st.file_uploader(
        'Choose PDF files',
        type=['pdf'],
        accept_multiple_files=True,
        help='Upload one or more PDF files to add to the knowledge base'
    )
    
    col1, col2 = st.columns([1, 1])
    with col1:
        chunk_size = st.slider('Chunk Size:', 200, 1000, 500, step=50)
    with col2:
        st.info(f'Recommended: 500 for balanced performance')
    
    if uploaded_files:
        st.write(f'📁 Selected {len(uploaded_files)} file(s):')
        for file in uploaded_files:
            st.write(f'• {file.name} ({file.size:,} bytes)')
        
        if st.button('📤 Process PDFs', type='primary', use_container_width=True):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                temp_files = []
                for i, uploaded_file in enumerate(uploaded_files):
                    status_text.text(f'Processing {uploaded_file.name}...')
                    progress_bar.progress((i + 1) / len(uploaded_files))
                    
                    # Save to temporary file
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        temp_files.append(tmp_file.name)
                
                # Process all files
                status_text.text('Adding to vector store...')
                st.session_state.processor.add_pdf_documents(temp_files, chunk_size=chunk_size)
                
                # Cleanup
                for temp_file in temp_files:
                    try:
                        os.unlink(temp_file)
                    except:
                        pass
                
                progress_bar.progress(1.0)
                status_text.text('✅ Processing complete!')
                st.success(f'✅ Successfully processed {len(uploaded_files)} PDF file(s)')
                st.rerun()
                
            except Exception as e:
                st.error(f'❌ Error processing PDFs: {str(e)}')
                st.code(traceback.format_exc())

# Confluence Integration tab
with tab3:
    st.header('🌐 Confluence Integration')
    
    # Show connection status
    confluence_status = st.session_state.processor.get_confluence_status()
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader('Connection Status')
        if confluence_status['available']:
            st.success('✅ Connected to Confluence')
            st.info(f"URL: {confluence_status['url']}")
            st.info(f"User: {confluence_status['username']}")
        else:
            st.error('❌ Confluence not available')
            st.error(f"Error: {confluence_status['error']}")
    
    with col2:
        st.subheader('Configuration')
        st.info('Set these environment variables:')
        st.code('''
CONFLUENCE_URL=https://your-domain.atlassian.net
CONFLUENCE_USERNAME=your-email@domain.com
CONFLUENCE_API_TOKEN=your-api-token
        ''')
    
    if confluence_status['available']:
        st.subheader('📄 Ingest Confluence Pages')
        
        page_ids_input = st.text_area(
            'Page IDs (one per line):',
            placeholder='123456789\n987654321\n...',
            help='Enter Confluence page IDs, one per line'
        )
        
        col1, col2 = st.columns([1, 1])
        with col1:
            chunk_size = st.slider('Chunk Size:', 200, 1000, 500, step=50, key='confluence_chunk')
        with col2:
            st.info('Smaller chunks = more precise search')
        
        if st.button('📥 Ingest Pages', type='primary', use_container_width=True):
            if page_ids_input.strip():
                page_ids = [pid.strip() for pid in page_ids_input.strip().split('\n') if pid.strip()]
                
                with st.spinner(f'🔄 Processing {len(page_ids)} Confluence page(s)...'):
                    try:
                        st.session_state.processor.add_confluence_documents(
                            page_ids=page_ids,
                            chunk_size=chunk_size
                        )
                        st.success(f'✅ Successfully processed {len(page_ids)} Confluence page(s)')
                        st.rerun()
                    except Exception as e:
                        st.error(f'❌ Error processing Confluence pages: {str(e)}')
                        st.code(traceback.format_exc())
            else:
                st.warning('⚠️ Please enter at least one page ID')

# Generate Design Doc tab
with tab4:
    st.header('📋 Generate Design Document')
    
    if not has_documents:
        st.warning('⚠️ No documents available. Upload PDFs or ingest Confluence data first for better results.')
    
    col1, col2 = st.columns([2, 1])
    with col1:
        user_request = st.text_area(
            'Describe what you want to build:',
            placeholder='e.g., A microservice for user authentication with OAuth2 integration...',
            height=100
        )
    with col2:
        doc_title = st.text_input(
            'Document Title (optional):',
            placeholder='Auto-generated if empty'
        )
    
    if st.button('📋 Generate Design Document', type='primary', use_container_width=True):
        if user_request.strip():
            with st.spinner('🤖 Generating design document...'):
                try:
                    # Initialize doc generator
                    doc_generator = initialize_doc_generator()
                    
                    if doc_generator:
                        result = doc_generator.generate_design_document(
                            user_request=user_request.strip(),
                            title=doc_title.strip() if doc_title.strip() else None
                        )
                        
                        st.success('✅ Design document generated successfully!')
                        
                        # Display metadata
                        col1, col2, col3 = st.columns([1, 1, 1])
                        with col1:
                            st.metric('Sources Used', result['metadata']['source_count'])
                        with col2:
                            st.metric('LLM Type', result['metadata']['llm_used'])
                        with col3:
                            st.metric('Generated', result['metadata']['timestamp'])
                        
                        # Display document
                        st.subheader('📄 Generated Document')
                        st.markdown(result['document'])
                        
                        # Download button
                        st.download_button(
                            label='💾 Download Document',
                            data=result['document'],
                            file_name=f"design_doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                            mime='text/markdown',
                            use_container_width=True
                        )
                        
                        # Show sources
                        if result['sources']:
                            with st.expander('📚 Sources Used'):
                                for i, source in enumerate(result['sources'], 1):
                                    st.write(f"{i}. **{source['title']}** ({source['type']}) - Score: {source['score']:.3f}")
                                    if source.get('url'):
                                        st.write(f"   🔗 [Link]({source['url']})")
                    else:
                        st.error('❌ Failed to initialize document generator')
                        if hasattr(st.session_state, 'doc_generator_error'):
                            st.error(f"Error: {st.session_state.doc_generator_error}")
                
                except Exception as e:
                    st.error(f'❌ Error generating document: {str(e)}')
                    st.code(traceback.format_exc())
        else:
            st.warning('⚠️ Please describe what you want to build')

# System Test tab
with tab5:
    st.header('🧪 System Test & Diagnostics')
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader('🔍 Component Status')
        
        # Test vector store
        if st.button('Test Vector Store', use_container_width=True):
            try:
                vectorstore = st.session_state.processor.get_vectorstore()
                if vectorstore:
                    # Try a simple search
                    test_results = st.session_state.processor.search_documents('test', k=1)
                    st.success(f'✅ Vector store working - {len(test_results)} results')
                else:
                    st.warning('⚠️ No vector store available')
            except Exception as e:
                st.error(f'❌ Vector store error: {str(e)}')
        
        # Test Confluence
        if st.button('Test Confluence', use_container_width=True):
            try:
                status = st.session_state.processor.get_confluence_status()
                if status['available']:
                    st.success('✅ Confluence connection working')
                else:
                    st.error(f'❌ Confluence error: {status["error"]}')
            except Exception as e:
                st.error(f'❌ Confluence test error: {str(e)}')
        
        # Test Document Generator
        if st.button('Test Document Generator', use_container_width=True):
            try:
                doc_gen = initialize_doc_generator()
                if doc_gen:
                    st.success('✅ Document generator initialized')
                else:
                    st.error('❌ Document generator failed to initialize')
            except Exception as e:
                st.error(f'❌ Document generator error: {str(e)}')
    
    with col2:
        st.subheader('📊 System Information')
        
        # Environment variables
        env_vars = ['CONFLUENCE_URL', 'CONFLUENCE_USERNAME', 'CONFLUENCE_API_TOKEN']
        st.write('**Environment Variables:**')
        for var in env_vars:
            value = os.getenv(var, 'Not set')
            if var == 'CONFLUENCE_API_TOKEN' and value != 'Not set':
                value = f'{value[:8]}...' if len(value) > 8 else '***'
            st.write(f'• {var}: {value}')
        
        # File system
        st.write('**File System:**')
        vector_store_path = './vector_store/'
        if os.path.exists(vector_store_path):
            files = os.listdir(vector_store_path)
            st.write(f'• Vector store files: {len(files)}')
            for file in files[:5]:  # Show first 5 files
                st.write(f'  - {file}')
        else:
            st.write('• Vector store directory: Not found')
    
    # Clear data section
    st.subheader('🗑️ Data Management')
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button('🗑️ Clear Vector Store', type='secondary', use_container_width=True):
            try:
                vector_store_path = './vector_store/'
                if os.path.exists(vector_store_path):
                    import shutil
                    shutil.rmtree(vector_store_path)
                    st.success('✅ Vector store cleared')
                    st.rerun()
                else:
                    st.info('ℹ️ No vector store to clear')
            except Exception as e:
                st.error(f'❌ Error clearing vector store: {str(e)}')
    
    with col2:
        if st.button('🔄 Restart Components', type='secondary', use_container_width=True):
            try:
                # Clear cached resources
                st.cache_resource.clear()
                # Reset session state
                for key in ['processor', 'confluence_processor']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.success('✅ Components restarted')
                st.rerun()
            except Exception as e:
                st.error(f'❌ Error restarting: {str(e)}')

# Footer
st.markdown('---')
st.markdown('**AI Document Assistant** - Enhanced RAG system with PDF and Confluence integration')