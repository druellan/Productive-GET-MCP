import os

class Config:
    """Configuration for Productive MCP Server"""

    def __init__(self):
        self.api_key = os.getenv(
            "PRODUCTIVE_API_KEY", ""
        )
        self.base_url = os.getenv("PRODUCTIVE_BASE_URL", "https://api.productive.io/api/v2")
        self.timeout = int(os.getenv("PRODUCTIVE_TIMEOUT", "30"))
        self.organization = int(os.getenv("PRODUCTIVE_ORGANIZATION", "27956"))

    def validate(self) -> bool:
        """Validate configuration"""
        return bool(self.api_key and self.base_url)

    @property
    def headers(self) -> dict:
        """Return headers for Productive API requests"""
        return {
            "X-Auth-Token": self.api_key,
            "X-Organization-Id": str(self.organization),
            "Content-Type": "application/vnd.api+json",
            "User-Agent": "Productive-MCP-Server/1.0"
        }

# Global config instance
config = Config()
