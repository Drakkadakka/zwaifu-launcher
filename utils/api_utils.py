"""
API Utilities Module
Provides common API key management and authentication functions
"""

import os
import json
import requests
from typing import Optional, Dict, Any


def load_api_key(project_root: Optional[str] = None) -> Optional[str]:
    """
    Load API key from api_key.json file
    
    Args:
        project_root: Optional path to project root. If None, will try to find it automatically.
    
    Returns:
        API key string if found, None otherwise
    """
    try:
        if project_root is None:
            # Try to find the project root by looking for api_key.json
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
        
        api_key_path = os.path.join(project_root, 'api_key.json')
        
        if os.path.exists(api_key_path):
            with open(api_key_path, 'r') as f:
                api_key_data = json.load(f)
                api_key = api_key_data.get('api_key')
                if api_key:
                    print(f"Loaded API key from {api_key_path}")
                    return api_key
        
        print(f"API key file not found at {api_key_path}")
        return None
        
    except Exception as e:
        print(f"Failed to load API key: {e}")
        return None


def make_authenticated_api_call(
    endpoint: str, 
    method: str = 'GET', 
    data: Optional[Dict[str, Any]] = None,
    base_url: str = 'http://localhost:8081',
    api_key: Optional[str] = None,
    project_root: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Make an authenticated API call using the loaded API key
    
    Args:
        endpoint: API endpoint (e.g., '/api/status')
        method: HTTP method ('GET' or 'POST')
        data: Data to send with POST request
        base_url: Base URL for API server
        api_key: API key to use. If None, will try to load from file
        project_root: Project root path for loading API key
    
    Returns:
        JSON response if successful, None otherwise
    """
    try:
        # Load API key if not provided
        if api_key is None:
            api_key = load_api_key(project_root)
            if not api_key:
                print("No API key available for API call")
                return None
        
        # Prepare headers
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        # Make the request
        url = f"{base_url.rstrip('/')}{endpoint}"
        
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers, timeout=10)
        elif method.upper() == 'POST':
            response = requests.post(url, headers=headers, json=data, timeout=10)
        else:
            print(f"Unsupported HTTP method: {method}")
            return None
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"API call failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"API call error: {e}")
        return None


def test_api_connection(
    base_url: str = 'http://localhost:8081',
    api_key: Optional[str] = None,
    project_root: Optional[str] = None
) -> bool:
    """
    Test API connection using the loaded API key
    
    Args:
        base_url: Base URL for API server
        api_key: API key to use. If None, will try to load from file
        project_root: Project root path for loading API key
    
    Returns:
        True if connection successful, False otherwise
    """
    result = make_authenticated_api_call(
        '/api/status', 
        'GET', 
        base_url=base_url,
        api_key=api_key,
        project_root=project_root
    )
    
    if result:
        print(f"API connection successful! Status: {result.get('status', 'Unknown')}")
        return True
    else:
        print("API connection failed. Check if API server is running and API key is valid.")
        return False


def get_api_key_info(project_root: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Get information about the API key
    
    Args:
        project_root: Project root path for loading API key
    
    Returns:
        Dictionary with API key info if found, None otherwise
    """
    try:
        if project_root is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
        
        api_key_path = os.path.join(project_root, 'api_key.json')
        
        if os.path.exists(api_key_path):
            with open(api_key_path, 'r') as f:
                api_key_data = json.load(f)
                return {
                    'api_key': api_key_data.get('api_key', '')[:16] + '...' if api_key_data.get('api_key') else None,
                    'created': api_key_data.get('created'),
                    'file_path': api_key_path
                }
        
        return None
        
    except Exception as e:
        print(f"Failed to get API key info: {e}")
        return None


# Example usage functions
def example_usage():
    """Example of how to use the API utilities"""
    print("API Utilities Example Usage")
    print("=" * 40)
    
    # Load API key
    api_key = load_api_key()
    if api_key:
        print(f"API key loaded: {api_key[:16]}...")
        
        # Test connection
        if test_api_connection(api_key=api_key):
            # Make API calls
            status = make_authenticated_api_call('/api/status', api_key=api_key)
            if status:
                print(f"Server status: {status}")
            
            processes = make_authenticated_api_call('/api/processes', api_key=api_key)
            if processes:
                print(f"Processes: {processes}")
    else:
        print("No API key found. Generate one first using the launcher.")


if __name__ == "__main__":
    example_usage() 