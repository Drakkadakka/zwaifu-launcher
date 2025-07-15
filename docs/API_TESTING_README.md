# Z-Waifu Launcher API Authentication Testing

This guide provides comprehensive testing for the API key authentication system in the Z-Waifu Launcher.

## Overview

The Z-Waifu Launcher includes a secure API server that uses Bearer token authentication with the following features:

- **Admin Key**: Generated automatically when the API server starts
- **API Keys**: Generated using the admin key, valid for 24 hours
- **Rate Limiting**: Prevents abuse with configurable limits
- **Process Type Validation**: Prevents injection attacks
- **Key Expiration**: Automatic cleanup of expired keys

## Prerequisites

1. **Start the Z-Waifu Launcher**
2. **Enable the API Server**:
   - Go to the "Advanced Features" tab
   - Click "Start API Server"
   - Note the admin key from the logs

## Testing Methods

### Method 1: Python Test Script (Recommended)

The most comprehensive testing approach using the Python script.

#### Setup
```bash
# Install required dependencies
pip install requests

# Run the test script
python test_api_authentication.py
```

#### Features Tested
- ✅ Server availability
- ✅ Missing authentication headers
- ✅ Invalid authentication headers
- ✅ Admin key generation
- ✅ API key validation
- ✅ Process operations
- ✅ Invalid process types
- ✅ Rate limiting
- ✅ Expired key handling

### Method 2: Admin Key Extraction

Extract the admin key from launcher logs for manual testing.

```bash
python get_admin_key.py
```

This script will:
- Check if the API server is running
- Extract the admin key from logs
- Save it to `admin_key.json` for convenience

### Method 3: Curl Commands

For command-line testing using curl.

```bash
# Make the script executable (Linux/Mac)
chmod +x test_api_curl.sh

# Run the curl tests
./test_api_curl.sh
```

## Manual Testing with Curl

### 1. Test Server Availability
```bash
curl -i http://localhost:8081/api/status
```
**Expected**: 401 Unauthorized (not 404 Not Found)

### 2. Test Missing Authentication
```bash
curl -i -X POST http://localhost:8081/api/start/Oobabooga
```
**Expected**: 401 Unauthorized

### 3. Test Invalid Authentication
```bash
curl -i -H "Authorization: Bearer invalid_key" http://localhost:8081/api/status
```
**Expected**: 401 Unauthorized

### 4. Generate API Key (requires admin key)
```bash
curl -i -X POST \
  -H "Authorization: Bearer YOUR_ADMIN_KEY" \
  -H "Content-Type: application/json" \
  http://localhost:8081/api/keys/generate
```
**Expected**: 200 OK with JSON response containing `api_key` and `expires_in`

### 5. Test Valid API Key
```bash
curl -i -H "Authorization: Bearer YOUR_API_KEY" http://localhost:8081/api/status
```
**Expected**: 200 OK with JSON response

### 6. Test Process Operations
```bash
# Start a process
curl -i -X POST \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  http://localhost:8081/api/start/Oobabooga

# Stop a process
curl -i -X POST \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  http://localhost:8081/api/stop/Z-Waifu
```

### 7. Test Invalid Process Types
```bash
curl -i -X POST \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  http://localhost:8081/api/start/InvalidProcess
```
**Expected**: 400 Bad Request

## API Endpoints

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/status` | GET | Get server status | ✅ |
| `/api/processes` | GET | Get process status | ✅ |
| `/api/start/<process_type>` | POST | Start a process | ✅ |
| `/api/stop/<process_type>` | POST | Stop a process | ✅ |
| `/api/keys/generate` | POST | Generate API key | Admin Key |

## Valid Process Types

- `Oobabooga`
- `Z-Waifu`
- `Ollama`
- `RVC`

## Rate Limits

- **Status/Processes**: 10 requests per minute
- **Start/Stop**: 5 requests per minute
- **Key Generation**: No limit (admin key required)

## Security Features

### 1. Bearer Token Authentication
All API endpoints require a valid Bearer token in the Authorization header.

### 2. Key Expiration
API keys automatically expire after 24 hours and are cleaned up.

### 3. Process Type Validation
Only predefined process types are allowed to prevent injection attacks.

### 4. Rate Limiting
Prevents abuse with configurable request limits per endpoint.

### 5. Admin Key Protection
Only the admin key can generate new API keys.

## Troubleshooting

### API Server Not Starting
1. Check if Flask is installed: `pip install flask flask-limiter`
2. Check if port 8081 is available
3. Check launcher logs for errors

### Authentication Failures
1. Verify the admin key is correct
2. Check if the API key has expired
3. Ensure proper Bearer token format

### Rate Limiting Issues
1. Wait for the rate limit window to reset
2. Reduce request frequency
3. Check rate limit configuration

### Process Operations Failing
1. Verify batch files are configured
2. Check if processes are already running
3. Review launcher logs for process errors

## Test Results

The Python test script generates detailed results in JSON format:
```
api_auth_test_results_YYYYMMDD_HHMMSS.json
```

This file contains:
- Test name and status
- Timestamp
- Detailed error messages
- Response data

## Security Best Practices

1. **Keep Admin Key Secure**: The admin key should be kept confidential
2. **Rotate API Keys**: Generate new API keys regularly
3. **Monitor Usage**: Check logs for unusual activity
4. **Network Security**: Consider firewall rules for the API port
5. **HTTPS in Production**: Use HTTPS for production deployments

## Example Integration

### Python Client Example
```python
import requests

class ZWaifuAPIClient:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {api_key}"}
    
    def get_status(self):
        response = requests.get(f"{self.base_url}/api/status", headers=self.headers)
        return response.json()
    
    def start_process(self, process_type):
        response = requests.post(
            f"{self.base_url}/api/start/{process_type}",
            headers=self.headers
        )
        return response.json()
```

### JavaScript Client Example
```javascript
class ZWaifuAPIClient {
    constructor(baseUrl, apiKey) {
        this.baseUrl = baseUrl;
        this.headers = {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json'
        };
    }
    
    async getStatus() {
        const response = await fetch(`${this.baseUrl}/api/status`, {
            headers: this.headers
        });
        return response.json();
    }
    
    async startProcess(processType) {
        const response = await fetch(`${this.baseUrl}/api/start/${processType}`, {
            method: 'POST',
            headers: this.headers
        });
        return response.json();
    }
}
```

## Support

If you encounter issues with the API authentication system:

1. Check the launcher logs in `data/launcher_log.txt`
2. Verify all dependencies are installed
3. Ensure the API server is running on port 8081
4. Test with the provided test scripts
5. Review the security configuration

For additional help, refer to the main launcher documentation or create an issue in the project repository. 