import streamlit as st
import pandas as pd
from typing import Dict, List, Any
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def view_results():
    """
    View and manage extraction results - COMPLETELY REDESIGNED TO AVOID NESTED EXPANDERS
    """
    st.title("View Results")
    
    # Validate session state
    if not hasattr(st.session_state, "authenticated") or not hasattr(st.session_state, "client") or not st.session_state.authenticated or not st.session_state.client:
        st.error("Please authenticate with Box first")
        return
    
    # Ensure extraction_results is initialized
    if not hasattr(st.session_state, "extraction_results"):
        st.session_state.extraction_results = {}
        logger.info("Initialized extraction_results in view_results")
    
    # Ensure selected_result_ids is initialized
    if not hasattr(st.session_state, "selected_result_ids"):
        st.session_state.selected_result_ids = []
        logger.info("Initialized selected_result_ids in view_results")
    
    # Ensure metadata_config is initialized
    if not hasattr(st.session_state, "metadata_config"):
        st.session_state.metadata_config = {
            "extraction_method": "freeform",
            "freeform_prompt": "Extract key metadata from this document.",
            "use_template": False,
            "template_id": "",
            "custom_fields": [],
            "ai_model": "azure__openai__gpt_4o_mini",
            "batch_size": 5
        }
        logger.info("Initialized metadata_config in view_results")
    
    if not hasattr(st.session_state, "extraction_results") or not st.session_state.extraction_results:
        st.warning("No extraction results available. Please process files first.")
        if st.button("Go to Process Files", key="go_to_process_files_btn"):
            st.session_state.current_page = "Process Files"
            st.rerun()
        return
    
    st.write("Review and manage the metadata extraction results.")
    
    # Initialize session state for results viewer
    if not hasattr(st.session_state, "results_filter"):
        st.session_state.results_filter = ""
    
    # Filter options
    st.subheader("Filter Results")
    st.session_state.results_filter = st.text_input(
        "Filter by file name",
        value=st.session_state.results_filter,
        key="filter_input"
    )
    
    # Get filtered results
    filtered_results = {}
    
    # Process extraction_results to prepare for display
    for file_id, result in st.session_state.extraction_results.items():
        # Create a standardized result structure
        processed_result = {
            "file_id": file_id,
            "file_name": "Unknown"
        }
        
        # Try to find file name
        for file in st.session_state.selected_files:
            if file["id"] == file_id:
                processed_result["file_name"] = file["name"]
                break
        
        # Process the result data based on its structure
        if isinstance(result, dict):
            # Store the original result
            processed_result["original_data"] = result
            
            # Check if this is a direct API response with an answer field
            if "answer" in result:
                answer = result["answer"]
                
                # Check if answer is a JSON string that needs parsing
                if isinstance(answer, str):
                    try:
                        parsed_answer = json.loads(answer)
                        if isinstance(parsed_answer, dict):
                            processed_result["result_data"] = parsed_answer
                        else:
                            processed_result["result_data"] = {"extracted_text": answer}
                    except json.JSONDecodeError:
                        # Not valid JSON, treat as text
                        processed_result["result_data"] = {"extracted_text": answer}
                elif isinstance(answer, dict):
                    # Already a dictionary
                    processed_result["result_data"] = answer
                else:
                    # Some other format, store as is
                    processed_result["result_data"] = {"extracted_text": str(answer)}
            
            # Check for items array with answer field (common in Box AI responses)
            elif "items" in result and isinstance(result["items"], list) and len(result["items"]) > 0:
                item = result["items"][0]
                if isinstance(item, dict) and "answer" in item:
                    answer = item["answer"]
                    
                    # Check if answer is a JSON string that needs parsing
                    if isinstance(answer, str):
                        try:
                            parsed_answer = json.loads(answer)
                            if isinstance(parsed_answer, dict):
                                processed_result["result_data"] = parsed_answer
                            else:
                                processed_result["result_data"] = {"extracted_text": answer}
                        except json.JSONDecodeError:
                            # Not valid JSON, treat as text
                            processed_result["result_data"] = {"extracted_text": answer}
                    elif isinstance(answer, dict):
                        # Already a dictionary
                        processed_result["result_data"] = answer
                    else:
                        # Some other format, store as is
                        processed_result["result_data"] = {"extracted_text": str(answer)}
            
            # If no structured data found, check for other fields that might contain data
            if "result_data" not in processed_result:
                # Look for any fields that might contain extracted data
                for key in ["extracted_data", "data", "result", "metadata"]:
                    if key in result and result[key]:
                        if isinstance(result[key], dict):
                            processed_result["result_data"] = result[key]
                            break
                        elif isinstance(result[key], str):
                            try:
                                parsed_data = json.loads(result[key])
                                if isinstance(parsed_data, dict):
                                    processed_result["result_data"] = parsed_data
                                    break
                            except json.JSONDecodeError:
                                processed_result["result_data"] = {"extracted_text": result[key]}
                                break
                
                # If still no result_data, use the entire result as is
                if "result_data" not in processed_result:
                    processed_result["result_data"] = result
        else:
            # Not a dictionary, store as text
            processed_result["result_data"] = {"extracted_text": str(result)}
        
        # Add to filtered results
        filtered_results[file_id] = processed_result
    
    # Apply filter if specified
    if st.session_state.results_filter:
        filtered_results = {
            file_id: result for file_id, result in filtered_results.items()
            if st.session_state.results_filter.lower() in result.get("file_name", "").lower()
        }
    
    # Display results count
    st.write(f"Showing {len(filtered_results)} of {len(st.session_state.extraction_results)} results")
    
    # Display results
    st.subheader("Extraction Results")
    
    # Determine if we're using structured or freeform extraction
    is_structured = st.session_state.metadata_config.get("extraction_method") == "structured"
    
    # Create tabs for different views
    tab1, tab2 = st.tabs(["Table View", "Detailed View"])
    
    with tab1:
        # Table view implementation
        # (Code continues as in original file)
        pass

    with tab2:
        # Detailed view implementation
        # (Code continues as in original file)
        pass

# Add an alias for backward compatibility
results_viewer = view_results
