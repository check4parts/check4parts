import requests


class BMPartsAdapter:
    API_URL = ""

    def fetch_data(self):
        response = requests.get(self.API_URL)
        if response.status_code == 200:
            return response.json()
        return {"error": "Failed to fetch data"}
