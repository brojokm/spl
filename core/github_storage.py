import json
import requests
import base64
import streamlit as st
import os
import time

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
        
        # Add a small delay to avoid rate limiting and race conditions
        time.sleep(1)
        
        # API endpoint for getting and updating file
        api_url = f"https://api.github.com/repos/{repo}/contents/{file_path}"
        
        # Headers for authentication
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Get the current file to obtain its SHA - always get the latest version
        response = requests.get(api_url, headers=headers, params={"ref": branch})
        
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
        
        # Check if the content is different before updating
        current_content = base64.b64decode(file_info["content"]).decode('utf-8')
        new_content = json.dumps(data, indent=2)
        
        # If content is the same, no need to update
        if current_content.strip() == new_content.strip():
            st.info(f"No changes detected in {file_path}, skipping update")
            return True
        
        # Prepare the update
        encoded_content = base64.b64encode(new_content.encode()).decode()
        
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
        elif update_response.status_code == 409:
            # Handle conflict by getting the latest version and trying again
            st.warning(f"Conflict detected for {file_path}, getting latest version and retrying...")
            
            # Get the latest file version
            latest_response = requests.get(api_url, headers=headers, params={"ref": branch})
            if latest_response.status_code != 200:
                st.error(f"Error getting latest version: {latest_response.status_code}")
                return False
                
            latest_file_info = latest_response.json()
            latest_sha = latest_file_info["sha"]
            
            # Update with the latest SHA
            update_data["sha"] = latest_sha
            retry_response = requests.put(api_url, headers=headers, json=update_data)
            
            if retry_response.status_code in [200, 201]:
                st.success(f"Successfully updated {file_path} on GitHub after resolving conflict")
                return True
            else:
                error_msg = f"Error updating file after conflict resolution: {retry_response.status_code}"
                if hasattr(retry_response, 'json'):
                    error_msg += f" - {retry_response.json().get('message', '')}"
                st.error(error_msg)
                return False
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

def batch_update_github_files(files_data):
    """
    Update multiple JSON files on GitHub in a single operation
    
    Args:
        files_data: Dictionary mapping file paths to their data
                   e.g., {"data/teams.json": teams_data}
    
    Returns:
        tuple: (success, message)
    """
    try:
        # GitHub API settings
        if "github" not in st.secrets:
            return False, "GitHub secrets not configured"
            
        token = st.secrets["github"]["token"]
        repo = st.secrets["github"]["repo"]
        branch = st.secrets["github"]["branch"]
        
        # Headers for authentication
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        results = {}
        all_success = True
        
        # First, get all current files to check their SHA
        file_info = {}
        for file_path in files_data.keys():
            api_url = f"https://api.github.com/repos/{repo}/contents/{file_path}"
            response = requests.get(api_url, headers=headers, params={"ref": branch})
            
            if response.status_code == 200:
                file_info[file_path] = response.json()
            elif response.status_code == 404:
                # File doesn't exist yet
                file_info[file_path] = None
            else:
                all_success = False
                results[file_path] = f"Error getting file info: {response.status_code}"
        
        # Now update each file with the correct SHA
        for file_path, data in files_data.items():
            try:
                api_url = f"https://api.github.com/repos/{repo}/contents/{file_path}"
                
                # Prepare content
                content = json.dumps(data, indent=2)
                encoded_content = base64.b64encode(content.encode()).decode()
                
                # Create update payload
                update_data = {
                    "message": f"Update {file_path} via batch operation",
                    "content": encoded_content,
                    "branch": branch
                }
                
                # Add SHA if file exists
                if file_info[file_path]:
                    current_sha = file_info[file_path]["sha"]
                    update_data["sha"] = current_sha
                    
                    # Check if content is different
                    current_content = base64.b64decode(file_info[file_path]["content"]).decode('utf-8')
                    if current_content.strip() == content.strip():
                        results[file_path] = "No changes needed"
                        continue
                
                # Update the file
                update_response = requests.put(api_url, headers=headers, json=update_data)
                
                if update_response.status_code in [200, 201]:
                    results[file_path] = "Success"
                elif update_response.status_code == 409:
                    # Handle conflict by getting the latest SHA
                    retry_response = requests.get(api_url, headers=headers, params={"ref": branch})
                    if retry_response.status_code == 200:
                        latest_sha = retry_response.json()["sha"]
                        update_data["sha"] = latest_sha
                        
                        # Try again with the latest SHA
                        retry_update = requests.put(api_url, headers=headers, json=update_data)
                        if retry_update.status_code in [200, 201]:
                            results[file_path] = "Success after conflict resolution"
                        else:
                            all_success = False
                            results[file_path] = f"Failed after conflict: {retry_update.status_code}"
                    else:
                        all_success = False
                        results[file_path] = f"Failed to resolve conflict: {retry_response.status_code}"
                else:
                    all_success = False
                    results[file_path] = f"Failed: {update_response.status_code}"
                    
                # Add a small delay between updates to avoid rate limiting
                time.sleep(1)
                    
            except Exception as e:
                all_success = False
                results[file_path] = f"Error: {str(e)}"
        
        # Prepare result message
        message_parts = [f"{file}: {status}" for file, status in results.items()]
        message = "\n".join(message_parts)
        
        return all_success, message
        
    except Exception as e:
        return False, f"Error in batch update: {str(e)}"