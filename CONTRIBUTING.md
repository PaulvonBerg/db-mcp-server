# Contributing to Deutsche Bahn MCP Server

Thank you for your interest in contributing to this project! This guide will help you get started with contributing to the Deutsche Bahn MCP Server.

## 🙏 Attribution Request

**If you use this work, code, or concepts in your own projects, please provide proper attribution:**

```
Based on Deutsche Bahn MCP Server by Paul von Berg
https://github.com/PaulvonBerg/db-mcp-server
```

We appreciate your consideration!

## 🚀 Getting Started

### Prerequisites

- Python 3.11 or higher
- Deutsche Bahn API credentials from [developers.deutschebahn.com](https://developers.deutschebahn.com)
- Git for version control
- A code editor (VS Code, PyCharm, etc.)

### Development Setup

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/[your-username]/deutsche-bahn-mcp-server.git
   cd deutsche-bahn-mcp-server
   ```

2. **Set up virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your DB API credentials
   ```

4. **Test the setup:**
   ```bash
   python main.py
   # Server should start at http://localhost:8080
   ```

## 🛠️ Development Guidelines

### Code Style

- **Follow PEP 8** Python style guidelines
- **Add type hints** to all function parameters and return values
- **Include docstrings** for all public functions and classes
- **Use descriptive variable names** and avoid abbreviations
- **Keep functions focused** - one responsibility per function

### Project Structure

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

### Adding New Features

#### 1. New MCP Tools

When adding new tools to the `tools/` directory:

```python
from server_instance import mcp
from utils import tool_error_handler, fetch_from_db_api
from models import YourModel

@mcp.tool()
@tool_error_handler
async def your_new_tool(param: str) -> List[YourModel]:
    """
    Clear description of what this tool does.
    
    Args:
        param: Description of the parameter
        
    Returns:
        Description of what's returned
        
    Examples:
        - your_new_tool("example") → Expected result
    """
    # Implementation here
    pass
```

#### 2. New Data Models

Add models to `models.py` using Pydantic:

```python
class YourModel(BaseModel):
    """Description of what this model represents."""
    field_name: str
    optional_field: Optional[int] = None
```

#### 3. New MCP Prompts

Add prompts to `prompts/travel_prompts.py`:

```python
@mcp.prompt(
    name="your_prompt_name",
    title="Human-Readable Title",
    description="Detailed description of what this prompt helps with..."
)
async def your_prompt(param: str):
    # Implementation here
    pass
```

### Testing

- **Test all new functionality** before submitting PRs
- **Include edge cases** in your testing
- **Test with real API responses** when possible
- **Verify error handling** works correctly

```bash
# Test locally
python main.py

# Test specific functionality
python -c "
import asyncio
from tools.your_tool import your_function
asyncio.run(your_function('test_param'))
"
```

## 🔒 Security Considerations

### API Credentials

- **Never commit** API keys or secrets to the repository
- **Use environment variables** for all sensitive configuration
- **Test with valid credentials** but use placeholder values in documentation

### Input Validation

- **Validate all user inputs** using the utilities in `utils.py`
- **Sanitize data** before passing to external APIs
- **Handle errors gracefully** and don't expose internal details

### Rate Limiting

- **Respect Deutsche Bahn API limits** in your implementations
- **Add appropriate delays** for bulk operations
- **Consider caching** for frequently accessed data

## 📋 Pull Request Process

### Before Submitting

1. **Ensure your code follows** the style guidelines above
2. **Test thoroughly** with real API credentials
3. **Update documentation** if you're adding new features
4. **Check for breaking changes** and note them in your PR

### PR Requirements

- **Clear title** describing what the PR does
- **Detailed description** of changes and why they're needed
- **List any breaking changes** or migration requirements
- **Include testing steps** for reviewers

### PR Template

```markdown
## Description
Brief description of what this PR does.

## Changes Made
- [ ] Added new feature X
- [ ] Fixed bug Y
- [ ] Updated documentation

## Testing
- [ ] Tested locally with valid API credentials
- [ ] Verified error handling works
- [ ] Checked for breaking changes

## Breaking Changes
List any breaking changes and migration steps needed.

## Additional Notes
Any other context or information reviewers should know.
```

## 🐛 Bug Reports

### Before Reporting

1. **Check existing issues** to avoid duplicates
2. **Test with the latest version** of the code
3. **Verify your API credentials** are working

### Bug Report Template

```markdown
## Bug Description
Clear description of what's wrong.

## Steps to Reproduce
1. Step one
2. Step two
3. Expected vs actual result

## Environment
- Python version:
- Operating system:
- API credentials working: Yes/No

## Error Messages
Include full error messages and stack traces.

## Additional Context
Any other relevant information.
```

## 🌟 Feature Requests

We welcome suggestions for new features! Please:

1. **Check existing issues** and discussions first
2. **Describe the use case** clearly
3. **Explain why** this would be valuable
4. **Consider implementation complexity** and maintenance burden

## 📞 Getting Help

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Documentation**: Check the README and code comments first

## 🏆 Recognition

Contributors will be acknowledged in:
- The project README
- Release notes for significant contributions
- Special recognition for major features or fixes

## 📜 License

By contributing to this project, you agree that your contributions will be licensed under the same CC BY 4.0 license as the project.

Thank you for contributing to the Deutsche Bahn MCP Server!
