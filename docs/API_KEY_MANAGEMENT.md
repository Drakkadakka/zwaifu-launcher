# API Key Management System

This document describes the comprehensive API key management system implemented in the Z-Waifu Launcher.

## Overview

The API key management system provides secure authentication for all API calls to the Z-Waifu Launcher. API keys are automatically generated, stored, and loaded by all components that need to make authenticated API calls.

### Persistent API Keys

The system now supports **persistent API keys** that remain valid across launcher restarts:

- **30-Day Expiration**: Keys are valid for 30 days instead of 24 hours
- **Automatic Loading**: Keys are automatically loaded when the API server starts
- **Expiration Extension**: When loaded, keys are extended to expire 30 days from the current time
- **No Manual Refresh**: You no longer need to regenerate keys after each restart

## Features

- ✅ **Automatic API Key Generation** - Generate keys through the GUI
- ✅ **Persistent Storage** - Keys stored in `api_key.json` file and persist between restarts
- ✅ **Automatic Loading** - All components automatically load keys on startup
- ✅ **Extended Expiration** - Keys valid for 30 days instead of 24 hours
- ✅ **Key Refresh/Regeneration** - Refresh keys when needed
- ✅ **Utility Functions** - Easy-to-use functions for API calls
- ✅ **GUI Integration** - Buttons for key management in the launcher
- ✅ **Test Scripts** - Comprehensive testing of the authentication system

## File Structure

```
ZWAIFU-PROJECT/
├── api_key.json                    # Stored API key (auto-generated)
├── utils/
│   └── api_utils.py               # API utility functions
├── test_api_authentication.py     # Authentication test script
├── example_api_usage.py           # Usage example script
└── zwaifu_launcher_gui.py         # Main launcher with key management
```

## API Key File Format

The `api_key.json` file contains:

```json
{
  "api_key": "your_64_character_hex_key_here",
  "created": 1234567890.123
}
```

## GUI Features

### Advanced Features Tab

The launcher includes several API key management buttons:

1. **Generate API Key** - Creates a new API key
2. **Refresh API Key** - Regenerates the API key
3. **Test API** - Tests the API connection using the current key

### Usage

1. Start the Z-Waifu Launcher
2. Go to the "Advanced Features" tab
3. Click "Start API Server"
4. Click "Generate API Key" to create your first key
5. Use "Refresh API Key" to regenerate when needed
6. Use "Test API" to verify the connection

## Utility Functions

### `utils/api_utils.py`

This module provides easy-to-use functions for API key management:

#### `load_api_key(project_root=None)`
Loads the API key from `api_key.json`

```python
from utils.api_utils import load_api_key

api_key = load_api_key()
if api_key:
    print(f"API key loaded: {api_key[:16]}...")
```

#### `make_authenticated_api_call(endpoint, method='GET', data=None, base_url='http://localhost:8081', api_key=None)`
Makes an authenticated API call

```python
from utils.api_utils import make_authenticated_api_call

# Get server status
status = make_authenticated_api_call('/api/status')

# Start a process
result = make_authenticated_api_call(
    '/api/start/Oobabooga', 
    method='POST'
)
```

#### `test_api_connection(base_url='http://localhost:8081', api_key=None)`
Tests if the API server is accessible

```python
from utils.api_utils import test_api_connection

if test_api_connection():
    print("API connection successful!")
else:
    print("API connection failed!")
```

#### `get_api_key_info(project_root=None)`
Gets information about the stored API key

```python
from utils.api_utils import get_api_key_info

info = get_api_key_info()
if info:
    print(f"Key created: {info['created']}")
    print(f"Key file: {info['file_path']}")
```

## Integration in Components

### LauncherGUI Class

The main launcher class includes:

- `load_api_key()` - Loads API key from file
- `refresh_api_key()` - Regenerates API key
- `make_api_call()` - Makes authenticated API calls
- `test_api_connection()` - Tests API connection

### WebInterface Class

The web interface automatically loads API keys for external API calls:

- `load_api_key()` - Loads API key
- `make_authenticated_api_call()` - Makes authenticated calls

### MobileApp Class

The mobile app includes API key management:

- `load_api_key()` - Loads API key
- `make_authenticated_api_call()` - Makes authenticated calls

### AnalyticsSystem Class

The analytics system can make authenticated API calls:

- `load_api_key()` - Loads API key
- `make_authenticated_api_call()` - Makes authenticated calls

## Testing

### Test Scripts

Run the comprehensive test script:

```bash
python test_api_authentication.py
```

This script tests:
- Server availability
- Missing authentication
- Invalid authentication
- Admin key generation
- API key validation
- Process operations
- Rate limiting
- Expired key handling

#### Persistent Key Test

Test the persistent API key functionality:

```bash
python test_persistent_api_key.py
```

This script tests:
- Current API key validity
- Launcher restart simulation
- Key expiration calculation
- Persistent storage verification

### Example Usage

Run the example script to see how to use the API utilities:

```bash
python example_api_usage.py
```

## Security Features

### Key Generation
- 64-character hexadecimal keys
- Cryptographically secure random generation
- Extended expiration (30 days) for persistent use
- Automatic loading and validation on startup

### Storage
- Keys stored in JSON format
- File permissions should be restricted
- Keys are not logged in plain text

### Validation
- Bearer token authentication
- Rate limiting on API endpoints
- Automatic key cleanup
- Persistent key validation across restarts
- Extended expiration time (30 days)

## API Endpoints

All API endpoints require authentication:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/status` | GET | Get server status |
| `/api/processes` | GET | Get process information |
| `/api/start/<process_type>` | POST | Start a process |
| `/api/stop/<process_type>` | POST | Stop a process |
| `/api/keys/generate` | POST | Generate API key (requires admin) |

## Error Handling

The system includes comprehensive error handling:

- Missing API key files
- Invalid API keys
- Network connection issues
- Server unavailability
- Rate limiting exceeded

## Best Practices

1. **Keep API Keys Secure**
   - Don't share API keys
   - Use file permissions to restrict access
   - Regenerate keys periodically

2. **Error Handling**
   - Always check return values from API calls
   - Handle connection errors gracefully
   - Log errors for debugging

3. **Testing**
   - Test API connections before making calls
   - Use the provided test scripts
   - Verify authentication is working

## Troubleshooting

### Common Issues

1. **"No API key found"**
   - Generate an API key using the launcher
   - Check that `api_key.json` exists

2. **"API connection failed"**
   - Make sure the API server is running
   - Check the port (default: 8081)
   - Verify the API key is valid

3. **"401 Unauthorized"**
   - API key may be expired (check if older than 30 days)
   - Regenerate the API key
   - Check the Authorization header format
   - Verify the key was loaded on startup

### Debugging

Enable debug logging in the launcher to see detailed API call information.

## Future Enhancements

- Database storage for API keys
- Multiple API key support
- Key permissions and scopes
- Webhook support
- OAuth2 integration
- API key rotation policies
- Configurable expiration times
- Key usage analytics

## Support

For issues with the API key management system:

1. Check the launcher logs
2. Run the test script
3. Verify the API server is running
4. Check file permissions on `api_key.json` 