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
server2_handler = APIHandler(config('API_WORKOUT_URL'), config('WORKOUT_TOKEN'))

def get_all_products():
    products1 = server1_handler.get_data('get_product/')
    products2 = server2_handler.get_data('products/')
    if isinstance(products1, dict):
        products1 = products1.get('data', [])
    if isinstance(products2, dict):
        products2 = products2.get('data', [])
    return products1 + products2 if isinstance(products1, list) and isinstance(products2, list) else []

def get_all_books():
    # Hàm mới để lấy dữ liệu sách từ API sách
    books_api_url = config('BOOKS_API_URL')  # Định nghĩa trong .env
    books_api_token = config('BOOKS_API_TOKEN')  # Định nghĩa trong .env
    headers = {'Authorization': f'Bearer {books_api_token}'}
    
    try:
        response = requests.get(books_api_url, headers=headers)
        response.raise_for_status()
        books = response.json()
        # Chuẩn hóa dữ liệu sách để dùng trong template
        standardized_books = []
        for book in books:
            standardized_books.append({
                'product_id': book['id'],  # Dùng 'id' làm product_id để thống nhất
                'name': book['name'],
                'price': book['price'],
                'description': book['description'],
                'images': [book['image']],  # Giả định image là URL hoặc tên file
                'category': book['category'],
                'quantity': book['quanlity']  # Sửa typo nếu cần
            })
        return standardized_books
    except requests.exceptions.RequestException as e:
        print(f"Error fetching books: {e}")
        return []