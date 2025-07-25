# Deutsche Bahn MCP Server

A comprehensive Model Context Protocol (MCP) server that provides unified access to Deutsche Bahn (DB) and German mobility APIs. Built with Python, FastAPI, and FastMCP for seamless integration with Claude Desktop and other MCP clients.

The server is ready for local and cloud deployment. A running MCP server is available to connect by adding the URL to your MCP Client: `https://db-mcp.datamonkey.tech/mcp`.

## 🚀 Features

- **🚄 Complete Railway Data**: Stations, timetables, real-time disruptions, and parking
- **🤖 MCP Protocol**: Full support for tools, prompts, and resources
- **🛡️ Production Ready**: Security headers, rate limiting, input validation
- **🏗️ Modular Architecture**: Clean, maintainable codebase structure
- **☁️ Cloud Native**: Designed for Google Cloud Run deployment
- **📚 Rich Documentation**: Comprehensive guides and reference materials

## 📋 Quick Start (for developers - User instructions below)

### Prerequisites

- Python 3.11+
- Deutsche Bahn API credentials ([Get them here](https://developers.deutschebahn.com))
- Google Cloud account (for deployment)

### Local Development

1. **Clone and setup:**
   ```bash
   git clone <repository-url>
   cd deutsche-bahn-mcp-server
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your DB API credentials
   ```

3. **Run the server:**
   ```bash
   python main.py
   # Server available at http://localhost:8080
   ```

## 🎯 Live Server Usage Guide

The Deutsche Bahn MCP Server is live at `https://db-mcp.datamonkey.tech` and ready to use immediately. Follow these step-by-step guides to start accessing German railway data in Claude.

### 🖥️ Claude Desktop Setup

**Step 1: Locate your configuration file**
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\\Claude\\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

**Step 2: Edit the configuration**
Open the file and add the Deutsche Bahn server:

```json
{
  "mcpServers": {
    "deutschebahn": {
      "command": "npx",
      "args": [
        "-y", "mcp-remote",
        "https://db-mcp.datamonkey.tech/mcp",
        "--transport", "http-only"
      ]
    }
  }
}
```

**Step 3: Restart Claude Desktop**
- Close Claude Desktop completely
- Reopen the application
- You should see "Deutsche Bahn MCP Server" in the MCP section

**Step 4: Test the connection**
Ask Claude: *"What train stations are in Berlin?"*

### 🌐 Claude.ai Web Usage

**Step 1: Start a conversation**
Go to [claude.ai](https://claude.ai) and begin a new conversation.

**Step 2: Add the MCP Server**
Click on *"Search and Tools > Add connectors > Manage connectors"*
Select *"Add custom connector"*
Enter a name, e.g.: *"Deutsche Bahn MCP Server"* 
Enter this remote MCP Server URL: `https://db-mcp.datamonkey.tech/mcp`

**Step 3: Test immediately**
Try asking: *"Find train stations near Frankfurt and check for any current delays at Frankfurt Hauptbahnhof."*

### 📱 Quick Examples to Try

Once connected, try these practical examples:

**🔍 Station Search**
- *"Find all train stations in Munich"*
- *"What stations are within 5km of coordinates 52.5200, 13.4050?"*

**🚄 Real-time Information**
- *"Are there any delays at Berlin Hauptbahnhof right now?"*
- *"Show me the departure schedule for Hamburg Hbf at 3 PM today"*

**♿ Accessibility Planning**
- *"Is barrier-free travel possible from München to Hamburg?"*
- *"What accessibility services are available at Köln Hauptbahnhof?"*

**🅿️ Parking Information**
- *"What parking is available at Frankfurt Hauptbahnhof tomorrow at 10 AM?"*
- *"Find parking facilities near Düsseldorf main station"*

**🗺️ Travel Planning**
- *"Help me plan accessible travel from Berlin to Dresden"*
- *"What are the major railway hubs in Bavaria?"*

### 🔧 Connection Troubleshooting

**Claude Desktop Issues:**

*Problem: Server not showing in MCP section*
- Verify JSON syntax in config file (use a JSON validator)
- Ensure Claude Desktop was fully restarted
- Check the file is saved in the correct location

*Problem: Connection timeouts*
- Verify internet connection
- Try: `curl https://db-mcp.datamonkey.tech/mcp/ping` in terminal
- If curl fails, there may be network restrictions

*Problem: "Command not found" errors*
- Ensure Node.js and npm are installed
- Try running: `npm install -g mcp-remote`

**Claude.ai Web Issues:**

*Problem: "Cannot connect to MCP server"*
- The web version may need explicit MCP server support
- Try asking Claude to help you connect step by step
- Alternative: Use specific tool calls like asking for station information

**General Issues:**

*Server Status Check:*
```bash
# Test if server is responding
curl https://db-mcp.datamonkey.tech/health

# Test MCP endpoint
curl https://db-mcp.datamonkey.tech/mcp/ping
```

*Rate Limiting:*
- Server allows 60 requests/minute, 1000/hour
- If exceeded, wait and try again
- Consider using specific queries rather than broad searches

## 🛠️ Available Features

### 🔧 Tools (13 available)

#### **Station Data**
- `get_station_by_name(name, limit=10)` - Search stations by name with fallback filtering
- `get_stations_by_position(lat, lon, radius=2.0)` - Find nearby stations using smart regional filtering

#### **Timetables & Disruptions**
- `get_planned_timetable(eva_number, date, hour)` - Scheduled departures/arrivals
- `get_recent_timetable_changes(eva_number)` - Real-time updates (last 2 minutes)
- `get_full_timetable_changes(eva_number)` - All known future disruptions

#### **Parking Information**
- `get_parking_by_station(stop_place_id)` - Parking facilities near stations
- `search_parking_facilities(station_name)` - Search parking by station name using real API
- `get_parking_prognoses(facility_id, datetime)` - Availability forecasts

#### **Accessibility Services**
- `find_facilities(station_number, type, state)` - Elevators, escalators status
- `get_facilities_by_station(station_number)` - Complete facility overview  
- `get_szentralen_by_location(lat, lon)` - Mobility service centers using regional filtering
- `search_szentralen(limit, offset)` - Service center search with pagination

### 💬 Interactive Prompts (7 available)

- `accessibility_check` - Barrier-free travel verification between stations
- `parking_prognosis` - Parking availability forecast at stations
- `recent_timetable_changes` - Real-time delays & service disruptions
- `planned_timetable_window` - Train schedule for specific time periods
- `station_services` - Complete station information & amenities
- `nearby_stations` - Find railway stations near geographic coordinates
- `current_disruptions` - Comprehensive service disruption overview

### 📚 Reference Resources (5 available)

- `file://reference/station-categories` - German railway station classification guide
- `file://reference/train-types` - Complete guide to German train types (ICE, IC, RE, etc.)
- `file://stations/major-hubs` - List of Germany's most important railway stations
- `file://services/accessibility-guide` - Comprehensive accessibility features guide
- `file://status/current-disruptions` - System-wide disruption overview

## 🏗️ Architecture

```
├── main.py                    # FastAPI application entry point
├── server_instance.py         # Shared MCP server instance
├── mcp_server.py             # Server setup and module registration
├── utils.py                  # Shared utilities and validation
├── config.py                 # Configuration and secret management
├── models.py                 # Pydantic data models
├── rate_limiter.py           # Security: rate limiting
├── tools/                    # MCP Tools
│   ├── station_tools.py      # Station search and lookup
│   ├── timetable_tools.py    # Timetables and disruptions
│   ├── parking_tools.py      # Parking facilities
│   └── facility_tools.py     # Accessibility services
├── resources/                # MCP Resources
│   └── travel_resources.py   # Travel guides and references
└── prompts/                  # MCP Prompts
    └── travel_prompts.py      # Interactive travel assistance
```

## 🎯 Smart Geographic Filtering

The server implements intelligent regional filtering to maximize API efficiency and result relevance:

### **Coordinate-to-Region Mapping**
- **Federal State Detection**: Maps coordinates to German federal states (Bayern, Hessen, etc.)
- **Border Area Handling**: Includes neighboring states for locations near borders
- **City-based Filtering**: Uses major cities within relevant states for targeted searches

### **Enhanced Station Search**
- **Regional Pre-filtering**: `get_stations_by_position()` fetches stations from relevant federal states instead of random 1000
- **Fallback Mechanisms**: `get_station_by_name()` uses API searchstring with client-side fallback
- **Distance Calculations**: Precise haversine distance calculations using actual coordinates

### **S-Zentralen Regional Filtering** 
- **City Matching**: Filters S-Zentralen by cities within coordinate-determined regions
- **State-to-Cities Mapping**: Comprehensive mapping of federal states to major cities
- **Relevant Results**: Returns regional service centers instead of all German centers

## 🔒 Security Features

- **Rate Limiting**: 60 requests/minute, 1000 requests/hour per client
- **Input Validation**: Comprehensive sanitization and validation
- **Security Headers**: XSS, CSRF, content-type protection
- **Error Sanitization**: No sensitive information disclosure
- **HTTPS Only**: Secure transport layer
- **CORS Protection**: Controlled cross-origin access

## 🚀 Deployment

### Google Cloud Run (Recommended)

Deploy your own instance of the Deutsche Bahn MCP Server with these steps:

#### Prerequisites
- Google Cloud CLI installed and configured
- Deutsche Bahn API credentials from [developers.deutschebahn.com](https://developers.deutschebahn.com)

#### Basic Deployment (Default Cloud Run URL)

1. **Setup secrets:**
   ```bash
   # Create secrets for your DB API credentials
   echo "your_db_api_key" | gcloud secrets create DB_API_KEY --data-file=-
   echo "your_db_api_secret" | gcloud secrets create DB_API_SECRET --data-file=-
   ```

2. **Deploy the service:**
   ```bash
   # Clone the repository
   git clone https://github.com/your-repo/deutsche-bahn-mcp-server
   cd deutsche-bahn-mcp-server
   
   # Deploy to Cloud Run
   gcloud run deploy deutschebahn-mcp-server \\
     --source . \\
     --region europe-west3 \\
     --allow-unauthenticated \\
     --port 8080
   ```

3. **Grant secret access permissions:**
   ```bash
   # Get your service account email from the deployment output
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \\
     --member="serviceAccount:your-service-account@your-project.iam.gserviceaccount.com" \\
     --role="roles/secretmanager.secretAccessor"
   ```

4. **Use your MCP server:**
   Your server will be available at the provided Cloud Run URL, e.g.:
   `https://deutschebahn-mcp-server-123456789.region.run.app/mcp`

#### Custom Domain Deployment (Production)

For production use with a custom domain and enhanced security:

1. **Follow basic deployment steps 1-3 above**

2. **Setup custom domain and load balancer** (see [Google Cloud Load Balancer docs](https://cloud.google.com/load-balancing/docs/https))

3. **Redeploy with custom domain:**
   ```bash
   gcloud run deploy deutschebahn-mcp-server \\
     --source . \\
     --region europe-west3 \\
     --allow-unauthenticated \\
     --port 8080 \\
     --set-env-vars CUSTOM_DOMAIN=your-domain.com
   ```

#### Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `CUSTOM_DOMAIN` | Optional | Your custom domain (enables enhanced security) | `mcp.example.com` |
| `CLOUD_RUN_URL` | Auto-detected | Cloud Run backend URL (auto-detected, override if needed) | `https://service-123.region.run.app` |
| `GCP_PROJECT_ID` | Auto-detected | Google Cloud project ID (auto-detected from metadata) | `my-project-123` |

**Note**: The `CLOUD_RUN_URL` is automatically detected from the Cloud Run environment. You only need to set `CUSTOM_DOMAIN` if using a custom domain with load balancer.

### Docker (Local Development)

```bash
# Build the image
docker build -t deutschebahn-mcp-server .

# Run locally with your API credentials
docker run -p 8080:8080 \\
  -e DB_API_KEY=your_db_api_key \\
  -e DB_API_SECRET=your_db_api_secret \\
  deutschebahn-mcp-server

# Server available at http://localhost:8080/mcp
```

### Security Considerations

- **Default deployment**: Uses Cloud Run's built-in HTTPS and allows access from the generated URL
- **Custom domain**: Restricts access to your specific domain only, blocks direct Cloud Run URL access
- **API credentials**: Always stored in Google Secret Manager, never in environment variables or code
- **Rate limiting**: Built-in protection (60 req/min, 1000 req/hour per client)

### Deployment Troubleshooting

**Secret Manager Access Issues:**
```bash
# Verify secrets exist
gcloud secrets list

# Check service account permissions
gcloud projects get-iam-policy YOUR_PROJECT_ID \\
  --flatten="bindings[].members" \\
  --filter="bindings.members:*gserviceaccount.com"
```

**Connection Issues:**
```bash
# Test your deployed service
curl https://your-service-url/health

# Check logs
gcloud run logs read --service=deutschebahn-mcp-server --region=your-region
```

## 📖 Usage Examples

### Smart Geographic Station Search
```python
# Ask Claude: "Find train stations near Munich city center"
# Uses: get_stations_by_position(48.1351, 11.5820) 
# → Smart regional filtering returns relevant Bavarian stations
```

### Enhanced Station Search
```python
# Ask Claude: "Find train stations in Frankfurt"
# Uses: get_station_by_name("Frankfurt")
# → API searchstring parameter with intelligent fallback
```

### Regional Service Centers
```python
# Ask Claude: "Find mobility service centers near Berlin"
# Uses: get_szentralen_by_location(52.5200, 13.4050)
# → Returns Berlin/Brandenburg S-Zentralen using city filtering
```

### Real-time Disruptions
```python
# Ask Claude: "Are there any delays at Berlin Hauptbahnhof?"
# Uses: recent_timetable_changes prompt
```

### Accurate Parking Search
```python
# Ask Claude: "Find parking at Frankfurt Hauptbahnhof"
# Uses: search_parking_facilities("Frankfurt Hauptbahnhof")
# → Uses real API stationName parameter for accurate results
```

## 🧪 Development

### Running Tests
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Run with coverage
pytest --cov=. tests/
```

### Code Quality
```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

### Local Testing with MCP Inspector
```bash
# Install MCP Inspector
npm install -g @modelcontextprotocol/inspector

# Inspect local server
mcp-inspector http://localhost:8080/mcp
```

## 🤝 Contributing

We welcome contributions from the community! Please see our [CONTRIBUTING.md](CONTRIBUTING.md) guide for detailed information.

### Quick Start for Contributors

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes with tests
4. Follow our development guidelines
5. Submit a pull request

### Attribution Request

**If you use this work, code, or concepts in your own projects, please provide proper attribution:**

```
Based on Deutsche Bahn MCP Server by Paul von Berg
https://github.com/PaulvonBerg/db-mcp-server
```

Thank you!

## 📝 API Reference

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DB_API_KEY` | Deutsche Bahn API client ID | Yes | - |
| `DB_API_SECRET` | Deutsche Bahn API secret key | Yes | - |
| `GCP_PROJECT_ID` | Google Cloud project ID | Auto-detected | - |
| `CUSTOM_DOMAIN` | Custom domain for enhanced security | Optional | - |
| `CLOUD_RUN_URL` | Cloud Run backend URL | Auto-detected | - |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | Optional | INFO |
| `PORT` | Server port | Optional | 8080 |

### Deutsche Bahn APIs Used

- **StaDa API v2**: Station master data
- **Timetables API v1**: Schedule and disruption data
- **Parking Information API v2**: DB Bahnpark facilities
- **FaSta API v2**: Facility status (elevators, escalators)

## 🐛 Troubleshooting

### Common Issues

**API Authentication Errors**
- Verify your DB API credentials are correct
- Check API key permissions and quotas

**Connection Issues**
- Ensure server is running on correct port
- Verify firewall settings allow connections
- Check Cloud Run service permissions

**MCP Client Connection**
- Verify MCP client configuration syntax
- Check server URL accessibility
- Ensure proper transport mode (http-only)

### Debugging

Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
python main.py
```

## 📄 License

This project is licensed under the **Creative Commons Attribution 4.0 International License (CC BY 4.0)** - see the [LICENSE](LICENSE) file for details.

### Attribution Requirements

When using this software or data, you must provide appropriate credit to:
- **Deutsche Bahn AG** for the underlying APIs and railway data (CC BY 4.0)
- **Contributors** of this MCP server implementation

### Deutsche Bahn API Compliance

This software accesses Deutsche Bahn's public APIs under different licensing terms:

- **Most APIs**: CC BY 4.0 (Station data, Timetables, Accessibility services)
- **Parking API**: "Datenlizenz Deutschland – Namensnennung – Version 2.0" (dl-de/by-2-0)

**Important**: Parking information data has additional restrictions:
- Content modification is **not permitted**
- Technical format changes are allowed
- Specific attribution required: "Parking Information Daten der DB BahnPark – API über den DB API Marketplace"

Users must comply with Deutsche Bahn's API terms of service at [developers.deutschebahn.com](https://developers.deutschebahn.com/).

**Note**: This software is not officially associated with Deutsche Bahn AG.

## ⚠️ Service Disclaimer

**For users of the live server at `https://db-mcp.datamonkey.tech`:**

This is a **community-provided service** hosted independently. Please note:

- **No uptime guarantees** - Service may be unavailable without notice
- **Rate limits apply** - 60 requests/minute, 1000/hour per client
- **Data accuracy** - Information is provided as-is from Deutsche Bahn APIs
- **No liability** - Use at your own risk for informational purposes only
- **Service monitoring** - Usage may be logged for operational purposes
- **Terms compliance** - Users must comply with Deutsche Bahn API terms

**For production use**, consider hosting your own instance using the deployment instructions above.

**Hosting provider**: This service is provided by an independent developer and is not affiliated with Deutsche Bahn AG

## 🙏 Acknowledgments

- Deutsche Bahn for providing public APIs
- Anthropic for the Model Context Protocol
- FastMCP library for Python MCP implementation

---

**Live Server**: https://db-mcp.datamonkey.tech  