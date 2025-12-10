import requests
import os
import json

class URLScanner:
    def __init__(self):
        self.api_key = os.environ.get('SAFE_BROWSING_API_KEY')
        self.api_url = "https://safebrowsing.googleapis.com/v4/threatMatches:find"

    def scan_url(self, url):
        """
        Scans a URL using Google Safe Browsing API.
        Returns a dictionary with status and details.
        """
        if not self.api_key:
            return {
                "status": "warning",
                "message": "API Key not configured. Please set SAFE_BROWSING_API_KEY in environment variables.",
                "details": "Running in mock mode.",
                "safe": True # Default to safe in mock mode to not scare, or maybe Warning?
            }

        payload = {
            "client": {
                "clientId": "social-engineering-simulator",
                "clientVersion": "1.0.0"
            },
            "threatInfo": {
                "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"],
                "platformTypes": ["ANY_PLATFORM"],
                "threatEntryTypes": ["URL"],
                "threatEntries": [
                    {"url": url}
                ]
            }
        }

        try:
            params = {'key': self.api_key}
            response = requests.post(self.api_url, params=params, json=payload)
            response.raise_for_status()
            data = response.json()

            if "matches" in data:
                # Threat found
                matches = data["matches"]
                threat_types = list(set([match["threatType"] for match in matches]))
                return {
                    "status": "danger",
                    "safe": False,
                    "message": "Threat Detected!",
                    "details": f"This URL is flagged as: {', '.join(threat_types)}"
                }
            else:
                # No threat found
                return {
                    "status": "success",
                    "safe": True,
                    "message": "URL appears safe.",
                    "details": "No threats found in Google Safe Browsing database."
                }

        except Exception as e:
            return {
                "status": "error",
                "safe": False,
                "message": "Error scanning URL",
                "details": str(e)
            }
