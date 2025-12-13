"""Streamlit frontend for Syllabus Gap Analyzer."""
import streamlit as st
import requests
import json
from pathlib import Path
import time

# Backend API URL - using all interfaces
BACKEND_URL = "http://desktop-machine.tailac2e85.ts.net:8000"

# Page configuration
st.set_page_config(
    page_title="Syllabus Gap Analyzer",
    page_icon="📚",
    layout="wide"
)

# Initialize session state
if "document_id" not in st.session_state:
    st.session_state.document_id = None
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None
if "search_completed" not in st.session_state:
    st.session_state.search_completed = False

# Title
st.title("📚 Syllabus Gap Analyzer")
st.markdown("Compare your syllabus PDF against industry job descriptions to identify gaps and viable topics.")

# Sidebar
with st.sidebar:
    st.header("Settings")
    backend_url = st.text_input("Backend URL", value=BACKEND_URL)
    
    st.header("Session Info")
    if st.session_state.document_id:
        st.success(f"Document ID: {st.session_state.document_id[:8]}...")
    else:
        st.info("No document uploaded")
    
    if st.session_state.conversation_id:
        st.success(f"Conversation ID: {st.session_state.conversation_id[:8]}...")
    else:
        st.info("No conversation started")
    
    if st.button("Clear Session"):
        st.session_state.document_id = None
        st.session_state.conversation_id = None
        st.session_state.search_completed = False
        st.session_state.messages = []  # Clear chat history
        st.rerun()

# Main tabs
tab1, tab2, tab3, tab4 = st.tabs(["📄 Upload PDF", "🔍 Search Jobs", "📊 Analyze Gaps", "💬 Chat"])

# Tab 1: Upload PDF
with tab1:
    st.header("Upload Syllabus PDF")
    st.markdown("Upload your syllabus PDF to extract topics and prepare for analysis.")
    
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    
    if uploaded_file is not None:
        if st.button("Upload and Extract Topics", type="primary"):
            with st.spinner("Uploading PDF and extracting topics..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.read(), "application/pdf")}
                    response = requests.post(f"{backend_url}/pdf", files=files, timeout=120)
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.session_state.document_id = result["document_id"]
                        st.session_state.conversation_id = None  # Reset conversation
                        st.session_state.search_completed = False
                        
                        st.success(f"✅ PDF uploaded successfully!")
                        st.json({
                            "document_id": result["document_id"],
                            "topic_extract_status": result["topic_extract_status"],
                            "text_preview": result["extracted_text_preview"][:200] + "..."
                        })
                        st.info("You can now proceed to search for jobs or use the chat interface.")
                        st.rerun()
                    else:
                        st.error(f"Upload failed: {response.status_code} - {response.text}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Error connecting to backend: {str(e)}")
                    st.info("Make sure the backend server is running at " + backend_url)

# Tab 2: Search Jobs
with tab2:
    st.header("Search for Job Descriptions")
    st.markdown("Search for industry job descriptions based on your criteria.")
    
    if not st.session_state.document_id:
        st.warning("⚠️ Please upload a PDF first in the 'Upload PDF' tab.")
    else:
        search_instruction = st.text_area(
            "Search Instructions",
            value="Find Data Engineer and Database Administrator jobs from top companies in the last 30 days in the US",
            height=100,
            help="Describe what types of jobs you want to search for"
        )
        
        if st.button("Search Jobs", type="primary"):
            with st.spinner("Searching for job descriptions... This may take a minute."):
                try:
                    payload = {
                        "message": search_instruction,
                        "document_id": st.session_state.document_id
                    }
                    response = requests.post(f"{backend_url}/chat", json=payload, timeout=300)
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.session_state.conversation_id = result["conversation_id"]
                        
                        st.success(f"✅ {result['response']}")
                        
                        tool_calls = result.get("tool_calls")
                        if tool_calls:
                            st.json(tool_calls)
                        
                        st.session_state.search_completed = True
                        st.info("Search completed! You can now analyze gaps in the 'Analyze Gaps' tab.")
                    else:
                        st.error(f"Search failed: {response.status_code} - {response.text}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Error connecting to backend: {str(e)}")

# Tab 3: Analyze Gaps
with tab3:
    st.header("Analyze Syllabus vs Industry Gaps")
    st.markdown("Generate gap analysis tables comparing syllabus topics with industry requirements.")
    
    if not st.session_state.document_id:
        st.warning("⚠️ Please upload a PDF first in the 'Upload PDF' tab.")
    elif not st.session_state.conversation_id:
        st.warning("⚠️ Please search for jobs first in the 'Search Jobs' tab.")
    else:
        if st.button("Generate Analysis", type="primary"):
            with st.spinner("Analyzing gaps... This may take a minute."):
                try:
                    payload = {
                        "message": "Analyze the syllabus topics against the job descriptions and show me the gaps",
                        "conversation_id": st.session_state.conversation_id,
                        "document_id": st.session_state.document_id
                    }
                    response = requests.post(f"{backend_url}/chat", json=payload, timeout=300)
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        st.success("✅ Analysis complete!")
                        st.markdown(result.get("response", ""))
                        
                        tables = result.get("tables")
                        if tables:
                            # Table A: Viable Topics
                            table_a = tables.get("table_a", [])
                            if table_a:
                                st.subheader("📋 Table A: Syllabus Topics Still Viable in Industry")
                                
                                for i, row in enumerate(table_a, 1):
                                    with st.expander(f"{i}. {row.get('syllabus_topic', 'N/A')} - Relevance: {row.get('industry_relevance_score', 0)}%"):
                                        col1, col2 = st.columns(2)
                                        with col1:
                                            st.metric("Evidence Jobs", row.get('evidence_job_count', 0))
                                            st.write("**Industry Phrasing:**")
                                            st.write(row.get('example_industry_phrasing', 'N/A'))
                                        with col2:
                                            st.write("**Notes:**")
                                            st.write(row.get('notes', 'N/A'))
                                        
                                        references = row.get('references', [])
                                        if references:
                                            st.write("**References:**")
                                            for ref in references:
                                                st.markdown(f"- [{ref}]({ref})")
                            
                            # Table B: Missing Topics
                            table_b = tables.get("table_b", [])
                            if table_b:
                                st.subheader("📋 Table B: Missing Topics to Add to Syllabus")
                                
                                for i, row in enumerate(table_b, 1):
                                    priority_color = {
                                        "High": "🔴",
                                        "Medium": "🟡",
                                        "Low": "🟢"
                                    }.get(row.get('priority', 'Medium'), '⚪')
                                    
                                    with st.expander(f"{priority_color} {i}. {row.get('missing_topic', 'N/A')} - Priority: {row.get('priority', 'N/A')}"):
                                        col1, col2 = st.columns(2)
                                        with col1:
                                            st.metric("Frequency in Jobs", row.get('frequency_in_jobs', 0))
                                            st.write("**Suggested Insertion:**")
                                            st.write(row.get('suggested_syllabus_insertion', 'N/A'))
                                        with col2:
                                            st.write("**Rationale:**")
                                            st.write(row.get('rationale', 'N/A'))
                                        
                                        references = row.get('references', [])
                                        if references:
                                            st.write("**References:**")
                                            for ref in references:
                                                st.markdown(f"- [{ref}]({ref})")
                        else:
                            st.warning("No tables found in response")
                    else:
                        st.error(f"Analysis failed: {response.status_code} - {response.text}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Error connecting to backend: {str(e)}")

# Tab 4: Chat Interface
with tab4:
    st.header("💬 Chat Interface")
    st.markdown("Interact with the system using natural language. The AI will automatically call search or analysis tools as needed.")
    
    # PDF Upload in Chat - Always visible
    col1, col2 = st.columns([3, 1])
    with col1:
        uploaded_file = st.file_uploader("📄 Upload PDF here (drag & drop or browse)", type="pdf", key="chat_pdf_uploader", help="Upload a syllabus PDF to analyze")
    with col2:
        upload_button = st.button("Upload", type="primary", key="chat_upload_btn", disabled=(uploaded_file is None))
    
    # Handle PDF upload
    if uploaded_file is not None and upload_button:
        with st.spinner("Uploading PDF and extracting topics..."):
            try:
                # Reset file pointer
                uploaded_file.seek(0)
                files = {"file": (uploaded_file.name, uploaded_file.read(), "application/pdf")}
                response = requests.post(f"{backend_url}/pdf", files=files, timeout=120)
                
                if response.status_code == 200:
                    result = response.json()
                    st.session_state.document_id = result["document_id"]
                    
                    # Initialize messages if needed
                    if "messages" not in st.session_state:
                        st.session_state.messages = []
                    
                    # Add user message about upload
                    st.session_state.messages.append({
                        "role": "user",
                        "content": f"I uploaded a PDF file: {uploaded_file.name}"
                    })
                    
                    # Add assistant confirmation message
                    upload_msg = f"✅ PDF uploaded successfully! I've extracted topics from your syllabus. Document ID: {result['document_id'][:8]}... Topics extracted: {result['topic_extract_status']}. You can now ask me to search for jobs or analyze gaps."
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": upload_msg
                    })
                    
                    st.success("PDF uploaded! Check the chat below.")
                    st.rerun()
                else:
                    st.error(f"Upload failed: {response.status_code} - {response.text}")
            except requests.exceptions.RequestException as e:
                st.error(f"Error connecting to backend: {str(e)}")
    
    # Chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Helper function to display analysis tables
    def display_analysis_tables(tables):
        """Display Table A and Table B in a user-friendly format."""
        table_a = tables.get("table_a", [])
        table_b = tables.get("table_b", [])
        
        if not table_a and not table_b:
            return
        
        st.markdown("---")
        st.subheader("📊 Gap Analysis Results")
        
        # Table A: Viable Topics
        if table_a:
            st.markdown("### ✅ Table A: Syllabus Topics Still Viable in Industry")
            for i, row in enumerate(table_a, 1):
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**{i}. {row.get('syllabus_topic', 'N/A')}**")
                        if row.get('example_industry_phrasing'):
                            st.caption(f"Industry phrasing: {row.get('example_industry_phrasing')}")
                        if row.get('notes'):
                            st.caption(f"Note: {row.get('notes')}")
                    with col2:
                        score = row.get('industry_relevance_score', 0)
                        st.metric("Relevance", f"{score}%")
                        st.caption(f"{row.get('evidence_job_count', 0)} jobs")
                    
                    # References
                    references = row.get('references', [])
                    if references:
                        ref_text = " | ".join([f"[Source {idx+1}]({ref})" for idx, ref in enumerate(references[:3])])
                        st.caption(f"References: {ref_text}")
                    
                    if i < len(table_a):
                        st.markdown("---")
        
        # Table B: Missing Topics
        if table_b:
            st.markdown("### ⚠️ Table B: Missing Topics to Add to Syllabus")
            for i, row in enumerate(table_b, 1):
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**{i}. {row.get('missing_topic', 'N/A')}**")
                        if row.get('rationale'):
                            st.caption(f"Rationale: {row.get('rationale')}")
                        if row.get('suggested_syllabus_insertion'):
                            st.caption(f"Suggested placement: {row.get('suggested_syllabus_insertion')}")
                    with col2:
                        priority = row.get('priority', 'N/A')
                        priority_color = {'High': '🔴', 'Medium': '🟡', 'Low': '🟢'}.get(priority, '⚪')
                        st.markdown(f"**Priority:** {priority_color} {priority}")
                        st.caption(f"{row.get('frequency_in_jobs', 0)} jobs")
                    
                    # References
                    references = row.get('references', [])
                    if references:
                        ref_text = " | ".join([f"[Source {idx+1}]({ref})" for idx, ref in enumerate(references[:3])])
                        st.caption(f"References: {ref_text}")
                    
                    if i < len(table_b):
                        st.markdown("---")
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Display tables if any (no tool calls shown)
            if "tables" in message and message["tables"]:
                display_analysis_tables(message["tables"])
    
    # Chat input
    if prompt := st.chat_input("Ask me to search for jobs or analyze gaps..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    payload = {
                        "message": prompt,
                        "conversation_id": st.session_state.conversation_id,
                        "document_id": st.session_state.document_id
                    }
                    
                    response = requests.post(f"{backend_url}/chat", json=payload, timeout=300)
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        # Update conversation ID
                        if result.get("conversation_id"):
                            st.session_state.conversation_id = result["conversation_id"]
                        
                        # Update document ID if provided
                        if result.get("document_id"):
                            st.session_state.document_id = result["document_id"]
                        
                        # Display response
                        st.markdown(result.get("response", ""))
                        
                        # Store message with metadata (tool_calls stored but not displayed)
                        message_data = {
                            "role": "assistant",
                            "content": result.get("response", "")
                        }
                        
                        # Store tool_calls for backend tracking but don't display to user
                        if result.get("tool_calls"):
                            message_data["tool_calls"] = result["tool_calls"]
                        
                        # Display tables nicely if present
                        if result.get("tables"):
                            message_data["tables"] = result["tables"]
                            display_analysis_tables(result["tables"])
                        
                        st.session_state.messages.append(message_data)
                        st.rerun()  # Refresh UI to enable chat input again
                    else:
                        error_msg = f"Error: {response.status_code} - {response.text}"
                        st.error(error_msg)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": error_msg
                        })
                        st.rerun()  # Refresh UI even on error
                except requests.exceptions.RequestException as e:
                    error_msg = f"Connection error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })
                    st.rerun()  # Refresh UI even on error

