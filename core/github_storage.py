import json
import requests
import base64
import streamlit as st
import os

def update_json_file(file_path, data):
    """
    Update a JSON file in the GitHub repository
    
    Args:
        file_path: Path to the JSON file (e.g., 'data/teams.json')
        data: The data to write to the file
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # GitHub API settings
        if "github" not in st.secrets:
            st.error("GitHub secrets not configured. Please add GitHub credentials to .streamlit/secrets.toml")
            return False
            
        token = st.secrets["github"]["token"]
        repo = st.secrets["github"]["repo"]
        branch = st.secrets["github"]["branch"]
        
        # API endpoint for getting and updating file
        api_url = f"https://api.github.com/repos/{repo}/contents/{file_path}"
        
        # Headers for authentication
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Get the current file to obtain its SHA
        response = requests.get(api_url, headers=headers)
        
        # Handle file not found (create new file)
        if response.status_code == 404:
            st.info(f"File {file_path} not found on GitHub. Creating new file.")
            
            # Prepare the content
            content = json.dumps(data, indent=2)
            encoded_content = base64.b64encode(content.encode()).decode()
            
            # Create the file payload
            create_data = {
                "message": f"Create {file_path} via Streamlit app",
                "content": encoded_content,
                "branch": branch
            }
            
            # Create the file
            create_response = requests.put(api_url, headers=headers, json=create_data)
            
            if create_response.status_code in [200, 201]:
                st.success(f"Successfully created {file_path} on GitHub")
                return True
            else:
                error_msg = f"Error creating file: {create_response.status_code}"
                if hasattr(create_response, 'json'):
                    error_msg += f" - {create_response.json().get('message', '')}"
                st.error(error_msg)
                return False
                
        elif response.status_code != 200:
            error_msg = f"Error getting file: {response.status_code}"
            if hasattr(response, 'json'):
                error_msg += f" - {response.json().get('message', '')}"
            st.error(error_msg)
            return False
        
        file_info = response.json()
        sha = file_info["sha"]
        
        # Prepare the update
        content = json.dumps(data, indent=2)
        encoded_content = base64.b64encode(content.encode()).decode()
        
        # Create the update payload
        update_data = {
            "message": f"Update {file_path} via Streamlit app",
            "content": encoded_content,
            "sha": sha,
            "branch": branch
        }
        
        # Update the file
        update_response = requests.put(api_url, headers=headers, json=update_data)
        
        if update_response.status_code in [200, 201]:
            st.success(f"Successfully updated {file_path} on GitHub")
            return True
        else:
            error_msg = f"Error updating file: {update_response.status_code}"
            if hasattr(update_response, 'json'):
                error_msg += f" - {update_response.json().get('message', '')}"
            st.error(error_msg)
            return False
            
    except Exception as e:
        st.error(f"Error updating GitHub file: {str(e)}")
        return False

def test_github_connection():
    """Test the GitHub connection and return status"""
    try:
        if "github" not in st.secrets:
            return False, "GitHub secrets not configured"
            
        token = st.secrets["github"]["token"]
        repo = st.secrets["github"]["repo"]
        
        # API endpoint for getting repo info
        api_url = f"https://api.github.com/repos/{repo}"
        
        # Headers for authentication
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Test the connection
        response = requests.get(api_url, headers=headers)
        
        if response.status_code == 200:
            repo_info = response.json()
            return True, f"Connected to GitHub repository: {repo_info['full_name']}"
        else:
            error_msg = f"GitHub API returned status code: {response.status_code}"
            if hasattr(response, 'json'):
                error_msg += f" - {response.json().get('message', '')}"
            return False, error_msg
            
    except Exception as e:
        return False, f"Error connecting to GitHub: {str(e)}"