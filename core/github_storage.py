import json
import requests
import base64
import streamlit as st

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
        if response.status_code != 200:
            print(f"Error getting file: {response.status_code}")
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
            print(f"Successfully updated {file_path}")
            return True
        else:
            print(f"Error updating file: {update_response.status_code}")
            print(update_response.json())
            return False
            
    except Exception as e:
        print(f"Error updating GitHub file: {str(e)}")
        return False