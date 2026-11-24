import urllib.request
import urllib.error
from tools.registry import registry


# Fetch raw text content from a URL
async def web_fetch(url: str) -> str:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "MyAgent/1.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            content = response.read().decode("utf-8", errors="replace")
        if len(content) > 5000:
            content = content[:5000] + "\n... (truncated)"
        return content
    except urllib.error.URLError as e:
        return f"Error fetching URL: {e}"


registry.register(
    name="web_fetch",
    description="Fetch the content of a web page by URL. Returns the raw text content.",
    parameters={
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "The URL to fetch",
            }
        },
        "required": ["url"],
    },
    handler=web_fetch,
)