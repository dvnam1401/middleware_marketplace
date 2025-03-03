import requests
from decouple import config

class APIHandler:
    def __init__(self, api_url, token):
        self.api_url = api_url
        self.headers = {'Authorization': f'Bearer {token}'}

    def get_data(self, endpoint):
        try:
            response = requests.get(f"{self.api_url}{endpoint}", headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}

# Initialize handlers for each server
server1_handler = APIHandler(config('SERVER1_API_URL'), config('SERVER1_API_TOKEN'))
server2_handler = APIHandler(config('SERVER2_API_URL'), config('SERVER2_API_TOKEN'))

def get_all_products():
    products1 = server1_handler.get_data('get_product/')
    products2 = server2_handler.get_data('products/')
    if isinstance(products1, dict):
        products1 = products1.get('data', [])
    if isinstance(products2, dict):
        products2 = products2.get('data', [])
    return products1 + products2 if isinstance(products1, list) and isinstance(products2, list) else []