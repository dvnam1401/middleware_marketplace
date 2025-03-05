from django.shortcuts import render, redirect
from django.http import JsonResponse
from .api_handlers import get_all_products, get_all_books  
from decouple import config
from django.views.decorators.csrf import csrf_exempt
import requests
def home(request):
    products = get_all_products() or []  # Nếu không có products, trả về danh sách rỗng
    books = get_all_books() or []  # Nếu không có books, trả về danh sách rỗng
    return render(request, 'home.html', {'products': products, 'books': books})

# def product_detail(request, product_id):
#     products = get_all_products()
#     product = next((p for p in products if str(p.get('product_id')) == str(product_id)), None)
#     if product:
#         # Thay thế __NEWLINE__ bằng <br> để hiển thị xuống dòng
#         product['description'] = product['description'].replace('__NEWLINE__', '<br>')
#     api_orders_url = config('API_ORDERS_URL')
#     access_token = config('SERVER1_API_TOKEN')
#     return render(request, 'product_detail.html', {'product': product, 'api_orders_url': api_orders_url, 'access_token': access_token})
from django.views.decorators.http import require_POST
@csrf_exempt
@require_POST
def order_book(request):
    try:
        # Đọc dữ liệu từ request body
        body = request.body.decode('utf-8')
        if not body:
            return JsonResponse({'status': 'error', 'message': 'No data received'}, status=400)
        
        data = json.loads(body)
        book_id = data.get('id')  # Lấy từ client (bookId trong JS)
        quantity = data.get('quantity')  # Lấy từ client

        if not book_id or not quantity:
            return JsonResponse({'status': 'error', 'message': 'Missing id or quantity'}, status=400)

        # Gọi API đặt hàng sách với định dạng yêu cầu
        api_book_orders_url = config('API_BOOK_ORDERS_URL')
        books_api_token = config('BOOKS_API_TOKEN')
        headers = {
            'Authorization': f'Bearer {books_api_token}',
            'Content-Type': 'application/json'
        }
        payload = {
            'productid': int(book_id),  # Đổi tên thành 'productid' theo API yêu cầu
            'number_of_items': int(quantity)  # Đổi tên thành 'number_of_items'
        }

        response = requests.post(api_book_orders_url, json=payload, headers=headers)
        response.raise_for_status()  # Nếu có lỗi HTTP, sẽ raise exception

        # Nếu server trả về thành công (status 200), trả về thông báo
        return JsonResponse({
            'status': 'success',
            'message': 'Mua hàng thành công',  # Thông báo cụ thể
            'data': response.json()  # Trả về dữ liệu từ API nếu có
        })

    except requests.exceptions.RequestException as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Failed to order book: {str(e)}'
        }, status=500)
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

def product_detail(request, product_id):
    products = get_all_products()
    product = next((p for p in products if str(p.get('product_id')) == str(product_id)), None)
    
    if product:
        product['description'] = product['description'].replace('__NEWLINE__', '<br>')
        api_orders_url = config('API_ORDERS_URL')
        access_token = config('SERVER1_API_TOKEN')
        return render(request, 'product_detail.html', {
            'product': product,
            'api_orders_url': api_orders_url,
            'access_token': access_token
        })
    
    return render(request, 'product_detail.html', {'product': None})

def book_detail(request, product_id):
    print(product_id)
    books = get_all_books()
    book = next((b for b in books if str(b.get('product_id')) == str(product_id)), None)
    
    if book:
        book['description'] = book['description'].replace('__NEWLINE__', '<br>')
        api_orders_url = config('API_ORDERS_URL')
        access_token = config('BOOKS_API_TOKEN')
        return render(request, 'book_detail.html', {
            'book': book,
            'api_orders_url': api_orders_url,
            'access_token': access_token
        })
    
    return render(request, 'book_detail.html', {'book': None})

# View để hiển thị form nhập liệu
def workout_form(request):
    return render(request, 'workout_form.html')

# views.py
def workout_details(request):
    if 'workout_data' not in request.session:
        return redirect('workout_form')

    workout_data = request.session['workout_data']

    # Tách video thành danh sách và giữ nguyên trong dữ liệu
    for day in workout_data["DT"]["WorkoutDays"]:
        for exercise in day["WorkoutExercises"]:
            # Check if video_male is a string before splitting
            if isinstance(exercise["Exercise"]["video_male"], str):
                exercise["Exercise"]["video_male"] = exercise["Exercise"]["video_male"].split(', ')
            # Make sure it's a list even if it's not a string
            elif not isinstance(exercise["Exercise"]["video_male"], list):
                exercise["Exercise"]["video_male"] = [str(exercise["Exercise"]["video_male"])]
                
            # Do the same for video_female if it exists
            if "video_female" in exercise["Exercise"]:
                if isinstance(exercise["Exercise"]["video_female"], str):
                    exercise["Exercise"]["video_female"] = exercise["Exercise"]["video_female"].split(', ')
                elif not isinstance(exercise["Exercise"]["video_female"], list):
                    exercise["Exercise"]["video_female"] = [str(exercise["Exercise"]["video_female"])]
    request.session['workout_data'] = workout_data
    return render(request, 'workout_details.html', {'workout_data': workout_data})

def workout_start(request):
    if 'workout_data' not in request.session:
        return redirect('workout_form')
    workout_data = request.session['workout_data']
    day = request.GET.get('day', 'Day 1')
    selected_day = next((d for d in workout_data['DT']['WorkoutDays'] if d['day_of_week'] == day), None)
    if selected_day is None:
        return redirect('workout_form')
    return render(request, 'workout_start.html', {'day': selected_day})

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

@require_POST
@csrf_exempt
def save_workout_data(request):
    if request.method == 'POST':
        try:
            # Đọc dữ liệu thô từ request body
            body = request.body.decode('utf-8')
            if not body:
                return JsonResponse({'status': 'error', 'message': 'No data received'}, status=400)

            # Parse JSON
            data = json.loads(body)
            workout_data = data.get('workout_data')
            if not workout_data:
                return JsonResponse({'status': 'error', 'message': 'Workout data not found in request'}, status=400)

            # Lưu vào session
            request.session['workout_data'] = workout_data
            return JsonResponse({'status': 'success'})
        except json.JSONDecodeError as e:
            return JsonResponse({'status': 'error', 'message': f'Invalid JSON: {str(e)}'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)

# Dữ liệu giả từ file JSON
def workout_plan(request):
    if request.method == 'POST':
        gender = request.POST.get('gender')
        weight = request.POST.get('weight')
        height = request.POST.get('height')
        age = request.POST.get('age')
        continent = request.POST.get('continent')

        # Sử dụng dữ liệu giả
        workout_data = mock_workout_data
        request.session['workout_data'] = workout_data
        return render(request, 'workout_plan.html', {'workout_data': workout_data})

    return redirect('workout_form')

def workout_plan(request):
    if request.method == 'POST':
        # Lấy thông tin từ form
        gender = request.POST.get('gender')
        weight = request.POST.get('weight')
        height = request.POST.get('height')
        age = request.POST.get('age')
        continent = request.POST.get('continent')

        # Chuẩn bị dữ liệu gửi lên API
        data = {
            'Gender': gender,
            'Weight': float(weight),
            'Height': float(height),
            'Age': int(age),
            'continent': continent
        }

        # Gọi API của server2
        api_workout_url = config('API_WORKOUT_URL')  # Lấy URL API từ config
        workout_token = config('WORKOUT_TOKEN')  # Lấy token từ config
        headers = {'Authorization': f'Bearer {workout_token}'}  # Thêm header Authorization

        try:
            response = requests.post(api_workout_url, json=data, headers=headers)
            
            if response.status_code == 200:
                # Nếu thành công, lấy dữ liệu trả về từ API
                workout_data = response.json()
                
                # Lưu dữ liệu vào session để sử dụng trong các trang khác
                request.session['workout_data'] = workout_data

                return render(request, 'workout_plan.html', {'workout_data': workout_data})
            else:
                # Nếu API trả về lỗi, trả về thông báo lỗi
                return JsonResponse({'error': 'Failed to fetch workout plan from API'}, status=500)
        
        except requests.exceptions.RequestException as e:
            # Nếu có lỗi kết nối API, trả về thông báo lỗi
            return JsonResponse({'error': f'API request failed: {str(e)}'}, status=500)

    # Nếu không phải POST, redirect về form
    return render(request, 'workout_form.html')

mock_workout_data = {
    "EC": 0,
    "EM": "Generative Workout Plan Success",
    "DT": {
        "training_split": "Upper/Lower",
        "training_split_vi": "Trên/Dưới",
        "goal": "Balanced fitness (strength, hypertrophy, endurance)",
        "goal_vi": "Cân bằng thể lực (sức mạnh, phì đại, sức bền)",
        "training_level": "Beginner/Intermediate",
        "training_level_vi": "Sơ cấp/Trung cấp",
        "WorkoutDays": [
            {
                "day_of_week": "Day 1",
                "day_of_week_vi": "Ngày 1",
                "WorkoutExercises": [
                    {
                        "sets": 3,
                        "reps": "8-12 rep",
                        "rest": 60,
                        "notes": "Controlled movements",
                        "notes_vi": "Chuyển động có kiểm soát",
                        "Exercise": {
                            "name": "Barbell Reverse Grip Bench Press",
                            "name_vi": "Máy ép băng ghế dự bị có tay cầm ngược Barbell",
                            "video_male": "https://media.musclewiki.com/media/uploads/videos/branded/male-Barbell-barbell-reverse-grip-bench-press-front.mp4#t=0.1, https://media.musclewiki.com/media/uploads/videos/branded/male-Barbell-barbell-reverse-grip-bench-press-side.mp4#t=0.1",
                            "video_female": "https://media.musclewiki.com/media/uploads/videos/branded/female-Barbell-barbell-reverse-grip-bench-press-front.mp4#t=0.1, https://media.musclewiki.com/media/uploads/videos/branded/female-Barbell-barbell-reverse-grip-bench-press-side.mp4#t=0.1",
                            "description": "",
                            "description_vi": "",
                            "link_description": "",
                            "step": "1. Lay flat on the bench with your feet on the ground. With straight arms unrack the bar with a reverse grip.\n2. Lower the bar to your lower chest\n3. Raise the bar until you've locked your elbows.\n",
                            "step_vi": "1. Nằm ngửa trên ghế, đặt chân xuống đất. Với cánh tay thẳng, tháo thanh bằng tay cầm ngược.\n2. Hạ thanh đòn xuống ngực dưới\n3. Nâng thanh đòn cho đến khi bạn khóa khuỷu tay.\n",
                            "GroupMuscle": {
                                "name": "Chest",
                                "name_vi": "Ngực"
                            },
                            "Equipment": {
                                "name": "Barbell",
                                "name_vi": "Thanh tạ",
                                "icon": "\n\n<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 67 40\" fill=\"none\">\n    <g stroke=\"currentColor\" stroke-linecap=\"round\" stroke-linejoin=\"round\" clip-path=\"url(#a)\">\n        <path stroke-width=\"1.757\" d=\"M25.435 17.064c.23-1.459.36-3.086.36-4.8 0-6.29-1.73-11.382-3.862-11.382M13.548 13.477c.207 5.715 1.844 10.171 3.838 10.171 2.131 0 3.86-5.099 3.86-11.383 0-6.284-1.729-11.386-3.86-11.386-1.994 0-3.635 4.453-3.838 10.167M62.33.879c2.132 0 3.86 5.096 3.86 11.383 0 6.287-1.728 11.38-3.86 11.38M53.942 13.477c.206 5.715 1.843 10.168 3.838 10.168 2.131 0 3.86-5.096 3.86-11.38C61.64 5.98 59.91.882 57.78.882c-1.995 0-3.635 4.453-3.838 10.167M17.386.879h4.547M17.386 23.645h4.547M57.78.879h4.55M57.78 23.645h4.55\"></path>\n        <path stroke-width=\"1.757\" d=\"M25.795 11.046h30.773c.67 0 1.215.546 1.215 1.216 0 .67-.545 1.215-1.215 1.215H25.795v-2.43ZM11.56 13.477h4.61a1.216 1.216 0 1 0 0-2.43h-4.61a1.216 1.216 0 1 0 0 2.43Z\"></path>\n        <path stroke-width=\"1.757\" d=\"M11.56 13.477h.118a1.216 1.216 0 1 0 0-2.43h-.118a1.216 1.216 0 0 0 0 2.43ZM66.165 11.046h2.328c.337 0 .64.137.861.358.222.221.358.524.358.86 0 .67-.546 1.216-1.216 1.216h-2.328M55.81 30.7c0 1.27-3.032 2.297-6.776 2.297-3.743 0-6.772-1.028-6.772-2.298\"></path>\n        <path stroke-width=\"1.757\" d=\"M48.313 26.328c-3.401.121-6.054 1.097-6.054 2.285 0 1.268 3.035 2.298 6.776 2.298 3.74 0 6.775-1.027 6.775-2.298 0-1.188-2.65-2.161-6.05-2.285\"></path>\n        <path stroke-width=\"1.054\" d=\"M48.868 28.086c-.791.027-1.407.255-1.407.53 0 .295.706.534 1.577.534.87 0 1.576-.24 1.576-.534 0-.275-.615-.503-1.407-.53\"></path>\n        <path stroke-width=\"1.757\" d=\"M55.81 28.61v2.09M42.262 28.61v2.09M44.7 24.394c0 2.134-5.096 3.862-11.384 3.862-6.287 0-11.38-1.728-11.38-3.862M32.1 16.009c-5.713.206-10.17 1.843-10.17 3.837 0 2.132 5.1 3.86 11.383 3.86 6.285 0 11.384-1.728 11.384-3.86 0-1.994-4.454-3.634-10.168-3.837\"></path>\n        <path stroke-width=\"1.757\" d=\"M33.035 18.961c-1.328.049-2.365.428-2.365.892 0 .494 1.185.897 2.647.897 1.46 0 2.646-.403 2.646-.898 0-.463-1.034-.845-2.364-.89M44.7 19.846v4.548M21.933 19.846v4.548M21.936 29.138c0 2.131 5.096 3.862 11.38 3.862 3.814 0 7.188-.637 9.252-1.616M44.7 26.843v-2.252M21.933 24.59v4.548\"></path>\n    </g>\n    <defs>\n        <clipPath id=\"a\">\n            <path fill=\"#fff\" d=\"M0 0h70.591v39H0z\"></path>\n        </clipPath>\n    </defs>\n</svg>"
                            },
                            "Difficulty": {
                                "name": "Intermediate",
                                "name_vi": "Trung cấp"
                            }
                        }
                    },
                    {
                        "sets": 3,
                        "reps": "8-12 rep",
                        "rest": 60,
                        "notes": "Stable core",
                        "notes_vi": "Cốt lõi ổn định",
                        "Exercise": {
                            "name": "Dumbbell Row Bilateral",
                            "name_vi": "Hàng tạ song phương",
                            "video_male": "https://media.musclewiki.com/media/uploads/videos/branded/male-Dumbbells-dumbbell-row-bilateral-front.mp4#t=0.1, https://media.musclewiki.com/media/uploads/videos/branded/male-Dumbbells-dumbbell-row-bilateral-side.mp4#t=0.1",
                            "video_female": "https://media.musclewiki.com/media/uploads/videos/branded/female-Dumbbells-dumbbell-row-bilateral-front.mp4#t=0.1, https://media.musclewiki.com/media/uploads/videos/branded/female-Dumbbells-dumbbell-row-bilateral-side.mp4#t=0.1",
                            "description": "",
                            "description_vi": "",
                            "link_description": "",
                            "step": "1. Grab both dumbbells and hinge forward at the hips. Make sure you keep a flat back.\n2. The closer your torso is to parallel with the ground the longer the range of motion will be at your shoulder. The better the results you'll get from the exercise.\n3. Let your arms hang freely, and then pull your elbow joint straight back toward the ceiling.\n",
                            "step_vi": "1. Nắm lấy cả hai quả tạ và xoay hông về phía trước. Hãy chắc chắn rằng bạn giữ một lưng phẳng.\n2. Thân của bạn càng gần song song với mặt đất thì phạm vi chuyển động của vai bạn càng dài. Kết quả bạn nhận được từ bài tập càng tốt.\n3. Để cánh tay của bạn buông thõng tự do, sau đó kéo khớp khuỷu tay thẳng về phía trần nhà.\n",
                            "GroupMuscle": {
                                "name": "Traps Middle",
                                "name_vi": "Bẫy giữa"
                            },
                            "Equipment": {
                                "name": "Dumbbells",
                                "name_vi": "Tạ đơn",
                                "icon": "\n<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 62 61\" fill=\"none\" >\n    <path stroke=\"currentColor\" stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-width=\"2\" d=\"M52.063 33.672c5.176-5.176 3.933-14.812-2.777-21.522-6.71-6.71-16.346-7.954-21.523-2.777-5.177 5.176-3.933 14.812 2.777 21.523 6.71 6.71 16.346 7.953 21.523 2.776Z\"></path>\n    <path stroke=\"currentColor\" stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-width=\"2\" d=\"M25.858 11.983a10.49 10.49 0 0 0-2.613 1.903c-5.18 5.18-3.93 14.81 2.78 21.522 6.711 6.71 16.341 7.953 21.518 2.776a10.422 10.422 0 0 0 1.904-2.613\"></path>\n    <path stroke=\"currentColor\" stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-width=\"2\" d=\"M20.337 28.597c-4.296-1.278-8.618-.596-11.448 2.234-4.623 4.623-3.512 13.234 2.486 19.23 5.997 5.998 14.604 7.106 19.227 2.483 2.827-2.826 3.512-7.151 2.238-11.444\"></path>\n    <path stroke=\"currentColor\" stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-width=\"2\" d=\"M7.188 33.167a9.231 9.231 0 0 0-2.333 1.701C.228 39.495 1.343 48.102 7.341 54.099c5.997 5.998 14.6 7.109 19.227 2.482a9.453 9.453 0 0 0 1.701-2.333M42.75 24.36c1.21-1.21.92-3.46-.648-5.027-1.566-1.567-3.817-1.857-5.026-.647-1.21 1.209-.92 3.46.648 5.026 1.567 1.567 3.817 1.857 5.026.648Z\"></path>\n    <path stroke=\"currentColor\" stroke-miterlimit=\"10\" stroke-width=\"2\" d=\"M23.444 32.3 18.846 36.9a4.02 4.02 0 1 0 5.685 5.685l4.598-4.598\"></path>\n</svg>"
                            },
                            "Difficulty": {
                                "name": "Beginner",
                                "name_vi": "Tập sự"
                            }
                        }
                    },
                    {
                        "sets": 3,
                        "reps": "8-12 rep",
                        "rest": 60,
                        "notes": "Control weight",
                        "notes_vi": "Kiểm soát cân nặng",
                        "Exercise": {
                            "name": "Dumbbell Overhead Press",
                            "name_vi": "Máy ép tạ trên cao",
                            "video_male": "https://media.musclewiki.com/media/uploads/videos/branded/male-Dumbbells-dumbbell-overhead-press-side.mp4#t=0.1, https://media.musclewiki.com/media/uploads/videos/branded/male-Dumbbells-dumbbell-overhead-press-front.mp4#t=0.1",
                            "video_female": "https://media.musclewiki.com/media/uploads/videos/branded/female-Dumbbells-dumbbell-overhead-press-side.mp4#t=0.1, https://media.musclewiki.com/media/uploads/videos/branded/female-Dumbbells-dumbbell-overhead-press-front.mp4#t=0.1",
                            "description": "",
                            "description_vi": "",
                            "link_description": "",
                            "step": "1. Start by standing with your feet shoulder-width apart and holding a dumbbell in each hand.\n2. Bring the dumbbells to your shoulders, with your palms facing forward and your elbows bent.\n3. From this starting position, extend your arms upwards so that the dumbbells are overhead.\n4. Make sure to keep your core engaged and your back straight throughout the movement.\n",
                            "step_vi": "1. Bắt đầu bằng cách đứng hai chân rộng bằng vai và mỗi tay cầm một quả tạ.\n2. Đưa tạ lên vai, lòng bàn tay hướng về phía trước và khuỷu tay cong.\n3. Từ vị trí bắt đầu này, mở rộng cánh tay của bạn lên trên để tạ ở trên đầu.\n4. Đảm bảo giữ cho lõi của bạn hoạt động và lưng thẳng trong suốt chuyển động.\n",
                            "GroupMuscle": {
                                "name": "Shoulders",
                                "name_vi": "Vai"
                            },
                            "Equipment": {
                                "name": "Dumbbells",
                                "name_vi": "Tạ đơn",
                                "icon": "\n<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 62 61\" fill=\"none\" >\n    <path stroke=\"currentColor\" stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-width=\"2\" d=\"M52.063 33.672c5.176-5.176 3.933-14.812-2.777-21.522-6.71-6.71-16.346-7.954-21.523-2.777-5.177 5.176-3.933 14.812 2.777 21.523 6.71 6.71 16.346 7.953 21.523 2.776Z\"></path>\n    <path stroke=\"currentColor\" stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-width=\"2\" d=\"M25.858 11.983a10.49 10.49 0 0 0-2.613 1.903c-5.18 5.18-3.93 14.81 2.78 21.522 6.711 6.71 16.341 7.953 21.518 2.776a10.422 10.422 0 0 0 1.904-2.613\"></path>\n    <path stroke=\"currentColor\" stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-width=\"2\" d=\"M20.337 28.597c-4.296-1.278-8.618-.596-11.448 2.234-4.623 4.623-3.512 13.234 2.486 19.23 5.997 5.998 14.604 7.106 19.227 2.483 2.827-2.826 3.512-7.151 2.238-11.444\"></path>\n    <path stroke=\"currentColor\" stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-width=\"2\" d=\"M7.188 33.167a9.231 9.231 0 0 0-2.333 1.701C.228 39.495 1.343 48.102 7.341 54.099c5.997 5.998 14.6 7.109 19.227 2.482a9.453 9.453 0 0 0 1.701-2.333M42.75 24.36c1.21-1.21.92-3.46-.648-5.027-1.566-1.567-3.817-1.857-5.026-.647-1.21 1.209-.92 3.46.648 5.026 1.567 1.567 3.817 1.857 5.026.648Z\"></path>\n    <path stroke=\"currentColor\" stroke-miterlimit=\"10\" stroke-width=\"2\" d=\"M23.444 32.3 18.846 36.9a4.02 4.02 0 1 0 5.685 5.685l4.598-4.598\"></path>\n</svg>"
                            },
                            "Difficulty": {
                                "name": "Novice",
                                "name_vi": "Người mới"
                            }
                        }
                    },
                    {
                        "sets": 3,
                        "reps": "As many reps as possible",
                        "rest": 60,
                        "notes": "Or Lat Pulldowns (918)",
                        "notes_vi": "Hoặc Lat Pulldown (918)",
                        "Exercise": {
                            "name": "Chin Ups",
                            "name_vi": "nâng cằm",
                            "video_male": "https://media.musclewiki.com/media/uploads/videos/branded/male-bodyweight-chinup-front.mp4#t=0.1, https://media.musclewiki.com/media/uploads/videos/branded/male-bodyweight-chinup-side.mp4#t=0.1",
                            "video_female": "https://media.musclewiki.com/media/uploads/videos/branded/female-bodyweight-chinup-front.mp4#t=0.1, https://media.musclewiki.com/media/uploads/videos/branded/female-bodyweight-chinup-side.mp4#t=0.1",
                            "description": "How To Perform The Chin Up\nSetup\nGrab the Chin Up bar with an underhand grip. Make sure the bars are set very deeply in your hand. Your palms should be making contact with the bar. \nNext, if you are using a bench or box to reach the Chin Up bars, step off of the step, and hold for a second, in a dead hang position. If you begin initiating the reps before the dead hang, you might swing too much to perform the exercise strictly. If you can reach the  bars without having to stand on anything, take your grip and then pull your feet slightly off the floor. Still hold for a second to prevent any swinging from happening.\nPull your shoulder blades down. This will engage your mid and lower traps and force your lats to do most of the work. Also, before beginning the first rep, make sure your elbows are extended.\nLower body\nAngle your legs forward slightly, push your hips back, and point your toes. This will force you to flex your abdominals and keep you more stable throughout the rep. (This will massively help you keep the reps strict).\nPerforming\nOnce you are in the proper position, begin to pull. Imagine trying to pull your elbows straight down to your sides.\nGet your chin over the bar before beginning the eccentric portion of the rap. Your elbows should fully extend at the bottom of each rep.\nProgressing The Chin Up\nDecide on a rep range. For example, 6 to 10. Once you are able to perform 10 reps with strict form, then it is time to progress. Do not be shy or hesitant to start adding weight  early on. Even if it is only 5 pounds. Progress is progress! From there, progress like you would any other exercise. Once you hit the top end of the rep range, add some more weight.\nThe best way to get better at doing Chin Ups is to do Chin Ups. But if you can't do them in the first place, then what should you do? ",
                            "description_vi": "Cách thực hiện động tác nâng cằm\nCài đặt\nNắm thanh Chin Up bằng tay cầm phía dưới. Đảm bảo các thanh được đặt rất sâu trong tay bạn. Lòng bàn tay của bạn phải tiếp xúc với thanh đòn. \nTiếp theo, nếu bạn đang sử dụng ghế dài hoặc hộp để chạm vào thanh Chin Up, hãy bước ra khỏi bậc thang và giữ trong tư thế treo người trong một giây. Nếu bạn bắt đầu thực hiện các lần lặp trước khi chết, bạn có thể vung quá nhiều để thực hiện bài tập một cách nghiêm túc. Nếu bạn có thể chạm tới các thanh mà không cần phải đứng trên bất cứ thứ gì, hãy nắm lấy tay rồi kéo nhẹ chân ra khỏi sàn. Vẫn giữ trong một giây để ngăn chặn bất kỳ sự lắc lư nào xảy ra.\nKéo bả vai của bạn xuống. Điều này sẽ thu hút các bẫy giữa và dưới của bạn và buộc các lat của bạn phải thực hiện hầu hết công việc. Ngoài ra, trước khi bắt đầu lần tập đầu tiên, hãy đảm bảo khuỷu tay của bạn được mở rộng.\nThân dưới\nHơi nghiêng chân về phía trước, đẩy hông về phía sau và hướng ngón chân về phía trước. Điều này sẽ buộc bạn phải gồng cơ bụng và giữ cho bạn ổn định hơn trong suốt quá trình tập. (Điều này sẽ giúp bạn giữ được số lần lặp lại một cách nghiêm ngặt).\nbiểu diễn\nKhi bạn đã ở đúng vị trí, hãy bắt đầu kéo. Hãy tưởng tượng bạn đang cố gắng kéo khuỷu tay thẳng xuống hai bên.\nĐưa cằm qua xà trước khi bắt đầu phần lập dị của đoạn rap. Khuỷu tay của bạn phải duỗi ra hoàn toàn ở cuối mỗi lần tập.\nTiến hành nâng cằm\nQuyết định về một phạm vi đại diện. Ví dụ: 6 đến 10. Khi bạn có thể thực hiện 10 lần với hình thức nghiêm ngặt thì đã đến lúc phải tiến bộ. Đừng ngại ngùng hay do dự khi bắt đầu tăng cân sớm. Dù chỉ có 5 pound. Tiến bộ là tiến bộ! Từ đó, tiến bộ giống như bất kỳ bài tập nào khác. Khi bạn đạt đến mức cao nhất của phạm vi số lần lặp lại, hãy tăng thêm trọng lượng.\nCách tốt nhất để thực hiện Chin Ups tốt hơn là thực hiện Chin Ups. Nhưng nếu bạn không thể thực hiện chúng ngay từ đầu thì bạn nên làm gì? ",
                            "link_description": "https://www.youtube.com/embed?v=tTXFD0R11aQ&feature=youtu.be",
                            "step": "1. Grab the bar shoulder width apart with a supinated grip (palms facing you)\n2. With your body hanging and arms fully extended, pull yourself up until your chin is past the bar.\n3. Slowly return to starting position. Repeat.\n",
                            "step_vi": "1. Nắm thanh tạ rộng bằng vai bằng một tay cầm ngửa (lòng bàn tay hướng về phía bạn)\n2. Với tư thế thả người và cánh tay duỗi thẳng hoàn toàn, hãy kéo người lên cho đến khi cằm vượt qua thanh.\n3. Từ từ quay trở lại vị trí ban đầu. Lặp lại.\n",
                            "GroupMuscle": {
                                "name": "Biceps",
                                "name_vi": "Bắp tay"
                            },
                            "Equipment": {
                                "name": "Bodyweight",
                                "name_vi": "Trọng lượng cơ thể",
                                "icon": "\n<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 63.14 155\" >\n    <defs>\n        <style>.bodyw__cls-1{fill:none;stroke:currentcolor;stroke-linecap:round;stroke-linejoin:round;stroke-width:6}</style>\n    </defs>\n    <g>\n        <path d=\"M31.57 2.5c5.23 0 7.63 4.24 7.63 9.47 0 2.31 5.13 12.36-7.63 12.36M31.57 2.5c-5.23 0-7.63 4.24-7.63 9.47 0 2.31-5.13 12.36 7.63 12.36M60.64 79.73c0 27.25-5.6-30.07-29.07-30.07S2.5 106.98 2.5 79.73s13.01-49.34 29.07-49.34 29.07 22.09 29.07 49.34Z\" class=\"bodyw__cls-1\"></path>\n        <path d=\"M52.22 140.27c0 45.35-20.65-50.05-20.65-50.05s-20.65 95.4-20.65 50.05 9.24-82.11 20.65-82.11 20.65 36.76 20.65 82.11Z\" class=\"bodyw__cls-1\"></path>\n    </g>\n</svg>"
                            },
                            "Difficulty": {
                                "name": "Intermediate",
                                "name_vi": "Trung cấp"
                            }
                        }
                    },
                    {
                        "sets": 3,
                        "reps": "10-15 rep",
                        "rest": 60,
                        "notes": "Control weight",
                        "notes_vi": "Kiểm soát cân nặng",
                        "Exercise": {
                            "name": "Dumbbell Curl",
                            "name_vi": "Quả tạ cuộn",
                            "video_male": "https://media.musclewiki.com/media/uploads/videos/branded/male-Dumbbells-dumbbell-curl-front.mp4#t=0.1, https://media.musclewiki.com/media/uploads/videos/branded/male-Dumbbells-dumbbell-curl-side.mp4#t=0.1",
                            "video_female": "https://media.musclewiki.com/media/uploads/videos/branded/female-Dumbbells-dumbbell-curl-front.mp4#t=0.1, https://media.musclewiki.com/media/uploads/videos/branded/female-Dumbbells-dumbbell-curl-side.mp4#t=0.1",
                            "description": "How To Perform the Dumbbell Bicep Curl\nSetup\nGrab two dumbbells and stand tall with your shoulder blades pulled back and your chest poked out. You can start with either the dumbbells in front of your quads or off to the sides of your legs. Whichever is more comfortable. Also, whichever will allow you to fully extend your elbows at the bottom of each rep.\nUse a shoulder width or slightly inside of shoulder width stance. \nPerforming \nBegin the rep by flexing your elbows. Try to touch your forearms to your biceps at the very top of the movement. Then begin the eccentric. Make sure to fully extend your elbows at the bottom of each rep so you get a full range of motion. \nIt is easy to use momentum on a bicep curl. We want our muscles and not momentum to do the work. So make sure you keep these strict. If you find yourself swinging the weight up, then your biceps have hit fatigue and it's time to end the set.",
                            "description_vi": "Cách thực hiện động tác gập bắp tay bằng tạ\nCài đặt\nLấy hai quả tạ và đứng thẳng với bả vai kéo về phía sau và ngực nhô ra. Bạn có thể bắt đầu với tạ ở phía trước cơ tứ đầu hoặc ở hai bên chân. Cái nào thoải mái hơn. Ngoài ra, điều nào sẽ cho phép bạn mở rộng hoàn toàn khuỷu tay của mình ở cuối mỗi lần tập.\nSử dụng tư thế rộng bằng vai hoặc hơi vào trong tư thế rộng bằng vai. \nbiểu diễn \nBắt đầu đại diện bằng cách uốn cong khuỷu tay của bạn. Cố gắng chạm cẳng tay vào bắp tay ở đầu chuyển động. Sau đó bắt đầu lập dị. Đảm bảo mở rộng hoàn toàn khuỷu tay của bạn ở cuối mỗi lần lặp lại để bạn có được phạm vi chuyển động đầy đủ. \nThật dễ dàng để sử dụng đà trên động tác uốn cong bắp tay. Chúng ta muốn cơ bắp của mình chứ không phải động lực để thực hiện công việc. Vì vậy hãy chắc chắn rằng bạn giữ những điều này nghiêm ngặt. Nếu bạn thấy mình vung tạ lên cao thì có nghĩa là bắp tay của bạn đã bị mỏi và đã đến lúc kết thúc hiệp tập.",
                            "link_description": "https://www.youtube.com/embed?v=tTXFD0R11aQ&feature=youtu.be",
                            "step": "1. Stand up straight with a dumbbell in each hand at arm's length.\n2. Raise one dumbbell and twist your forearm until it is vertical and your palm faces the shoulder.\n3. Lower to original position and repeat with opposite arm\n",
                            "step_vi": "1. Đứng thẳng với một quả tạ ở mỗi tay dài bằng sải tay.\n2. Nâng một quả tạ lên và vặn cẳng tay cho đến khi nó thẳng đứng và lòng bàn tay hướng vào vai.\n3. Hạ xuống vị trí ban đầu và lặp lại với cánh tay đối diện\n",
                            "GroupMuscle": {
                                "name": "Biceps",
                                "name_vi": "Bắp tay"
                            },
                            "Equipment": {
                                "name": "Dumbbells",
                                "name_vi": "Tạ đơn",
                                "icon": "\n<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 62 61\" fill=\"none\" >\n    <path stroke=\"currentColor\" stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-width=\"2\" d=\"M52.063 33.672c5.176-5.176 3.933-14.812-2.777-21.522-6.71-6.71-16.346-7.954-21.523-2.777-5.177 5.176-3.933 14.812 2.777 21.523 6.71 6.71 16.346 7.953 21.523 2.776Z\"></path>\n    <path stroke=\"currentColor\" stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-width=\"2\" d=\"M25.858 11.983a10.49 10.49 0 0 0-2.613 1.903c-5.18 5.18-3.93 14.81 2.78 21.522 6.711 6.71 16.341 7.953 21.518 2.776a10.422 10.422 0 0 0 1.904-2.613\"></path>\n    <path stroke=\"currentColor\" stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-width=\"2\" d=\"M20.337 28.597c-4.296-1.278-8.618-.596-11.448 2.234-4.623 4.623-3.512 13.234 2.486 19.23 5.997 5.998 14.604 7.106 19.227 2.483 2.827-2.826 3.512-7.151 2.238-11.444\"></path>\n    <path stroke=\"currentColor\" stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-width=\"2\" d=\"M7.188 33.167a9.231 9.231 0 0 0-2.333 1.701C.228 39.495 1.343 48.102 7.341 54.099c5.997 5.998 14.6 7.109 19.227 2.482a9.453 9.453 0 0 0 1.701-2.333M42.75 24.36c1.21-1.21.92-3.46-.648-5.027-1.566-1.567-3.817-1.857-5.026-.647-1.21 1.209-.92 3.46.648 5.026 1.567 1.567 3.817 1.857 5.026.648Z\"></path>\n    <path stroke=\"currentColor\" stroke-miterlimit=\"10\" stroke-width=\"2\" d=\"M23.444 32.3 18.846 36.9a4.02 4.02 0 1 0 5.685 5.685l4.598-4.598\"></path>\n</svg>"
                            },
                            "Difficulty": {
                                "name": "Novice",
                                "name_vi": "Người mới"
                            }
                        }
                    },
                    {
                        "sets": 3,
                        "reps": "12-15 rep",
                        "rest": 60,
                        "notes": "Elbows close to body",
                        "notes_vi": "Khuỷu tay sát vào cơ thể",
                        "Exercise": {
                            "name": "Cable Rope Pushdown",
                            "name_vi": "Đẩy dây cáp",
                            "video_male": "https://media.musclewiki.com/media/uploads/videos/branded/male-Cables-cable-push-down-side.mp4#t=0.1, https://media.musclewiki.com/media/uploads/videos/branded/male-Cables-cable-push-down-front.mp4#t=0.1",
                            "video_female": "https://media.musclewiki.com/media/uploads/videos/branded/female-Cables-cable-push-down-side.mp4#t=0.1, https://media.musclewiki.com/media/uploads/videos/branded/female-Cables-cable-push-down-front.mp4#t=0.1",
                            "description": "How To Perform The Cable Pushdown\nSet Up\nSet the cable pin all the way to the top. You can use a rope or a straight bar attachment for this exercise. In our demo video, we are using a rope so our instructions will be specific to that.\nGrab onto the rope and take a few steps back. You can start with your elbows in an extended or flexed position.\nPush your butt back slightly. This will get your hips out of the way giving your arms enough room to fully extend.\nPerforming The Cable Pushdown\nMy favorite cue to use on the Tricep Push Down is, \"T-Rex arms.\" It's extremely important that you keep your upper arm and your elbows glued to your side. Your elbow joint should be causing the movement and your forearm should be the only moving body part. This will keep the stress and tension purely on your triceps and not recruit other body parts. Make sure to fully extend and flex your elbows on each rep.\nBe careful of swinging and bouncing on this exercise. It is very common to use too much weight on this exercise. If you find yourself having to use momentum, the weight is too heavy.\nAlso, if you notice your shoulders beginning to roll forward on the concentric, the weight is too heavy. Your central nervous system is extremely intelligent and will help you get from point A to point B by any means necessary. It will begin trying to recruit your anterior deltoid and pec major by rolling your shoulders forward on top of the rope or straight bar so you can press the weight down instead of performing a strict Triceps Extension.",
                            "description_vi": "Cách thực hiện việc đẩy cáp xuống\nCài đặt\nĐặt chốt cáp lên trên cùng. Bạn có thể sử dụng dây hoặc thanh đòn thẳng cho bài tập này. Trong video demo, chúng tôi đang sử dụng một sợi dây nên hướng dẫn của chúng tôi sẽ cụ thể về điều đó.\nNắm lấy sợi dây và lùi lại vài bước. Bạn có thể bắt đầu với khuỷu tay ở tư thế duỗi hoặc gập.\nĐẩy mông về phía sau một chút. Điều này sẽ giúp hông của bạn không bị cản trở, giúp cánh tay của bạn có đủ chỗ để duỗi ra hoàn toàn.\nThực hiện việc đẩy cáp xuống\nGợi ý yêu thích của tôi để sử dụng trong Bài tập đẩy cơ tam đầu là \"cánh tay T-Rex\". Điều cực kỳ quan trọng là bạn phải giữ cho cánh tay trên và khuỷu tay dán chặt vào bên mình. Khớp khuỷu tay của bạn phải gây ra chuyển động và cẳng tay của bạn phải là bộ phận duy nhất chuyển động trên cơ thể. Điều này sẽ giữ cho căng thẳng và căng thẳng hoàn toàn ở cơ tam đầu của bạn và không huy động các bộ phận cơ thể khác. Đảm bảo duỗi và uốn cong khuỷu tay của bạn hoàn toàn trong mỗi lần tập.\nHãy cẩn thận khi lắc lư và nảy trong bài tập này. Việc sử dụng quá nhiều tạ trong bài tập này là điều rất bình thường. Nếu bạn thấy mình phải dùng đà thì khối lượng tạ quá nặng.\nNgoài ra, nếu bạn nhận thấy vai của mình bắt đầu nghiêng về phía trước đồng tâm thì trọng lượng cơ thể quá nặng. Hệ thống thần kinh trung ương của bạn cực kỳ thông minh và sẽ giúp bạn đi từ điểm A đến điểm B bằng mọi cách cần thiết. Nó sẽ bắt đầu cố gắng huy động cơ delta trước và cơ ngực chính của bạn bằng cách lăn vai của bạn về phía trước trên dây hoặc thanh thẳng để bạn có thể ấn tạ xuống thay vì thực hiện bài tập Cơ tam đầu nghiêm ngặt.",
                            "link_description": "",
                            "step": "1. The cable should be set all the way at the top of the machine.\n2. Make sure to keep your upper arm glued at your side. Extend your elbows until you feel your triceps contract.\n",
                            "step_vi": "1. Cáp phải được đặt hoàn toàn ở phía trên cùng của máy.\n2. Đảm bảo giữ chặt cánh tay trên của bạn ở bên cạnh. Mở rộng khuỷu tay của bạn cho đến khi bạn cảm thấy cơ tam đầu của mình co lại.\n",
                            "GroupMuscle": {
                                "name": "Triceps",
                                "name_vi": "Tay sau"
                            },
                            "Equipment": {
                                "name": "Cables",
                                "name_vi": "Dây cáp",
                                "icon": "\n<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 155 140.96\" >\n    <defs>\n        <style>.cables__cls-1{fill:none;stroke:currentcolor;stroke-linecap:round;stroke-linejoin:round;stroke-width:6}</style>\n    </defs>\n    <g>\n        <circle cx=\"77.5\" cy=\"31.51\" r=\"7.48\" class=\"cables__cls-1\"></circle>\n        <path d=\"M77.5 27.98V2.5M77.5 55.28l-4.45 4.45-3.72 3.73-36.31 36.29-.05.06 8.17 8.17.06-.05 31.85-31.86 4.45-4.44\" class=\"cables__cls-1\"></path>\n        <path d=\"m42.94 109.671-28.78 28.78L2.5 126.79l28.78-28.78z\" class=\"cables__cls-1\"></path>\n        <path d=\"M28.52 100.78a37.17 37.17 0 0 1 6.27 17.05M18.08 111.22a37.17 37.17 0 0 1 6.27 17.05M7.64 121.65a37.22 37.22 0 0 1 6.21 16.49M77.5 38.99v16.29l4.45 4.44 3.73 3.73 36.3 36.3.05.06-8.17 8.17-.06-.05-31.85-31.85-4.45-4.45\" class=\"cables__cls-1\"></path>\n        <path d=\"m123.722 98.011 28.779 28.78-11.66 11.66-28.78-28.78z\" class=\"cables__cls-1\"></path>\n        <path d=\"M126.48 100.78a37.17 37.17 0 0 0-6.27 17.05M136.92 111.22a37.17 37.17 0 0 0-6.27 17.05M147.36 121.65a37.22 37.22 0 0 0-6.21 16.49M73.05 76.07V59.73M81.95 76.08V59.72\" class=\"cables__cls-1\"></path>\n    </g>\n</svg>"
                            },
                            "Difficulty": {
                                "name": "Novice",
                                "name_vi": "Người mới"
                            }
                        }
                    }
                ]
            },
            {
                "day_of_week": "Day 2",
                "day_of_week_vi": "Ngày 2",
                "WorkoutExercises": [
                    {
                        "sets": 3,
                        "reps": "8-12 rep",
                        "rest": 90,
                        "notes": "Proper form",
                        "notes_vi": "Hình thức phù hợp",
                        "Exercise": {
                            "name": "Barbell Squat",
                            "name_vi": "Squat tạ",
                            "video_male": "https://media.musclewiki.com/media/uploads/videos/branded/male-Barbell-barbell-squat-side.mp4#t=0.1, https://media.musclewiki.com/media/uploads/videos/branded/male-Barbell-barbell-squat-front.mp4#t=0.1",
                            "video_female": "https://media.musclewiki.com/media/uploads/videos/branded/female-Barbell-barbell-squat-side.mp4#t=0.1, https://media.musclewiki.com/media/uploads/videos/branded/female-Barbell-barbell-squat-front.mp4#t=0.1",
                            "description": "The barbell squat is a fundamental strength training exercise that targets multiple muscle groups, including the quadriceps, hamstrings, glutes, and lower back. This full-body workout provides numerous benefits, such as increased power, endurance, and stability.\nIn this guide, you will learn how to set up, perform, and maintain proper technique while doing barbell squats, as well as things to avoid.",
                            "description_vi": "Barbell squat là một bài tập rèn luyện sức mạnh cơ bản nhắm vào nhiều nhóm cơ, bao gồm cơ tứ đầu, gân kheo, cơ mông và lưng dưới. Bài tập toàn thân này mang lại nhiều lợi ích, chẳng hạn như tăng sức mạnh, sức bền và sự ổn định.\nTrong hướng dẫn này, bạn sẽ học cách thiết lập, thực hiện và duy trì kỹ thuật phù hợp trong khi thực hiện động tác squat với tạ, cũng như những điều cần tránh.",
                            "link_description": "",
                            "step": "1. Stand with your feet shoulder-width apart. Maintain the natural arch in your back, squeezing your shoulder blades and raising your chest.\n2. Grip the bar across your shoulders and support it on your upper back. Unwrack the bar by straightening your legs, and take a step back.\n3. Bend your knees as you lower the weight without altering the form of your back until your hips are below your knees.\n4. Raise the bar back to starting position, lift with your legs and exhale at the top.\n",
                            "step_vi": "1. Đứng hai chân rộng bằng vai. Giữ lưng cong tự nhiên, siết chặt xương bả vai và nâng ngực lên.\n2. Nắm chặt thanh đòn qua vai và đỡ nó ở lưng trên. Mở thanh đòn bằng cách duỗi thẳng chân và lùi lại một bước.\n3. Cong đầu gối khi hạ tạ xuống mà không làm thay đổi hình dạng của lưng cho đến khi hông ở dưới đầu gối.\n4. Nâng thanh đòn trở lại vị trí ban đầu, nâng bằng hai chân và thở ra ở phía trên.\n",
                            "GroupMuscle": {
                                "name": "Glutes",
                                "name_vi": "Cơ mông"
                            },
                            "Equipment": {
                                "name": "Barbell",
                                "name_vi": "Thanh tạ",
                                "icon": "\n<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 67 40\" fill=\"none\">\n    <g stroke=\"currentColor\" stroke-linecap=\"round\" stroke-linejoin=\"round\" clip-path=\"url(#a)\">\n        <path stroke-width=\"1.757\" d=\"M25.435 17.064c.23-1.459.36-3.086.36-4.8 0-6.29-1.73-11.382-3.862-11.382M13.548 13.477c.207 5.715 1.844 10.171 3.838 10.171 2.131 0 3.86-5.099 3.86-11.383 0-6.284-1.729-11.386-3.86-11.386-1.994 0-3.635 4.453-3.838 10.167M62.33.879c2.132 0 3.86 5.096 3.86 11.383 0 6.287-1.728 11.38-3.86 11.38M53.942 13.477c.206 5.715 1.843 10.168 3.838 10.168 2.131 0 3.86-5.096 3.86-11.38C61.64 5.98 59.91.882 57.78.882c-1.995 0-3.635 4.453-3.838 10.167M17.386.879h4.547M17.386 23.645h4.547M57.78.879h4.55M57.78 23.645h4.55\"></path>\n        <path stroke-width=\"1.757\" d=\"M25.795 11.046h30.773c.67 0 1.215.546 1.215 1.216 0 .67-.545 1.215-1.215 1.215H25.795v-2.43ZM11.56 13.477h4.61a1.216 1.216 0 1 0 0-2.43h-4.61a1.216 1.216 0 1 0 0 2.43Z\"></path>\n        <path stroke-width=\"1.757\" d=\"M11.56 13.477h.118a1.216 1.216 0 1 0 0-2.43h-.118a1.216 1.216 0 0 0 0 2.43ZM66.165 11.046h2.328c.337 0 .64.137.861.358.222.221.358.524.358.86 0 .67-.546 1.216-1.216 1.216h-2.328M55.81 30.7c0 1.27-3.032 2.297-6.776 2.297-3.743 0-6.772-1.028-6.772-2.298\"></path>\n        <path stroke-width=\"1.757\" d=\"M48.313 26.328c-3.401.121-6.054 1.097-6.054 2.285 0 1.268 3.035 2.298 6.776 2.298 3.74 0 6.775-1.027 6.775-2.298 0-1.188-2.65-2.161-6.05-2.285\"></path>\n        <path stroke-width=\"1.054\" d=\"M48.868 28.086c-.791.027-1.407.255-1.407.53 0 .295.706.534 1.577.534.87 0 1.576-.24 1.576-.534 0-.275-.615-.503-1.407-.53\"></path>\n        <path stroke-width=\"1.757\" d=\"M55.81 28.61v2.09M42.262 28.61v2.09M44.7 24.394c0 2.134-5.096 3.862-11.384 3.862-6.287 0-11.38-1.728-11.38-3.862M32.1 16.009c-5.713.206-10.17 1.843-10.17 3.837 0 2.132 5.1 3.86 11.383 3.86 6.285 0 11.384-1.728 11.384-3.86 0-1.994-4.454-3.634-10.168-3.837\"></path>\n        <path stroke-width=\"1.757\" d=\"M33.035 18.961c-1.328.049-2.365.428-2.365.892 0 .494 1.185.897 2.647.897 1.46 0 2.646-.403 2.646-.898 0-.463-1.034-.845-2.364-.89M44.7 19.846v4.548M21.933 19.846v4.548M21.936 29.138c0 2.131 5.096 3.862 11.38 3.862 3.814 0 7.188-.637 9.252-1.616M44.7 26.843v-2.252M21.933 24.59v4.548\"></path>\n    </g>\n    <defs>\n        <clipPath id=\"a\">\n            <path fill=\"#fff\" d=\"M0 0h70.591v39H0z\"></path>\n        </clipPath>\n    </defs>\n</svg>"
                            },
                            "Difficulty": {
                                "name": "Intermediate",
                                "name_vi": "Trung cấp"
                            }
                        }
                    },
                    {
                        "sets": 3,
                        "reps": "10-15 rep",
                        "rest": 90,
                        "notes": "Hinge at hips",
                        "notes_vi": "Bản lề ở hông",
                        "Exercise": {
                            "name": "Dumbbell Romanian Deadlift",
                            "name_vi": "Quả tạ Rumani Deadlift",
                            "video_male": "https://media.musclewiki.com/media/uploads/videos/branded/male-Dumbbells-dumbbell-romanian-deadlift-front.mp4#t=0.1, https://media.musclewiki.com/media/uploads/videos/branded/male-Dumbbells-dumbbell-romanian-deadlift-side.mp4#t=0.1",
                            "video_female": "https://media.musclewiki.com/media/uploads/videos/branded/female-Dumbbells-dumbbell-romanian-deadlift-front.mp4#t=0.1, https://media.musclewiki.com/media/uploads/videos/branded/female-Dumbbells-dumbbell-romanian-deadlift-side.mp4#t=0.1",
                            "description": "",
                            "description_vi": "",
                            "link_description": "",
                            "step": "1. Stand with a shoulder width stance. Push your butt back while leaving your knees MOSTLY extended.\n2. You should feel a stretch in your hamstrings. When you feel the stretch, push your hips forward to complete the rep.\n3. Do not push your hips all the way forward. This will hyperextend your spine. Just go to a normal standing position.\n",
                            "step_vi": "1. Đứng với tư thế rộng bằng vai. Đẩy mông ra sau trong khi đầu gối HẦU HẾT duỗi ra.\n2. Bạn sẽ cảm thấy gân kheo bị căng. Khi bạn cảm thấy căng, hãy đẩy hông về phía trước để hoàn thành động tác.\n3. Đừng đẩy hông về phía trước. Điều này sẽ làm giãn cột sống của bạn. Chỉ cần về tư thế đứng bình thường.\n",
                            "GroupMuscle": {
                                "name": "Lower back",
                                "name_vi": "lưng dưới"
                            },
                            "Equipment": {
                                "name": "Dumbbells",
                                "name_vi": "Tạ đơn",
                                "icon": "\n<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 62 61\" fill=\"none\" >\n    <path stroke=\"currentColor\" stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-width=\"2\" d=\"M52.063 33.672c5.176-5.176 3.933-14.812-2.777-21.522-6.71-6.71-16.346-7.954-21.523-2.777-5.177 5.176-3.933 14.812 2.777 21.523 6.71 6.71 16.346 7.953 21.523 2.776Z\"></path>\n    <path stroke=\"currentColor\" stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-width=\"2\" d=\"M25.858 11.983a10.49 10.49 0 0 0-2.613 1.903c-5.18 5.18-3.93 14.81 2.78 21.522 6.711 6.71 16.341 7.953 21.518 2.776a10.422 10.422 0 0 0 1.904-2.613\"></path>\n    <path stroke=\"currentColor\" stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-width=\"2\" d=\"M20.337 28.597c-4.296-1.278-8.618-.596-11.448 2.234-4.623 4.623-3.512 13.234 2.486 19.23 5.997 5.998 14.604 7.106 19.227 2.483 2.827-2.826 3.512-7.151 2.238-11.444\"></path>\n    <path stroke=\"currentColor\" stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-width=\"2\" d=\"M7.188 33.167a9.231 9.231 0 0 0-2.333 1.701C.228 39.495 1.343 48.102 7.341 54.099c5.997 5.998 14.6 7.109 19.227 2.482a9.453 9.453 0 0 0 1.701-2.333M42.75 24.36c1.21-1.21.92-3.46-.648-5.027-1.566-1.567-3.817-1.857-5.026-.647-1.21 1.209-.92 3.46.648 5.026 1.567 1.567 3.817 1.857 5.026.648Z\"></path>\n    <path stroke=\"currentColor\" stroke-miterlimit=\"10\" stroke-width=\"2\" d=\"M23.444 32.3 18.846 36.9a4.02 4.02 0 1 0 5.685 5.685l4.598-4.598\"></path>\n</svg>"
                            },
                            "Difficulty": {
                                "name": "Beginner",
                                "name_vi": "Tập sự"
                            }
                        }
                    },
                    {
                        "sets": 3,
                        "reps": "10-15 rep",
                        "rest": 90,
                        "notes": "Control weight",
                        "notes_vi": "Kiểm soát cân nặng",
                        "Exercise": {
                            "name": "Machine Leg Press",
                            "name_vi": "Máy ép chân",
                            "video_male": "https://media.musclewiki.com/media/uploads/videos/branded/male-machine-leg-press-front.mp4#t=0.1, https://media.musclewiki.com/media/uploads/videos/branded/male-machine-leg-press-side.mp4#t=0.1",
                            "video_female": "https://media.musclewiki.com/media/uploads/videos/branded/female-machine-leg-press-front.mp4#t=0.1, https://media.musclewiki.com/media/uploads/videos/branded/female-machine-leg-press-side.mp4#t=0.1",
                            "description": "",
                            "description_vi": "",
                            "link_description": "",
                            "step": "1. Place your legs on the platform with your feet at shoulder width.\n2. Release the weight and extend your legs fully, without locking your knees.\n3. Lower the weight until your legs are at a 90° angle (but DO NOT allow your butt and lower back to rise off of the pad. This will put your lower back in a rounded position, which is very dangerous.)\n4. Raise the weight back to starting position.\n",
                            "step_vi": "1. Đặt chân lên bục với bàn chân rộng bằng vai.\n2. Thả tạ ra và duỗi chân hoàn toàn mà không khóa đầu gối.\n3. Hạ tạ xuống cho đến khi chân bạn tạo thành một góc 90° (nhưng KHÔNG để mông và lưng dưới nhô lên khỏi đệm. Điều này sẽ khiến lưng dưới của bạn ở tư thế cong, điều này rất nguy hiểm.)\n4. Nâng tạ trở lại vị trí ban đầu.\n",
                            "GroupMuscle": {
                                "name": "Glutes",
                                "name_vi": "Cơ mông"
                            },
                            "Equipment": {
                                "name": "Machine",
                                "name_vi": "Máy móc",
                                "icon": "\n<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 67 40\" fill=\"none\" >\n    <g stroke=\"currentColor\" stroke-linecap=\"round\" stroke-linejoin=\"round\" clip-path=\"url(#a)\">\n        <path stroke-width=\"1.757\" d=\"M25.435 17.064c.23-1.459.36-3.086.36-4.8 0-6.29-1.73-11.382-3.862-11.382M13.548 13.477c.207 5.715 1.844 10.171 3.838 10.171 2.131 0 3.86-5.099 3.86-11.383 0-6.284-1.729-11.386-3.86-11.386-1.994 0-3.635 4.453-3.838 10.167M62.33.879c2.132 0 3.86 5.096 3.86 11.383 0 6.287-1.728 11.38-3.86 11.38M53.942 13.477c.206 5.715 1.843 10.168 3.838 10.168 2.131 0 3.86-5.096 3.86-11.38C61.64 5.98 59.91.882 57.78.882c-1.995 0-3.635 4.453-3.838 10.167M17.386.879h4.547M17.386 23.645h4.547M57.78.879h4.55M57.78 23.645h4.55\"></path>\n        <path stroke-width=\"1.757\" d=\"M25.795 11.046h30.773c.67 0 1.215.546 1.215 1.216 0 .67-.545 1.215-1.215 1.215H25.795v-2.43ZM11.56 13.477h4.61a1.216 1.216 0 1 0 0-2.43h-4.61a1.216 1.216 0 1 0 0 2.43Z\"></path>\n        <path stroke-width=\"1.757\" d=\"M11.56 13.477h.118a1.216 1.216 0 1 0 0-2.43h-.118a1.216 1.216 0 0 0 0 2.43ZM66.165 11.046h2.328c.337 0 .64.137.861.358.222.221.358.524.358.86 0 .67-.546 1.216-1.216 1.216h-2.328M55.81 30.7c0 1.27-3.032 2.297-6.776 2.297-3.743 0-6.772-1.028-6.772-2.298\"></path>\n        <path stroke-width=\"1.757\" d=\"M48.313 26.328c-3.401.121-6.054 1.097-6.054 2.285 0 1.268 3.035 2.298 6.776 2.298 3.74 0 6.775-1.027 6.775-2.298 0-1.188-2.65-2.161-6.05-2.285\"></path>\n        <path stroke-width=\"1.054\" d=\"M48.868 28.086c-.791.027-1.407.255-1.407.53 0 .295.706.534 1.577.534.87 0 1.576-.24 1.576-.534 0-.275-.615-.503-1.407-.53\"></path>\n        <path stroke-width=\"1.757\" d=\"M55.81 28.61v2.09M42.262 28.61v2.09M44.7 24.394c0 2.134-5.096 3.862-11.384 3.862-6.287 0-11.38-1.728-11.38-3.862M32.1 16.009c-5.713.206-10.17 1.843-10.17 3.837 0 2.132 5.1 3.86 11.383 3.86 6.285 0 11.384-1.728 11.384-3.86 0-1.994-4.454-3.634-10.168-3.837\"></path>\n        <path stroke-width=\"1.757\" d=\"M33.035 18.961c-1.328.049-2.365.428-2.365.892 0 .494 1.185.897 2.647.897 1.46 0 2.646-.403 2.646-.898 0-.463-1.034-.845-2.364-.89M44.7 19.846v4.548M21.933 19.846v4.548M21.936 29.138c0 2.131 5.096 3.862 11.38 3.862 3.814 0 7.188-.637 9.252-1.616M44.7 26.843v-2.252M21.933 24.59v4.548\"></path>\n    </g>\n    <defs>\n        <clipPath id=\"a\">\n            <path fill=\"#fff\" d=\"M0 0h70.591v39H0z\"></path>\n        </clipPath>\n    </defs>\n</svg>"
                            },
                            "Difficulty": {
                                "name": "Novice",
                                "name_vi": "Người mới"
                            }
                        }
                    },
                    {
                        "sets": 3,
                        "reps": "12-15 rep",
                        "rest": 60,
                        "notes": "Control movement",
                        "notes_vi": "Kiểm soát chuyển động",
                        "Exercise": {
                            "name": "Machine Leg Extension",
                            "name_vi": "Mở rộng chân máy",
                            "video_male": "https://media.musclewiki.com/media/uploads/videos/branded/male-machine-leg-extension-front.mp4#t=0.1, https://media.musclewiki.com/media/uploads/videos/branded/male-machine-leg-extension-side.mp4#t=0.1",
                            "video_female": "https://media.musclewiki.com/media/uploads/videos/branded/female-machine-leg-extension-front.mp4#t=0.1, https://media.musclewiki.com/media/uploads/videos/branded/female-machine-leg-extension-side.mp4#t=0.1",
                            "description": "",
                            "description_vi": "",
                            "link_description": "",
                            "step": "1. Sit on the machine with your back against the cushion and adjust the machine you are using so that your knees are at a 90 degree angle at the starting position.\n2. Raise the weight by extending your knees outward, then lower your leg to the starting position. Both movements should be done in a slow, controlled motion.\n",
                            "step_vi": "1. Ngồi trên máy, lưng dựa vào đệm và điều chỉnh máy bạn đang sử dụng sao cho đầu gối của bạn tạo thành một góc 90 độ ở vị trí ban đầu.\n2. Nâng tạ lên bằng cách duỗi đầu gối ra ngoài, sau đó hạ chân xuống vị trí ban đầu. Cả hai chuyển động nên được thực hiện một cách chậm rãi và có kiểm soát.\n",
                            "GroupMuscle": {
                                "name": "Quads",
                                "name_vi": "đùi trong"
                            },
                            "Equipment": {
                                "name": "Machine",
                                "name_vi": "Máy móc",
                                "icon": "\n<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 67 40\" fill=\"none\" >\n    <g stroke=\"currentColor\" stroke-linecap=\"round\" stroke-linejoin=\"round\" clip-path=\"url(#a)\">\n        <path stroke-width=\"1.757\" d=\"M25.435 17.064c.23-1.459.36-3.086.36-4.8 0-6.29-1.73-11.382-3.862-11.382M13.548 13.477c.207 5.715 1.844 10.171 3.838 10.171 2.131 0 3.86-5.099 3.86-11.383 0-6.284-1.729-11.386-3.86-11.386-1.994 0-3.635 4.453-3.838 10.167M62.33.879c2.132 0 3.86 5.096 3.86 11.383 0 6.287-1.728 11.38-3.86 11.38M53.942 13.477c.206 5.715 1.843 10.168 3.838 10.168 2.131 0 3.86-5.096 3.86-11.38C61.64 5.98 59.91.882 57.78.882c-1.995 0-3.635 4.453-3.838 10.167M17.386.879h4.547M17.386 23.645h4.547M57.78.879h4.55M57.78 23.645h4.55\"></path>\n        <path stroke-width=\"1.757\" d=\"M25.795 11.046h30.773c.67 0 1.215.546 1.215 1.216 0 .67-.545 1.215-1.215 1.215H25.795v-2.43ZM11.56 13.477h4.61a1.216 1.216 0 1 0 0-2.43h-4.61a1.216 1.216 0 1 0 0 2.43Z\"></path>\n        <path stroke-width=\"1.757\" d=\"M11.56 13.477h.118a1.216 1.216 0 1 0 0-2.43h-.118a1.216 1.216 0 0 0 0 2.43ZM66.165 11.046h2.328c.337 0 .64.137.861.358.222.221.358.524.358.86 0 .67-.546 1.216-1.216 1.216h-2.328M55.81 30.7c0 1.27-3.032 2.297-6.776 2.297-3.743 0-6.772-1.028-6.772-2.298\"></path>\n        <path stroke-width=\"1.757\" d=\"M48.313 26.328c-3.401.121-6.054 1.097-6.054 2.285 0 1.268 3.035 2.298 6.776 2.298 3.74 0 6.775-1.027 6.775-2.298 0-1.188-2.65-2.161-6.05-2.285\"></path>\n        <path stroke-width=\"1.054\" d=\"M48.868 28.086c-.791.027-1.407.255-1.407.53 0 .295.706.534 1.577.534.87 0 1.576-.24 1.576-.534 0-.275-.615-.503-1.407-.53\"></path>\n        <path stroke-width=\"1.757\" d=\"M55.81 28.61v2.09M42.262 28.61v2.09M44.7 24.394c0 2.134-5.096 3.862-11.384 3.862-6.287 0-11.38-1.728-11.38-3.862M32.1 16.009c-5.713.206-10.17 1.843-10.17 3.837 0 2.132 5.1 3.86 11.383 3.86 6.285 0 11.384-1.728 11.384-3.86 0-1.994-4.454-3.634-10.168-3.837\"></path>\n        <path stroke-width=\"1.757\" d=\"M33.035 18.961c-1.328.049-2.365.428-2.365.892 0 .494 1.185.897 2.647.897 1.46 0 2.646-.403 2.646-.898 0-.463-1.034-.845-2.364-.89M44.7 19.846v4.548M21.933 19.846v4.548M21.936 29.138c0 2.131 5.096 3.862 11.38 3.862 3.814 0 7.188-.637 9.252-1.616M44.7 26.843v-2.252M21.933 24.59v4.548\"></path>\n    </g>\n    <defs>\n        <clipPath id=\"a\">\n            <path fill=\"#fff\" d=\"M0 0h70.591v39H0z\"></path>\n        </clipPath>\n    </defs>\n</svg>"
                            },
                            "Difficulty": {
                                "name": "Novice",
                                "name_vi": "Người mới"
                            }
                        }
                    },
                    {
                        "sets": 3,
                        "reps": "12-15 rep",
                        "rest": 60,
                        "notes": "Squeeze hamstrings",
                        "notes_vi": "Siết chặt gân kheo",
                        "Exercise": {
                            "name": "Machine Seated Leg Curl",
                            "name_vi": "Máy cuộn chân ngồi",
                            "video_male": "https://media.musclewiki.com/media/uploads/videos/branded/male-Machine-machine-seated-leg-curl-front.mp4#t=0.1, https://media.musclewiki.com/media/uploads/videos/branded/male-Machine-machine-seated-leg-curl-side.mp4#t=0.1",
                            "video_female": "https://media.musclewiki.com/media/uploads/videos/branded/female-Machine-machine-seated-leg-curl-front.mp4#t=0.1, https://media.musclewiki.com/media/uploads/videos/branded/female-Machine-machine-seated-leg-curl-side.mp4#t=0.1",
                            "description": "",
                            "description_vi": "",
                            "link_description": "",
                            "step": "1. Sit back in the seat. Use the two handles to push yourself back into the chair.\n2. Flex your ankles and point your toes upward.\n3. Flex your knee bringing the pad backward, extend your knee without allowing the weight to touch back down.\n",
                            "step_vi": "1. Ngồi lại vào ghế. Sử dụng hai tay cầm để đẩy mình trở lại ghế.\n2. Co duỗi mắt cá chân và hướng ngón chân lên trên.\n3. Co duỗi đầu gối để đưa miếng đệm về phía sau, duỗi đầu gối mà không để trọng lượng chạm trở lại.\n",
                            "GroupMuscle": {
                                "name": "Hamstrings",
                                "name_vi": "Đùi sau"
                            },
                            "Equipment": {
                                "name": "Machine",
                                "name_vi": "Máy móc",
                                "icon": "\n<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 67 40\" fill=\"none\" >\n    <g stroke=\"currentColor\" stroke-linecap=\"round\" stroke-linejoin=\"round\" clip-path=\"url(#a)\">\n        <path stroke-width=\"1.757\" d=\"M25.435 17.064c.23-1.459.36-3.086.36-4.8 0-6.29-1.73-11.382-3.862-11.382M13.548 13.477c.207 5.715 1.844 10.171 3.838 10.171 2.131 0 3.86-5.099 3.86-11.383 0-6.284-1.729-11.386-3.86-11.386-1.994 0-3.635 4.453-3.838 10.167M62.33.879c2.132 0 3.86 5.096 3.86 11.383 0 6.287-1.728 11.38-3.86 11.38M53.942 13.477c.206 5.715 1.843 10.168 3.838 10.168 2.131 0 3.86-5.096 3.86-11.38C61.64 5.98 59.91.882 57.78.882c-1.995 0-3.635 4.453-3.838 10.167M17.386.879h4.547M17.386 23.645h4.547M57.78.879h4.55M57.78 23.645h4.55\"></path>\n        <path stroke-width=\"1.757\" d=\"M25.795 11.046h30.773c.67 0 1.215.546 1.215 1.216 0 .67-.545 1.215-1.215 1.215H25.795v-2.43ZM11.56 13.477h4.61a1.216 1.216 0 1 0 0-2.43h-4.61a1.216 1.216 0 1 0 0 2.43Z\"></path>\n        <path stroke-width=\"1.757\" d=\"M11.56 13.477h.118a1.216 1.216 0 1 0 0-2.43h-.118a1.216 1.216 0 0 0 0 2.43ZM66.165 11.046h2.328c.337 0 .64.137.861.358.222.221.358.524.358.86 0 .67-.546 1.216-1.216 1.216h-2.328M55.81 30.7c0 1.27-3.032 2.297-6.776 2.297-3.743 0-6.772-1.028-6.772-2.298\"></path>\n        <path stroke-width=\"1.757\" d=\"M48.313 26.328c-3.401.121-6.054 1.097-6.054 2.285 0 1.268 3.035 2.298 6.776 2.298 3.74 0 6.775-1.027 6.775-2.298 0-1.188-2.65-2.161-6.05-2.285\"></path>\n        <path stroke-width=\"1.054\" d=\"M48.868 28.086c-.791.027-1.407.255-1.407.53 0 .295.706.534 1.577.534.87 0 1.576-.24 1.576-.534 0-.275-.615-.503-1.407-.53\"></path>\n        <path stroke-width=\"1.757\" d=\"M55.81 28.61v2.09M42.262 28.61v2.09M44.7 24.394c0 2.134-5.096 3.862-11.384 3.862-6.287 0-11.38-1.728-11.38-3.862M32.1 16.009c-5.713.206-10.17 1.843-10.17 3.837 0 2.132 5.1 3.86 11.383 3.86 6.285 0 11.384-1.728 11.384-3.86 0-1.994-4.454-3.634-10.168-3.837\"></path>\n        <path stroke-width=\"1.757\" d=\"M33.035 18.961c-1.328.049-2.365.428-2.365.892 0 .494 1.185.897 2.647.897 1.46 0 2.646-.403 2.646-.898 0-.463-1.034-.845-2.364-.89M44.7 19.846v4.548M21.933 19.846v4.548M21.936 29.138c0 2.131 5.096 3.862 11.38 3.862 3.814 0 7.188-.637 9.252-1.616M44.7 26.843v-2.252M21.933 24.59v4.548\"></path>\n    </g>\n    <defs>\n        <clipPath id=\"a\">\n            <path fill=\"#fff\" d=\"M0 0h70.591v39H0z\"></path>\n        </clipPath>\n    </defs>\n</svg>"
                            },
                            "Difficulty": {
                                "name": "Novice",
                                "name_vi": "Người mới"
                            }
                        }
                    },
                    {
                        "sets": 3,
                        "reps": "15-20 rep",
                        "rest": 60,
                        "notes": "Full ROM",
                        "notes_vi": "ROM đầy đủ",
                        "Exercise": {
                            "name": "Dumbbell Calf Raise",
                            "name_vi": "Nâng tạ tạ",
                            "video_male": "https://media.musclewiki.com/media/uploads/videos/branded/male-Dumbbells-dumbbell-calf-raise-front.mp4#t=0.1, https://media.musclewiki.com/media/uploads/videos/branded/male-Dumbbells-dumbbell-calf-raise-side.mp4#t=0.1",
                            "video_female": "https://media.musclewiki.com/media/uploads/videos/branded/female-Dumbbells-dumbbell-calf-raise-front.mp4#t=0.1, https://media.musclewiki.com/media/uploads/videos/branded/female-Dumbbells-dumbbell-calf-raise-side.mp4#t=0.1",
                            "description": "",
                            "description_vi": "",
                            "link_description": "",
                            "step": "1. Stand tall with your feet on the ground. You can put the the balls of your feet on top of a plate to extend the range of motion.\n2. Imagine you have a string attached to your heels and pull your heels up toward the ceiling.\n",
                            "step_vi": "1. Đứng thẳng và đặt chân xuống đất. Bạn có thể đặt lòng bàn chân lên trên một tấm đĩa để mở rộng phạm vi chuyển động.\n2. Hãy tưởng tượng bạn có một sợi dây buộc vào gót chân và kéo gót chân lên phía trần nhà.\n",
                            "GroupMuscle": {
                                "name": "Calves",
                                "name_vi": "Bắp chân"
                            },
                            "Equipment": {
                                "name": "Dumbbells",
                                "name_vi": "Tạ đơn",
                                "icon": "\n<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 62 61\" fill=\"none\" >\n    <path stroke=\"currentColor\" stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-width=\"2\" d=\"M52.063 33.672c5.176-5.176 3.933-14.812-2.777-21.522-6.71-6.71-16.346-7.954-21.523-2.777-5.177 5.176-3.933 14.812 2.777 21.523 6.71 6.71 16.346 7.953 21.523 2.776Z\"></path>\n    <path stroke=\"currentColor\" stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-width=\"2\" d=\"M25.858 11.983a10.49 10.49 0 0 0-2.613 1.903c-5.18 5.18-3.93 14.81 2.78 21.522 6.711 6.71 16.341 7.953 21.518 2.776a10.422 10.422 0 0 0 1.904-2.613\"></path>\n    <path stroke=\"currentColor\" stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-width=\"2\" d=\"M20.337 28.597c-4.296-1.278-8.618-.596-11.448 2.234-4.623 4.623-3.512 13.234 2.486 19.23 5.997 5.998 14.604 7.106 19.227 2.483 2.827-2.826 3.512-7.151 2.238-11.444\"></path>\n    <path stroke=\"currentColor\" stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-width=\"2\" d=\"M7.188 33.167a9.231 9.231 0 0 0-2.333 1.701C.228 39.495 1.343 48.102 7.341 54.099c5.997 5.998 14.6 7.109 19.227 2.482a9.453 9.453 0 0 0 1.701-2.333M42.75 24.36c1.21-1.21.92-3.46-.648-5.027-1.566-1.567-3.817-1.857-5.026-.647-1.21 1.209-.92 3.46.648 5.026 1.567 1.567 3.817 1.857 5.026.648Z\"></path>\n    <path stroke=\"currentColor\" stroke-miterlimit=\"10\" stroke-width=\"2\" d=\"M23.444 32.3 18.846 36.9a4.02 4.02 0 1 0 5.685 5.685l4.598-4.598\"></path>\n</svg>"
                            },
                            "Difficulty": {
                                "name": "Novice",
                                "name_vi": "Người mới"
                            }
                        }
                    }
                ]
            },
            {
                "day_of_week": "Day 3",
                "day_of_week_vi": "Ngày 3",
                "WorkoutExercises": [
                    {
                        "sets": "null",
                        "reps": "",
                        "rest": "null",
                        "notes": "Rest or Active Recovery (light cardio",
                        "notes_vi": "Nghỉ ngơi hoặc Phục hồi tích cực (cardio nhẹ",
                        "Exercise": {
                            "name": "Rest",
                            "name_vi": "Nghỉ ngơi",
                            "video_male": "https://media.istockphoto.com/id/1288434083/vi/video/ng%C6%B0%E1%BB%9Di-ph%E1%BB%A5-n%E1%BB%AF-ch%C3%A2u-%C3%A1-th%C6%B0-gi%C3%A3n-t%E1%BA%A1i-sofa.mp4?s=mp4-640x640-is&k=20&c=uHl0HeisH8OXiX7f5WGh6eVy1Y2_0wSWmdfsAksZ-Pg=, https://media.istockphoto.com/id/1288434083/vi/video/ng%C6%B0%E1%BB%9Di-ph%E1%BB%A5-n%E1%BB%AF-ch%C3%A2u-%C3%A1-th%C6%B0-gi%C3%A3n-t%E1%BA%A1i-sofa.mp4?s=mp4-640x640-is&k=20&c=uHl0HeisH8OXiX7f5WGh6eVy1Y2_0wSWmdfsAksZ-Pg=",
                            "video_female": "https://media.istockphoto.com/id/1288434083/vi/video/ng%C6%B0%E1%BB%9Di-ph%E1%BB%A5-n%E1%BB%AF-ch%C3%A2u-%C3%A1-th%C6%B0-gi%C3%A3n-t%E1%BA%A1i-sofa.mp4?s=mp4-640x640-is&k=20&c=uHl0HeisH8OXiX7f5WGh6eVy1Y2_0wSWmdfsAksZ-Pg=, https://media.istockphoto.com/id/1288434083/vi/video/ng%C6%B0%E1%BB%9Di-ph%E1%BB%A5-n%E1%BB%AF-ch%C3%A2u-%C3%A1-th%C6%B0-gi%C3%A3n-t%E1%BA%A1i-sofa.mp4?s=mp4-640x640-is&k=20&c=uHl0HeisH8OXiX7f5WGh6eVy1Y2_0wSWmdfsAksZ-Pg=",
                            "description": "null",
                            "description_vi": "null",
                            "link_description": "null",
                            "step": "null",
                            "step_vi": "null",
                            "GroupMuscle": {
                                "name": "Biceps",
                                "name_vi": "Bắp tay"
                            },
                            "Equipment": {
                                "name": "Barbell",
                                "name_vi": "Thanh tạ",
                                "icon": "\n<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 67 40\" fill=\"none\">\n    <g stroke=\"currentColor\" stroke-linecap=\"round\" stroke-linejoin=\"round\" clip-path=\"url(#a)\">\n        <path stroke-width=\"1.757\" d=\"M25.435 17.064c.23-1.459.36-3.086.36-4.8 0-6.29-1.73-11.382-3.862-11.382M13.548 13.477c.207 5.715 1.844 10.171 3.838 10.171 2.131 0 3.86-5.099 3.86-11.383 0-6.284-1.729-11.386-3.86-11.386-1.994 0-3.635 4.453-3.838 10.167M62.33.879c2.132 0 3.86 5.096 3.86 11.383 0 6.287-1.728 11.38-3.86 11.38M53.942 13.477c.206 5.715 1.843 10.168 3.838 10.168 2.131 0 3.86-5.096 3.86-11.38C61.64 5.98 59.91.882 57.78.882c-1.995 0-3.635 4.453-3.838 10.167M17.386.879h4.547M17.386 23.645h4.547M57.78.879h4.55M57.78 23.645h4.55\"></path>\n        <path stroke-width=\"1.757\" d=\"M25.795 11.046h30.773c.67 0 1.215.546 1.215 1.216 0 .67-.545 1.215-1.215 1.215H25.795v-2.43ZM11.56 13.477h4.61a1.216 1.216 0 1 0 0-2.43h-4.61a1.216 1.216 0 1 0 0 2.43Z\"></path>\n        <path stroke-width=\"1.757\" d=\"M11.56 13.477h.118a1.216 1.216 0 1 0 0-2.43h-.118a1.216 1.216 0 0 0 0 2.43ZM66.165 11.046h2.328c.337 0 .64.137.861.358.222.221.358.524.358.86 0 .67-.546 1.216-1.216 1.216h-2.328M55.81 30.7c0 1.27-3.032 2.297-6.776 2.297-3.743 0-6.772-1.028-6.772-2.298\"></path>\n        <path stroke-width=\"1.757\" d=\"M48.313 26.328c-3.401.121-6.054 1.097-6.054 2.285 0 1.268 3.035 2.298 6.776 2.298 3.74 0 6.775-1.027 6.775-2.298 0-1.188-2.65-2.161-6.05-2.285\"></path>\n        <path stroke-width=\"1.054\" d=\"M48.868 28.086c-.791.027-1.407.255-1.407.53 0 .295.706.534 1.577.534.87 0 1.576-.24 1.576-.534 0-.275-.615-.503-1.407-.53\"></path>\n        <path stroke-width=\"1.757\" d=\"M55.81 28.61v2.09M42.262 28.61v2.09M44.7 24.394c0 2.134-5.096 3.862-11.384 3.862-6.287 0-11.38-1.728-11.38-3.862M32.1 16.009c-5.713.206-10.17 1.843-10.17 3.837 0 2.132 5.1 3.86 11.383 3.86 6.285 0 11.384-1.728 11.384-3.86 0-1.994-4.454-3.634-10.168-3.837\"></path>\n        <path stroke-width=\"1.757\" d=\"M33.035 18.961c-1.328.049-2.365.428-2.365.892 0 .494 1.185.897 2.647.897 1.46 0 2.646-.403 2.646-.898 0-.463-1.034-.845-2.364-.89M44.7 19.846v4.548M21.933 19.846v4.548M21.936 29.138c0 2.131 5.096 3.862 11.38 3.862 3.814 0 7.188-.637 9.252-1.616M44.7 26.843v-2.252M21.933 24.59v4.548\"></path>\n    </g>\n    <defs>\n        <clipPath id=\"a\">\n            <path fill=\"#fff\" d=\"M0 0h70.591v39H0z\"></path>\n        </clipPath>\n    </defs>\n</svg>"
                            },
                            "Difficulty": {
                                "name": "Beginner",
                                "name_vi": "Tập sự"
                            }
                        }
                    }
                ]
            },
            {
                "day_of_week": "Day 4",
                "day_of_week_vi": "Ngày 4",
                "WorkoutExercises": [
                    {
                        "sets": 3,
                        "reps": "12-15 rep",
                        "rest": 60,
                        "notes": "Lighter than Day 1",
                        "notes_vi": "Nhẹ hơn ngày 1",
                        "Exercise": {
                            "name": "Dumbbell Bench Press",
                            "name_vi": "Máy ép tạ tạ",
                            "video_male": "https://media.musclewiki.com/media/uploads/videos/branded/male-dumbbell-bench-press-front_y8zKZJl.mp4#t=0.1, https://media.musclewiki.com/media/uploads/videos/branded/male-dumbbell-bench-press-side_rqe1iTe.mp4#t=0.1",
                            "video_female": "https://media.musclewiki.com/media/uploads/videos/branded/female-dumbbell-bench-press-front_y8zKZJl.mp4#t=0.1, https://media.musclewiki.com/media/uploads/videos/branded/female-dumbbell-bench-press-side_rqe1iTe.mp4#t=0.1",
                            "description": "",
                            "description_vi": "",
                            "link_description": "",
                            "step": "1. Start by lying flat on a bench with a dumbbell in each hand.\n2. Hold the dumbbells at chest level with your palms facing forward.\n3. Engage your core and press the dumbbells upward until your arms are fully extended.\n",
                            "step_vi": "1. Bắt đầu bằng cách nằm thẳng trên ghế dài với một quả tạ ở mỗi tay.\n2. Giữ tạ ngang ngực với lòng bàn tay hướng về phía trước.\n3. Tập trung vào cơ thể và ấn tạ lên trên cho đến khi cánh tay của bạn được mở rộng hoàn toàn.\n",
                            "GroupMuscle": {
                                "name": "Triceps",
                                "name_vi": "Tay sau"
                            },
                            "Equipment": {
                                "name": "Dumbbells",
                                "name_vi": "Tạ đơn",
                                "icon": "\n<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 62 61\" fill=\"none\" >\n    <path stroke=\"currentColor\" stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-width=\"2\" d=\"M52.063 33.672c5.176-5.176 3.933-14.812-2.777-21.522-6.71-6.71-16.346-7.954-21.523-2.777-5.177 5.176-3.933 14.812 2.777 21.523 6.71 6.71 16.346 7.953 21.523 2.776Z\"></path>\n    <path stroke=\"currentColor\" stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-width=\"2\" d=\"M25.858 11.983a10.49 10.49 0 0 0-2.613 1.903c-5.18 5.18-3.93 14.81 2.78 21.522 6.711 6.71 16.341 7.953 21.518 2.776a10.422 10.422 0 0 0 1.904-2.613\"></path>\n    <path stroke=\"currentColor\" stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-width=\"2\" d=\"M20.337 28.597c-4.296-1.278-8.618-.596-11.448 2.234-4.623 4.623-3.512 13.234 2.486 19.23 5.997 5.998 14.604 7.106 19.227 2.483 2.827-2.826 3.512-7.151 2.238-11.444\"></path>\n    <path stroke=\"currentColor\" stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-width=\"2\" d=\"M7.188 33.167a9.231 9.231 0 0 0-2.333 1.701C.228 39.495 1.343 48.102 7.341 54.099c5.997 5.998 14.6 7.109 19.227 2.482a9.453 9.453 0 0 0 1.701-2.333M42.75 24.36c1.21-1.21.92-3.46-.648-5.027-1.566-1.567-3.817-1.857-5.026-.647-1.21 1.209-.92 3.46.648 5.026 1.567 1.567 3.817 1.857 5.026.648Z\"></path>\n    <path stroke=\"currentColor\" stroke-miterlimit=\"10\" stroke-width=\"2\" d=\"M23.444 32.3 18.846 36.9a4.02 4.02 0 1 0 5.685 5.685l4.598-4.598\"></path>\n</svg>"
                            },
                            "Difficulty": {
                                "name": "Novice",
                                "name_vi": "Người mới"
                            }
                        }
                    },
                    {
                        "sets": 3,
                        "reps": "12-15 rep",
                        "rest": 60,
                        "notes": "Lighter than Day 1",
                        "notes_vi": "Nhẹ hơn ngày 1",
                        "Exercise": {
                            "name": "Dumbbell Row Bilateral",
                            "name_vi": "Hàng tạ song phương",
                            "video_male": "https://media.musclewiki.com/media/uploads/videos/branded/male-Dumbbells-dumbbell-row-bilateral-front.mp4#t=0.1, https://media.musclewiki.com/media/uploads/videos/branded/male-Dumbbells-dumbbell-row-bilateral-side.mp4#t=0.1",
                            "video_female": "https://media.musclewiki.com/media/uploads/videos/branded/female-Dumbbells-dumbbell-row-bilateral-front.mp4#t=0.1, https://media.musclewiki.com/media/uploads/videos/branded/female-Dumbbells-dumbbell-row-bilateral-side.mp4#t=0.1",
                            "description": "",
                            "description_vi": "",
                            "link_description": "",
                            "step": "1. Grab both dumbbells and hinge forward at the hips. Make sure you keep a flat back.\n2. The closer your torso is to parallel with the ground the longer the range of motion will be at your shoulder. The better the results you'll get from the exercise.\n3. Let your arms hang freely, and then pull your elbow joint straight back toward the ceiling.\n",
                            "step_vi": "1. Nắm lấy cả hai quả tạ và xoay hông về phía trước. Hãy chắc chắn rằng bạn giữ một lưng phẳng.\n2. Thân của bạn càng gần song song với mặt đất thì phạm vi chuyển động của vai bạn càng dài. Kết quả bạn nhận được từ bài tập càng tốt.\n3. Để cánh tay của bạn buông thõng tự do, sau đó kéo khớp khuỷu tay thẳng về phía trần nhà.\n",
                            "GroupMuscle": {
                                "name": "Traps Middle",
                                "name_vi": "Bẫy giữa"
                            },
                            "Equipment": {
                                "name": "Dumbbells",
                                "name_vi": "Tạ đơn",
                                "icon": "\n<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 62 61\" fill=\"none\" >\n    <path stroke=\"currentColor\" stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-width=\"2\" d=\"M52.063 33.672c5.176-5.176 3.933-14.812-2.777-21.522-6.71-6.71-16.346-7.954-21.523-2.777-5.177 5.176-3.933 14.812 2.777 21.523 6.71 6.71 16.346 7.953 21.523 2.776Z\"></path>\n    <path stroke=\"currentColor\" stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-width=\"2\" d=\"M25.858 11.983a10.49 10.49 0 0 0-2.613 1.903c-5.18 5.18-3.93 14.81 2.78 21.522 6.711 6.71 16.341 7.953 21.518 2.776a10.422 10.422 0 0 0 1.904-2.613\"></path>\n    <path stroke=\"currentColor\" stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-width=\"2\" d=\"M20.337 28.597c-4.296-1.278-8.618-.596-11.448 2.234-4.623 4.623-3.512 13.234 2.486 19.23 5.997 5.998 14.604 7.106 19.227 2.483 2.827-2.826 3.512-7.151 2.238-11.444\"></path>\n    <path stroke=\"currentColor\" stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-width=\"2\" d=\"M7.188 33.167a9.231 9.231 0 0 0-2.333 1.701C.228 39.495 1.343 48.102 7.341 54.099c5.997 5.998 14.6 7.109 19.227 2.482a9.453 9.453 0 0 0 1.701-2.333M42.75 24.36c1.21-1.21.92-3.46-.648-5.027-1.566-1.567-3.817-1.857-5.026-.647-1.21 1.209-.92 3.46.648 5.026 1.567 1.567 3.817 1.857 5.026.648Z\"></path>\n    <path stroke=\"currentColor\" stroke-miterlimit=\"10\" stroke-width=\"2\" d=\"M23.444 32.3 18.846 36.9a4.02 4.02 0 1 0 5.685 5.685l4.598-4.598\"></path>\n</svg>"
                            },
                            "Difficulty": {
                                "name": "Beginner",
                                "name_vi": "Tập sự"
                            }
                        }
                    },
                    {
                        "sets": 3,
                        "reps": "10-15 rep",
                        "rest": 60,
                        "notes": "Controlled movements",
                        "notes_vi": "Chuyển động có kiểm soát",
                        "Exercise": {
                            "name": "Dumbbell Arnold Press",
                            "name_vi": "Quả tạ Arnold Press",
                            "video_male": "https://media.musclewiki.com/media/uploads/videos/branded/male-Dumbbells-dumbbell-arnold-press-front.mp4#t=0.1, https://media.musclewiki.com/media/uploads/videos/branded/male-Dumbbells-dumbbell-arnold-press-side.mp4#t=0.1",
                            "video_female": "https://media.musclewiki.com/media/uploads/videos/branded/female-Dumbbells-dumbbell-arnold-press-front.mp4#t=0.1, https://media.musclewiki.com/media/uploads/videos/branded/female-Dumbbells-dumbbell-arnold-press-side.mp4#t=0.1",
                            "description": "",
                            "description_vi": "",
                            "link_description": "",
                            "step": "1. Stand with both palms facing you.\n2. Begin to press the dumbbells to the ceiling while rotating your palms.\n3. When you reach elbow extension, your palms should be facing forward.\n",
                            "step_vi": "1. Đứng với cả hai lòng bàn tay hướng về phía bạn.\n2. Bắt đầu ấn tạ lên trần nhà đồng thời xoay lòng bàn tay.\n3. Khi bạn duỗi khuỷu tay, lòng bàn tay của bạn phải hướng về phía trước.\n",
                            "GroupMuscle": {
                                "name": "Shoulders",
                                "name_vi": "Vai"
                            },
                            "Equipment": {
                                "name": "Dumbbells",
                                "name_vi": "Tạ đơn",
                                "icon": "\n<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 62 61\" fill=\"none\" >\n    <path stroke=\"currentColor\" stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-width=\"2\" d=\"M52.063 33.672c5.176-5.176 3.933-14.812-2.777-21.522-6.71-6.71-16.346-7.954-21.523-2.777-5.177 5.176-3.933 14.812 2.777 21.523 6.71 6.71 16.346 7.953 21.523 2.776Z\"></path>\n    <path stroke=\"currentColor\" stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-width=\"2\" d=\"M25.858 11.983a10.49 10.49 0 0 0-2.613 1.903c-5.18 5.18-3.93 14.81 2.78 21.522 6.711 6.71 16.341 7.953 21.518 2.776a10.422 10.422 0 0 0 1.904-2.613\"></path>\n    <path stroke=\"currentColor\" stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-width=\"2\" d=\"M20.337 28.597c-4.296-1.278-8.618-.596-11.448 2.234-4.623 4.623-3.512 13.234 2.486 19.23 5.997 5.998 14.604 7.106 19.227 2.483 2.827-2.826 3.512-7.151 2.238-11.444\"></path>\n    <path stroke=\"currentColor\" stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-width=\"2\" d=\"M7.188 33.167a9.231 9.231 0 0 0-2.333 1.701C.228 39.495 1.343 48.102 7.341 54.099c5.997 5.998 14.6 7.109 19.227 2.482a9.453 9.453 0 0 0 1.701-2.333M42.75 24.36c1.21-1.21.92-3.46-.648-5.027-1.566-1.567-3.817-1.857-5.026-.647-1.21 1.209-.92 3.46.648 5.026 1.567 1.567 3.817 1.857 5.026.648Z\"></path>\n    <path stroke=\"currentColor\" stroke-miterlimit=\"10\" stroke-width=\"2\" d=\"M23.444 32.3 18.846 36.9a4.02 4.02 0 1 0 5.685 5.685l4.598-4.598\"></path>\n</svg>"
                            },
                            "Difficulty": {
                                "name": "Intermediate",
                                "name_vi": "Trung cấp"
                            }
                        }
                    },
                    {
                        "sets": 3,
                        "reps": "15-20 rep",
                        "rest": 45,
                        "notes": "Light weight",
                        "notes_vi": "Trọng lượng nhẹ",
                        "Exercise": {
                            "name": "Cable Rope Face Pulls",
                            "name_vi": "Kéo mặt dây cáp",
                            "video_male": "https://media.musclewiki.com/media/uploads/videos/branded/male-Machine-machine-face-pulls-front.mp4#t=0.1, https://media.musclewiki.com/media/uploads/videos/branded/male-Machine-machine-face-pulls-side.mp4#t=0.1",
                            "video_female": "https://media.musclewiki.com/media/uploads/videos/branded/female-Machine-machine-face-pulls-front.mp4#t=0.1, https://media.musclewiki.com/media/uploads/videos/branded/female-Machine-machine-face-pulls-side.mp4#t=0.1",
                            "description": "",
                            "description_vi": "",
                            "link_description": "",
                            "step": "1. Facing the pulley, pull the weight towards you while keeping your arms parallel to the ground.\n2. Pull your hands back to both sides of your head and hold the position.\n3. Slowly return weight to starting position. Repeat.\n",
                            "step_vi": "1. Hướng mặt về phía ròng rọc, kéo vật nặng về phía bạn đồng thời giữ hai cánh tay song song với mặt đất.\n2. Kéo hai tay về hai bên đầu và giữ nguyên tư thế.\n3. Từ từ đưa trọng lượng trở lại vị trí ban đầu. Lặp lại.\n",
                            "GroupMuscle": {
                                "name": "Shoulders",
                                "name_vi": "Vai"
                            },
                            "Equipment": {
                                "name": "Cables",
                                "name_vi": "Dây cáp",
                                "icon": "\n<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 155 140.96\" >\n    <defs>\n        <style>.cables__cls-1{fill:none;stroke:currentcolor;stroke-linecap:round;stroke-linejoin:round;stroke-width:6}</style>\n    </defs>\n    <g>\n        <circle cx=\"77.5\" cy=\"31.51\" r=\"7.48\" class=\"cables__cls-1\"></circle>\n        <path d=\"M77.5 27.98V2.5M77.5 55.28l-4.45 4.45-3.72 3.73-36.31 36.29-.05.06 8.17 8.17.06-.05 31.85-31.86 4.45-4.44\" class=\"cables__cls-1\"></path>\n        <path d=\"m42.94 109.671-28.78 28.78L2.5 126.79l28.78-28.78z\" class=\"cables__cls-1\"></path>\n        <path d=\"M28.52 100.78a37.17 37.17 0 0 1 6.27 17.05M18.08 111.22a37.17 37.17 0 0 1 6.27 17.05M7.64 121.65a37.22 37.22 0 0 1 6.21 16.49M77.5 38.99v16.29l4.45 4.44 3.73 3.73 36.3 36.3.05.06-8.17 8.17-.06-.05-31.85-31.85-4.45-4.45\" class=\"cables__cls-1\"></path>\n        <path d=\"m123.722 98.011 28.779 28.78-11.66 11.66-28.78-28.78z\" class=\"cables__cls-1\"></path>\n        <path d=\"M126.48 100.78a37.17 37.17 0 0 0-6.27 17.05M136.92 111.22a37.17 37.17 0 0 0-6.27 17.05M147.36 121.65a37.22 37.22 0 0 0-6.21 16.49M73.05 76.07V59.73M81.95 76.08V59.72\" class=\"cables__cls-1\"></path>\n    </g>\n</svg>"
                            },
                            "Difficulty": {
                                "name": "Novice",
                                "name_vi": "Người mới"
                            }
                        }
                    },
                    {
                        "sets": 2,
                        "reps": "15-20 rep",
                        "rest": 45,
                        "notes": "Lighter than Day 1",
                        "notes_vi": "Nhẹ hơn ngày 1",
                        "Exercise": {
                            "name": "Dumbbell Curl",
                            "name_vi": "Quả tạ cuộn",
                            "video_male": "https://media.musclewiki.com/media/uploads/videos/branded/male-Dumbbells-dumbbell-curl-front.mp4#t=0.1, https://media.musclewiki.com/media/uploads/videos/branded/male-Dumbbells-dumbbell-curl-side.mp4#t=0.1",
                            "video_female": "https://media.musclewiki.com/media/uploads/videos/branded/female-Dumbbells-dumbbell-curl-front.mp4#t=0.1, https://media.musclewiki.com/media/uploads/videos/branded/female-Dumbbells-dumbbell-curl-side.mp4#t=0.1",
                            "description": "How To Perform the Dumbbell Bicep Curl\nSetup\nGrab two dumbbells and stand tall with your shoulder blades pulled back and your chest poked out. You can start with either the dumbbells in front of your quads or off to the sides of your legs. Whichever is more comfortable. Also, whichever will allow you to fully extend your elbows at the bottom of each rep.\nUse a shoulder width or slightly inside of shoulder width stance. \nPerforming \nBegin the rep by flexing your elbows. Try to touch your forearms to your biceps at the very top of the movement. Then begin the eccentric. Make sure to fully extend your elbows at the bottom of each rep so you get a full range of motion. \nIt is easy to use momentum on a bicep curl. We want our muscles and not momentum to do the work. So make sure you keep these strict. If you find yourself swinging the weight up, then your biceps have hit fatigue and it's time to end the set.",
                            "description_vi": "Cách thực hiện động tác gập bắp tay bằng tạ\nCài đặt\nLấy hai quả tạ và đứng thẳng với bả vai kéo về phía sau và ngực nhô ra. Bạn có thể bắt đầu với tạ ở phía trước cơ tứ đầu hoặc ở hai bên chân. Cái nào thoải mái hơn. Ngoài ra, điều nào sẽ cho phép bạn mở rộng hoàn toàn khuỷu tay của mình ở cuối mỗi lần tập.\nSử dụng tư thế rộng bằng vai hoặc hơi vào trong tư thế rộng bằng vai. \nbiểu diễn \nBắt đầu đại diện bằng cách uốn cong khuỷu tay của bạn. Cố gắng chạm cẳng tay vào bắp tay ở đầu chuyển động. Sau đó bắt đầu lập dị. Đảm bảo mở rộng hoàn toàn khuỷu tay của bạn ở cuối mỗi lần lặp lại để bạn có được phạm vi chuyển động đầy đủ. \nThật dễ dàng để sử dụng đà trên động tác uốn cong bắp tay. Chúng ta muốn cơ bắp của mình chứ không phải động lực để thực hiện công việc. Vì vậy hãy chắc chắn rằng bạn giữ những điều này nghiêm ngặt. Nếu bạn thấy mình vung tạ lên cao thì có nghĩa là bắp tay của bạn đã bị mỏi và đã đến lúc kết thúc hiệp tập.",
                            "link_description": "https://www.youtube.com/embed?v=tTXFD0R11aQ&feature=youtu.be",
                            "step": "1. Stand up straight with a dumbbell in each hand at arm's length.\n2. Raise one dumbbell and twist your forearm until it is vertical and your palm faces the shoulder.\n3. Lower to original position and repeat with opposite arm\n",
                            "step_vi": "1. Đứng thẳng với một quả tạ ở mỗi tay dài bằng sải tay.\n2. Nâng một quả tạ lên và vặn cẳng tay cho đến khi nó thẳng đứng và lòng bàn tay hướng vào vai.\n3. Hạ xuống vị trí ban đầu và lặp lại với cánh tay đối diện\n",
                            "GroupMuscle": {
                                "name": "Biceps",
                                "name_vi": "Bắp tay"
                            },
                            "Equipment": {
                                "name": "Dumbbells",
                                "name_vi": "Tạ đơn",
                                "icon": "\n<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 62 61\" fill=\"none\" >\n    <path stroke=\"currentColor\" stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-width=\"2\" d=\"M52.063 33.672c5.176-5.176 3.933-14.812-2.777-21.522-6.71-6.71-16.346-7.954-21.523-2.777-5.177 5.176-3.933 14.812 2.777 21.523 6.71 6.71 16.346 7.953 21.523 2.776Z\"></path>\n    <path stroke=\"currentColor\" stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-width=\"2\" d=\"M25.858 11.983a10.49 10.49 0 0 0-2.613 1.903c-5.18 5.18-3.93 14.81 2.78 21.522 6.711 6.71 16.341 7.953 21.518 2.776a10.422 10.422 0 0 0 1.904-2.613\"></path>\n    <path stroke=\"currentColor\" stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-width=\"2\" d=\"M20.337 28.597c-4.296-1.278-8.618-.596-11.448 2.234-4.623 4.623-3.512 13.234 2.486 19.23 5.997 5.998 14.604 7.106 19.227 2.483 2.827-2.826 3.512-7.151 2.238-11.444\"></path>\n    <path stroke=\"currentColor\" stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-width=\"2\" d=\"M7.188 33.167a9.231 9.231 0 0 0-2.333 1.701C.228 39.495 1.343 48.102 7.341 54.099c5.997 5.998 14.6 7.109 19.227 2.482a9.453 9.453 0 0 0 1.701-2.333M42.75 24.36c1.21-1.21.92-3.46-.648-5.027-1.566-1.567-3.817-1.857-5.026-.647-1.21 1.209-.92 3.46.648 5.026 1.567 1.567 3.817 1.857 5.026.648Z\"></path>\n    <path stroke=\"currentColor\" stroke-miterlimit=\"10\" stroke-width=\"2\" d=\"M23.444 32.3 18.846 36.9a4.02 4.02 0 1 0 5.685 5.685l4.598-4.598\"></path>\n</svg>"
                            },
                            "Difficulty": {
                                "name": "Novice",
                                "name_vi": "Người mới"
                            }
                        }
                    },
                    {
                        "sets": 2,
                        "reps": "15-20 rep",
                        "rest": 45,
                        "notes": "Lighter than Day 1",
                        "notes_vi": "Nhẹ hơn ngày 1",
                        "Exercise": {
                            "name": "Dumbbell Overhead Tricep Extension",
                            "name_vi": "Mở rộng cơ tam đầu trên tạ",
                            "video_male": "https://media.musclewiki.com/media/uploads/videos/branded/male-Dumbbells-dumbbell-overhead-tricep-extension-side.mp4#t=0.1, https://media.musclewiki.com/media/uploads/videos/branded/male-Dumbbells-dumbbell-overhead-tricep-extension-front.mp4#t=0.1",
                            "video_female": "https://media.musclewiki.com/media/uploads/videos/branded/female-Dumbbells-dumbbell-overhead-tricep-extension-side.mp4#t=0.1, https://media.musclewiki.com/media/uploads/videos/branded/female-Dumbbells-dumbbell-overhead-tricep-extension-front.mp4#t=0.1",
                            "description": "",
                            "description_vi": "",
                            "link_description": "",
                            "step": "1. Hold a dumbbell overhead.\n2. Flex at the elbows until the dumbbell is behind your head.\n3. Then extend your elbows until the dumbbell is back in the starting position.\n",
                            "step_vi": "1. Giữ một quả tạ trên đầu.\n2. Co duỗi khuỷu tay cho đến khi quả tạ ở phía sau đầu.\n3. Sau đó mở rộng khuỷu tay của bạn cho đến khi quả tạ trở lại vị trí ban đầu.\n",
                            "GroupMuscle": {
                                "name": "Triceps",
                                "name_vi": "Tay sau"
                            },
                            "Equipment": {
                                "name": "Dumbbells",
                                "name_vi": "Tạ đơn",
                                "icon": "\n<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 62 61\" fill=\"none\" >\n    <path stroke=\"currentColor\" stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-width=\"2\" d=\"M52.063 33.672c5.176-5.176 3.933-14.812-2.777-21.522-6.71-6.71-16.346-7.954-21.523-2.777-5.177 5.176-3.933 14.812 2.777 21.523 6.71 6.71 16.346 7.953 21.523 2.776Z\"></path>\n    <path stroke=\"currentColor\" stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-width=\"2\" d=\"M25.858 11.983a10.49 10.49 0 0 0-2.613 1.903c-5.18 5.18-3.93 14.81 2.78 21.522 6.711 6.71 16.341 7.953 21.518 2.776a10.422 10.422 0 0 0 1.904-2.613\"></path>\n    <path stroke=\"currentColor\" stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-width=\"2\" d=\"M20.337 28.597c-4.296-1.278-8.618-.596-11.448 2.234-4.623 4.623-3.512 13.234 2.486 19.23 5.997 5.998 14.604 7.106 19.227 2.483 2.827-2.826 3.512-7.151 2.238-11.444\"></path>\n    <path stroke=\"currentColor\" stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-width=\"2\" d=\"M7.188 33.167a9.231 9.231 0 0 0-2.333 1.701C.228 39.495 1.343 48.102 7.341 54.099c5.997 5.998 14.6 7.109 19.227 2.482a9.453 9.453 0 0 0 1.701-2.333M42.75 24.36c1.21-1.21.92-3.46-.648-5.027-1.566-1.567-3.817-1.857-5.026-.647-1.21 1.209-.92 3.46.648 5.026 1.567 1.567 3.817 1.857 5.026.648Z\"></path>\n    <path stroke=\"currentColor\" stroke-miterlimit=\"10\" stroke-width=\"2\" d=\"M23.444 32.3 18.846 36.9a4.02 4.02 0 1 0 5.685 5.685l4.598-4.598\"></path>\n</svg>"
                            },
                            "Difficulty": {
                                "name": "Beginner",
                                "name_vi": "Tập sự"
                            }
                        }
                    }
                ]
            },
            {
                "day_of_week": "Day 5",
                "day_of_week_vi": "Ngày 5",
                "WorkoutExercises": [
                    {
                        "sets": 3,
                        "reps": "10-12 per leg",
                        "rest": 60,
                        "notes": "Balance and control",
                        "notes_vi": "Cân bằng và kiểm soát",
                        "Exercise": {
                            "name": "Walking Lunge",
                            "name_vi": "Đi bộ lunge",
                            "video_male": "https://media.musclewiki.com/media/uploads/videos/branded/male-Recovery-lunge-walking-front.mp4#t=0.1, https://media.musclewiki.com/media/uploads/videos/branded/male-Recovery-lunge-walking-side.mp4#t=0.1",
                            "video_female": "https://media.musclewiki.com/media/uploads/videos/branded/female-Recovery-lunge-walking-front.mp4#t=0.1, https://media.musclewiki.com/media/uploads/videos/branded/female-Recovery-lunge-walking-side.mp4#t=0.1",
                            "description": "",
                            "description_vi": "",
                            "link_description": "",
                            "step": "1. Take a step forward shifting your weight onto the front leg.\n2. Bend the knee of the front leg so the knee of the back leg comes close to the ground.\n3. Stand up and go into lunging with the opposite leg.\n",
                            "step_vi": "1. Bước một bước về phía trước, chuyển trọng lượng của bạn lên chân trước.\n2. Cong đầu gối của chân trước sao cho đầu gối của chân sau sát mặt đất.\n3. Đứng dậy và lao vào tấn công bằng chân đối diện.\n",
                            "GroupMuscle": {
                                "name": "Glutes",
                                "name_vi": "Cơ mông"
                            },
                            "Equipment": {
                                "name": "Bodyweight",
                                "name_vi": "Trọng lượng cơ thể",
                                "icon": "\n<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 63.14 155\" >\n    <defs>\n        <style>.bodyw__cls-1{fill:none;stroke:currentcolor;stroke-linecap:round;stroke-linejoin:round;stroke-width:6}</style>\n    </defs>\n    <g>\n        <path d=\"M31.57 2.5c5.23 0 7.63 4.24 7.63 9.47 0 2.31 5.13 12.36-7.63 12.36M31.57 2.5c-5.23 0-7.63 4.24-7.63 9.47 0 2.31-5.13 12.36 7.63 12.36M60.64 79.73c0 27.25-5.6-30.07-29.07-30.07S2.5 106.98 2.5 79.73s13.01-49.34 29.07-49.34 29.07 22.09 29.07 49.34Z\" class=\"bodyw__cls-1\"></path>\n        <path d=\"M52.22 140.27c0 45.35-20.65-50.05-20.65-50.05s-20.65 95.4-20.65 50.05 9.24-82.11 20.65-82.11 20.65 36.76 20.65 82.11Z\" class=\"bodyw__cls-1\"></path>\n    </g>\n</svg>"
                            },
                            "Difficulty": {
                                "name": "Intermediate",
                                "name_vi": "Trung cấp"
                            }
                        }
                    },
                    {
                        "sets": 3,
                        "reps": "20-25",
                        "rest": 45,
                        "notes": "Full ROM",
                        "notes_vi": "ROM đầy đủ",
                        "Exercise": {
                            "name": "Calf Raises",
                            "name_vi": "Nuôi bê",
                            "video_male": "https://media.musclewiki.com/media/uploads/videos/branded/male-Bodyweight-calf-raises-front.mp4#t=0.1, https://media.musclewiki.com/media/uploads/videos/branded/male-Bodyweight-calf-raises-side.mp4#t=0.1",
                            "video_female": "https://media.musclewiki.com/media/uploads/videos/branded/female-Bodyweight-calf-raises-front.mp4#t=0.1, https://media.musclewiki.com/media/uploads/videos/branded/female-Bodyweight-calf-raises-side.mp4#t=0.1",
                            "description": "Here are a few tips to help you get the most out of this exercise:",
                            "description_vi": "Dưới đây là một số mẹo giúp bạn tận dụng tối đa bài tập này:",
                            "link_description": "",
                            "step": "1. Balance on the balls of your feet on the platform or plates, leaning forward to use the wall to assist with balance.\n2. Lower the heels of your feet towards the ground and pause, then push through the balls of your feet like you are standing tip toe, pausing at the apex of the motion.\n3. Repeat as necessary.\n",
                            "step_vi": "1. Giữ thăng bằng trên đầu bàn chân trên bục hoặc đĩa, nghiêng người về phía trước để dựa vào tường để hỗ trợ giữ thăng bằng.\n2. Hạ gót chân xuống đất và tạm dừng, sau đó đẩy phần bóng của bàn chân giống như bạn đang đứng nhón chân, dừng lại ở đỉnh của chuyển động.\n3. Lặp lại nếu cần thiết.\n",
                            "GroupMuscle": {
                                "name": "Calves",
                                "name_vi": "Bắp chân"
                            },
                            "Equipment": {
                                "name": "Bodyweight",
                                "name_vi": "Trọng lượng cơ thể",
                                "icon": "\n<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 63.14 155\" >\n    <defs>\n        <style>.bodyw__cls-1{fill:none;stroke:currentcolor;stroke-linecap:round;stroke-linejoin:round;stroke-width:6}</style>\n    </defs>\n    <g>\n        <path d=\"M31.57 2.5c5.23 0 7.63 4.24 7.63 9.47 0 2.31 5.13 12.36-7.63 12.36M31.57 2.5c-5.23 0-7.63 4.24-7.63 9.47 0 2.31-5.13 12.36 7.63 12.36M60.64 79.73c0 27.25-5.6-30.07-29.07-30.07S2.5 106.98 2.5 79.73s13.01-49.34 29.07-49.34 29.07 22.09 29.07 49.34Z\" class=\"bodyw__cls-1\"></path>\n        <path d=\"M52.22 140.27c0 45.35-20.65-50.05-20.65-50.05s-20.65 95.4-20.65 50.05 9.24-82.11 20.65-82.11 20.65 36.76 20.65 82.11Z\" class=\"bodyw__cls-1\"></path>\n    </g>\n</svg>"
                            },
                            "Difficulty": {
                                "name": "Novice",
                                "name_vi": "Người mới"
                            }
                        }
                    },
                    {
                        "sets": 3,
                        "reps": "15-20 rep",
                        "rest": 60,
                        "notes": "Squeeze glutes",
                        "notes_vi": "Siết cơ mông",
                        "Exercise": {
                            "name": "Glute Bridge",
                            "name_vi": "Cầu mông",
                            "video_male": "https://media.musclewiki.com/media/uploads/videos/branded/male-Bodyweight-glute-bridge-side.mp4#t=0.1, https://media.musclewiki.com/media/uploads/videos/branded/male-Bodyweight-glute-bridge-front.mp4#t=0.1",
                            "video_female": "https://media.musclewiki.com/media/uploads/videos/branded/female-Bodyweight-glute-bridge-side.mp4#t=0.1, https://media.musclewiki.com/media/uploads/videos/branded/female-Bodyweight-glute-bridge-front.mp4#t=0.1",
                            "description": "",
                            "description_vi": "",
                            "link_description": "",
                            "step": "1. Lie down with your knees bent and your feet flat on the floor.\n2. Push your hips up so that your butt is elevated and your back straight.\n3. Tense your glutes and raise your hips towards the ceiling.\n4. Once you are at the highest point you can manage, hold the position for a few seconds, and then slowly return to the starting position\n",
                            "step_vi": "1. Nằm xuống, gập đầu gối và đặt bàn chân phẳng trên sàn.\n2. Đẩy hông lên sao cho mông nâng cao và lưng thẳng.\n3. Căng cơ mông và nâng hông về phía trần nhà.\n4. Khi đã lên đến điểm cao nhất mà bạn có thể xoay sở được, hãy giữ nguyên tư thế trong vài giây rồi từ từ quay trở lại vị trí ban đầu\n",
                            "GroupMuscle": {
                                "name": "Glutes",
                                "name_vi": "Cơ mông"
                            },
                            "Equipment": {
                                "name": "Bodyweight",
                                "name_vi": "Trọng lượng cơ thể",
                                "icon": "\n<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 63.14 155\" >\n    <defs>\n        <style>.bodyw__cls-1{fill:none;stroke:currentcolor;stroke-linecap:round;stroke-linejoin:round;stroke-width:6}</style>\n    </defs>\n    <g>\n        <path d=\"M31.57 2.5c5.23 0 7.63 4.24 7.63 9.47 0 2.31 5.13 12.36-7.63 12.36M31.57 2.5c-5.23 0-7.63 4.24-7.63 9.47 0 2.31-5.13 12.36 7.63 12.36M60.64 79.73c0 27.25-5.6-30.07-29.07-30.07S2.5 106.98 2.5 79.73s13.01-49.34 29.07-49.34 29.07 22.09 29.07 49.34Z\" class=\"bodyw__cls-1\"></path>\n        <path d=\"M52.22 140.27c0 45.35-20.65-50.05-20.65-50.05s-20.65 95.4-20.65 50.05 9.24-82.11 20.65-82.11 20.65 36.76 20.65 82.11Z\" class=\"bodyw__cls-1\"></path>\n    </g>\n</svg>"
                            },
                            "Difficulty": {
                                "name": "Novice",
                                "name_vi": "Người mới"
                            }
                        }
                    },
                    {
                        "sets": 3,
                        "reps": "15-20 rep",
                        "rest": 45,
                        "notes": "Squeeze hamstrings",
                        "notes_vi": "Siết chặt gân kheo",
                        "Exercise": {
                            "name": "Machine Seated Leg Curl",
                            "name_vi": "Máy cuộn chân ngồi",
                            "video_male": "https://media.musclewiki.com/media/uploads/videos/branded/male-Machine-machine-seated-leg-curl-front.mp4#t=0.1, https://media.musclewiki.com/media/uploads/videos/branded/male-Machine-machine-seated-leg-curl-side.mp4#t=0.1",
                            "video_female": "https://media.musclewiki.com/media/uploads/videos/branded/female-Machine-machine-seated-leg-curl-front.mp4#t=0.1, https://media.musclewiki.com/media/uploads/videos/branded/female-Machine-machine-seated-leg-curl-side.mp4#t=0.1",
                            "description": "",
                            "description_vi": "",
                            "link_description": "",
                            "step": "1. Sit back in the seat. Use the two handles to push yourself back into the chair.\n2. Flex your ankles and point your toes upward.\n3. Flex your knee bringing the pad backward, extend your knee without allowing the weight to touch back down.\n",
                            "step_vi": "1. Ngồi lại vào ghế. Sử dụng hai tay cầm để đẩy mình trở lại ghế.\n2. Co duỗi mắt cá chân và hướng ngón chân lên trên.\n3. Co duỗi đầu gối để đưa miếng đệm về phía sau, duỗi đầu gối mà không để trọng lượng chạm trở lại.\n",
                            "GroupMuscle": {
                                "name": "Hamstrings",
                                "name_vi": "Đùi sau"
                            },
                            "Equipment": {
                                "name": "Machine",
                                "name_vi": "Máy móc",
                                "icon": "\n<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 67 40\" fill=\"none\" >\n    <g stroke=\"currentColor\" stroke-linecap=\"round\" stroke-linejoin=\"round\" clip-path=\"url(#a)\">\n        <path stroke-width=\"1.757\" d=\"M25.435 17.064c.23-1.459.36-3.086.36-4.8 0-6.29-1.73-11.382-3.862-11.382M13.548 13.477c.207 5.715 1.844 10.171 3.838 10.171 2.131 0 3.86-5.099 3.86-11.383 0-6.284-1.729-11.386-3.86-11.386-1.994 0-3.635 4.453-3.838 10.167M62.33.879c2.132 0 3.86 5.096 3.86 11.383 0 6.287-1.728 11.38-3.86 11.38M53.942 13.477c.206 5.715 1.843 10.168 3.838 10.168 2.131 0 3.86-5.096 3.86-11.38C61.64 5.98 59.91.882 57.78.882c-1.995 0-3.635 4.453-3.838 10.167M17.386.879h4.547M17.386 23.645h4.547M57.78.879h4.55M57.78 23.645h4.55\"></path>\n        <path stroke-width=\"1.757\" d=\"M25.795 11.046h30.773c.67 0 1.215.546 1.215 1.216 0 .67-.545 1.215-1.215 1.215H25.795v-2.43ZM11.56 13.477h4.61a1.216 1.216 0 1 0 0-2.43h-4.61a1.216 1.216 0 1 0 0 2.43Z\"></path>\n        <path stroke-width=\"1.757\" d=\"M11.56 13.477h.118a1.216 1.216 0 1 0 0-2.43h-.118a1.216 1.216 0 0 0 0 2.43ZM66.165 11.046h2.328c.337 0 .64.137.861.358.222.221.358.524.358.86 0 .67-.546 1.216-1.216 1.216h-2.328M55.81 30.7c0 1.27-3.032 2.297-6.776 2.297-3.743 0-6.772-1.028-6.772-2.298\"></path>\n        <path stroke-width=\"1.757\" d=\"M48.313 26.328c-3.401.121-6.054 1.097-6.054 2.285 0 1.268 3.035 2.298 6.776 2.298 3.74 0 6.775-1.027 6.775-2.298 0-1.188-2.65-2.161-6.05-2.285\"></path>\n        <path stroke-width=\"1.054\" d=\"M48.868 28.086c-.791.027-1.407.255-1.407.53 0 .295.706.534 1.577.534.87 0 1.576-.24 1.576-.534 0-.275-.615-.503-1.407-.53\"></path>\n        <path stroke-width=\"1.757\" d=\"M55.81 28.61v2.09M42.262 28.61v2.09M44.7 24.394c0 2.134-5.096 3.862-11.384 3.862-6.287 0-11.38-1.728-11.38-3.862M32.1 16.009c-5.713.206-10.17 1.843-10.17 3.837 0 2.132 5.1 3.86 11.383 3.86 6.285 0 11.384-1.728 11.384-3.86 0-1.994-4.454-3.634-10.168-3.837\"></path>\n        <path stroke-width=\"1.757\" d=\"M33.035 18.961c-1.328.049-2.365.428-2.365.892 0 .494 1.185.897 2.647.897 1.46 0 2.646-.403 2.646-.898 0-.463-1.034-.845-2.364-.89M44.7 19.846v4.548M21.933 19.846v4.548M21.936 29.138c0 2.131 5.096 3.862 11.38 3.862 3.814 0 7.188-.637 9.252-1.616M44.7 26.843v-2.252M21.933 24.59v4.548\"></path>\n    </g>\n    <defs>\n        <clipPath id=\"a\">\n            <path fill=\"#fff\" d=\"M0 0h70.591v39H0z\"></path>\n        </clipPath>\n    </defs>\n</svg>"
                            },
                            "Difficulty": {
                                "name": "Novice",
                                "name_vi": "Người mới"
                            }
                        }
                    },
                    {
                        "sets": 3,
                        "reps": "15-20 rep",
                        "rest": 45,
                        "notes": "Controlled movements",
                        "notes_vi": "Chuyển động có kiểm soát",
                        "Exercise": {
                            "name": "Machine Leg Extension",
                            "name_vi": "Mở rộng chân máy",
                            "video_male": "https://media.musclewiki.com/media/uploads/videos/branded/male-machine-leg-extension-front.mp4#t=0.1, https://media.musclewiki.com/media/uploads/videos/branded/male-machine-leg-extension-side.mp4#t=0.1",
                            "video_female": "https://media.musclewiki.com/media/uploads/videos/branded/female-machine-leg-extension-front.mp4#t=0.1, https://media.musclewiki.com/media/uploads/videos/branded/female-machine-leg-extension-side.mp4#t=0.1",
                            "description": "",
                            "description_vi": "",
                            "link_description": "",
                            "step": "1. Sit on the machine with your back against the cushion and adjust the machine you are using so that your knees are at a 90 degree angle at the starting position.\n2. Raise the weight by extending your knees outward, then lower your leg to the starting position. Both movements should be done in a slow, controlled motion.\n",
                            "step_vi": "1. Ngồi trên máy, lưng dựa vào đệm và điều chỉnh máy bạn đang sử dụng sao cho đầu gối của bạn tạo thành một góc 90 độ ở vị trí ban đầu.\n2. Nâng tạ lên bằng cách duỗi đầu gối ra ngoài, sau đó hạ chân xuống vị trí ban đầu. Cả hai chuyển động nên được thực hiện một cách chậm rãi và có kiểm soát.\n",
                            "GroupMuscle": {
                                "name": "Quads",
                                "name_vi": "đùi trong"
                            },
                            "Equipment": {
                                "name": "Machine",
                                "name_vi": "Máy móc",
                                "icon": "\n<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 67 40\" fill=\"none\" >\n    <g stroke=\"currentColor\" stroke-linecap=\"round\" stroke-linejoin=\"round\" clip-path=\"url(#a)\">\n        <path stroke-width=\"1.757\" d=\"M25.435 17.064c.23-1.459.36-3.086.36-4.8 0-6.29-1.73-11.382-3.862-11.382M13.548 13.477c.207 5.715 1.844 10.171 3.838 10.171 2.131 0 3.86-5.099 3.86-11.383 0-6.284-1.729-11.386-3.86-11.386-1.994 0-3.635 4.453-3.838 10.167M62.33.879c2.132 0 3.86 5.096 3.86 11.383 0 6.287-1.728 11.38-3.86 11.38M53.942 13.477c.206 5.715 1.843 10.168 3.838 10.168 2.131 0 3.86-5.096 3.86-11.38C61.64 5.98 59.91.882 57.78.882c-1.995 0-3.635 4.453-3.838 10.167M17.386.879h4.547M17.386 23.645h4.547M57.78.879h4.55M57.78 23.645h4.55\"></path>\n        <path stroke-width=\"1.757\" d=\"M25.795 11.046h30.773c.67 0 1.215.546 1.215 1.216 0 .67-.545 1.215-1.215 1.215H25.795v-2.43ZM11.56 13.477h4.61a1.216 1.216 0 1 0 0-2.43h-4.61a1.216 1.216 0 1 0 0 2.43Z\"></path>\n        <path stroke-width=\"1.757\" d=\"M11.56 13.477h.118a1.216 1.216 0 1 0 0-2.43h-.118a1.216 1.216 0 0 0 0 2.43ZM66.165 11.046h2.328c.337 0 .64.137.861.358.222.221.358.524.358.86 0 .67-.546 1.216-1.216 1.216h-2.328M55.81 30.7c0 1.27-3.032 2.297-6.776 2.297-3.743 0-6.772-1.028-6.772-2.298\"></path>\n        <path stroke-width=\"1.757\" d=\"M48.313 26.328c-3.401.121-6.054 1.097-6.054 2.285 0 1.268 3.035 2.298 6.776 2.298 3.74 0 6.775-1.027 6.775-2.298 0-1.188-2.65-2.161-6.05-2.285\"></path>\n        <path stroke-width=\"1.054\" d=\"M48.868 28.086c-.791.027-1.407.255-1.407.53 0 .295.706.534 1.577.534.87 0 1.576-.24 1.576-.534 0-.275-.615-.503-1.407-.53\"></path>\n        <path stroke-width=\"1.757\" d=\"M55.81 28.61v2.09M42.262 28.61v2.09M44.7 24.394c0 2.134-5.096 3.862-11.384 3.862-6.287 0-11.38-1.728-11.38-3.862M32.1 16.009c-5.713.206-10.17 1.843-10.17 3.837 0 2.132 5.1 3.86 11.383 3.86 6.285 0 11.384-1.728 11.384-3.86 0-1.994-4.454-3.634-10.168-3.837\"></path>\n        <path stroke-width=\"1.757\" d=\"M33.035 18.961c-1.328.049-2.365.428-2.365.892 0 .494 1.185.897 2.647.897 1.46 0 2.646-.403 2.646-.898 0-.463-1.034-.845-2.364-.89M44.7 19.846v4.548M21.933 19.846v4.548M21.936 29.138c0 2.131 5.096 3.862 11.38 3.862 3.814 0 7.188-.637 9.252-1.616M44.7 26.843v-2.252M21.933 24.59v4.548\"></path>\n    </g>\n    <defs>\n        <clipPath id=\"a\">\n            <path fill=\"#fff\" d=\"M0 0h70.591v39H0z\"></path>\n        </clipPath>\n    </defs>\n</svg>"
                            },
                            "Difficulty": {
                                "name": "Novice",
                                "name_vi": "Người mới"
                            }
                        }
                    }
                ]
            },
            {
                "day_of_week": "Day 6",
                "day_of_week_vi": "Ngày 6",
                "WorkoutExercises": [
                    {
                        "sets": "null",
                        "reps": "",
                        "rest": "null",
                        "notes": "Rest",
                        "notes_vi": "Nghỉ ngơi",
                        "Exercise": {
                            "name": "Rest",
                            "name_vi": "Nghỉ ngơi",
                            "video_male": "https://media.istockphoto.com/id/1288434083/vi/video/ng%C6%B0%E1%BB%9Di-ph%E1%BB%A5-n%E1%BB%AF-ch%C3%A2u-%C3%A1-th%C6%B0-gi%C3%A3n-t%E1%BA%A1i-sofa.mp4?s=mp4-640x640-is&k=20&c=uHl0HeisH8OXiX7f5WGh6eVy1Y2_0wSWmdfsAksZ-Pg=, https://media.istockphoto.com/id/1288434083/vi/video/ng%C6%B0%E1%BB%9Di-ph%E1%BB%A5-n%E1%BB%AF-ch%C3%A2u-%C3%A1-th%C6%B0-gi%C3%A3n-t%E1%BA%A1i-sofa.mp4?s=mp4-640x640-is&k=20&c=uHl0HeisH8OXiX7f5WGh6eVy1Y2_0wSWmdfsAksZ-Pg=",
                            "video_female": "https://media.istockphoto.com/id/1288434083/vi/video/ng%C6%B0%E1%BB%9Di-ph%E1%BB%A5-n%E1%BB%AF-ch%C3%A2u-%C3%A1-th%C6%B0-gi%C3%A3n-t%E1%BA%A1i-sofa.mp4?s=mp4-640x640-is&k=20&c=uHl0HeisH8OXiX7f5WGh6eVy1Y2_0wSWmdfsAksZ-Pg=, https://media.istockphoto.com/id/1288434083/vi/video/ng%C6%B0%E1%BB%9Di-ph%E1%BB%A5-n%E1%BB%AF-ch%C3%A2u-%C3%A1-th%C6%B0-gi%C3%A3n-t%E1%BA%A1i-sofa.mp4?s=mp4-640x640-is&k=20&c=uHl0HeisH8OXiX7f5WGh6eVy1Y2_0wSWmdfsAksZ-Pg=",
                            "description": "null",
                            "description_vi": "null",
                            "link_description": "null",
                            "step": "null",
                            "step_vi": "null",
                            "GroupMuscle": {
                                "name": "Biceps",
                                "name_vi": "Bắp tay"
                            },
                            "Equipment": {
                                "name": "Barbell",
                                "name_vi": "Thanh tạ",
                                "icon": "\n<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 67 40\" fill=\"none\">\n    <g stroke=\"currentColor\" stroke-linecap=\"round\" stroke-linejoin=\"round\" clip-path=\"url(#a)\">\n        <path stroke-width=\"1.757\" d=\"M25.435 17.064c.23-1.459.36-3.086.36-4.8 0-6.29-1.73-11.382-3.862-11.382M13.548 13.477c.207 5.715 1.844 10.171 3.838 10.171 2.131 0 3.86-5.099 3.86-11.383 0-6.284-1.729-11.386-3.86-11.386-1.994 0-3.635 4.453-3.838 10.167M62.33.879c2.132 0 3.86 5.096 3.86 11.383 0 6.287-1.728 11.38-3.86 11.38M53.942 13.477c.206 5.715 1.843 10.168 3.838 10.168 2.131 0 3.86-5.096 3.86-11.38C61.64 5.98 59.91.882 57.78.882c-1.995 0-3.635 4.453-3.838 10.167M17.386.879h4.547M17.386 23.645h4.547M57.78.879h4.55M57.78 23.645h4.55\"></path>\n        <path stroke-width=\"1.757\" d=\"M25.795 11.046h30.773c.67 0 1.215.546 1.215 1.216 0 .67-.545 1.215-1.215 1.215H25.795v-2.43ZM11.56 13.477h4.61a1.216 1.216 0 1 0 0-2.43h-4.61a1.216 1.216 0 1 0 0 2.43Z\"></path>\n        <path stroke-width=\"1.757\" d=\"M11.56 13.477h.118a1.216 1.216 0 1 0 0-2.43h-.118a1.216 1.216 0 0 0 0 2.43ZM66.165 11.046h2.328c.337 0 .64.137.861.358.222.221.358.524.358.86 0 .67-.546 1.216-1.216 1.216h-2.328M55.81 30.7c0 1.27-3.032 2.297-6.776 2.297-3.743 0-6.772-1.028-6.772-2.298\"></path>\n        <path stroke-width=\"1.757\" d=\"M48.313 26.328c-3.401.121-6.054 1.097-6.054 2.285 0 1.268 3.035 2.298 6.776 2.298 3.74 0 6.775-1.027 6.775-2.298 0-1.188-2.65-2.161-6.05-2.285\"></path>\n        <path stroke-width=\"1.054\" d=\"M48.868 28.086c-.791.027-1.407.255-1.407.53 0 .295.706.534 1.577.534.87 0 1.576-.24 1.576-.534 0-.275-.615-.503-1.407-.53\"></path>\n        <path stroke-width=\"1.757\" d=\"M55.81 28.61v2.09M42.262 28.61v2.09M44.7 24.394c0 2.134-5.096 3.862-11.384 3.862-6.287 0-11.38-1.728-11.38-3.862M32.1 16.009c-5.713.206-10.17 1.843-10.17 3.837 0 2.132 5.1 3.86 11.383 3.86 6.285 0 11.384-1.728 11.384-3.86 0-1.994-4.454-3.634-10.168-3.837\"></path>\n        <path stroke-width=\"1.757\" d=\"M33.035 18.961c-1.328.049-2.365.428-2.365.892 0 .494 1.185.897 2.647.897 1.46 0 2.646-.403 2.646-.898 0-.463-1.034-.845-2.364-.89M44.7 19.846v4.548M21.933 19.846v4.548M21.936 29.138c0 2.131 5.096 3.862 11.38 3.862 3.814 0 7.188-.637 9.252-1.616M44.7 26.843v-2.252M21.933 24.59v4.548\"></path>\n    </g>\n    <defs>\n        <clipPath id=\"a\">\n            <path fill=\"#fff\" d=\"M0 0h70.591v39H0z\"></path>\n        </clipPath>\n    </defs>\n</svg>"
                            },
                            "Difficulty": {
                                "name": "Beginner",
                                "name_vi": "Tập sự"
                            }
                        }
                    }
                ]
            },
            {
                "day_of_week": "Day 7",
                "day_of_week_vi": "Ngày 7",
                "WorkoutExercises": [
                    {
                        "sets": "null",
                        "reps": "",
                        "rest": "null",
                        "notes": "Rest",
                        "notes_vi": "Nghỉ ngơi",
                        "Exercise": {
                            "name": "Rest",
                            "name_vi": "Nghỉ ngơi",
                            "video_male": "https://media.istockphoto.com/id/1288434083/vi/video/ng%C6%B0%E1%BB%9Di-ph%E1%BB%A5-n%E1%BB%AF-ch%C3%A2u-%C3%A1-th%C6%B0-gi%C3%A3n-t%E1%BA%A1i-sofa.mp4?s=mp4-640x640-is&k=20&c=uHl0HeisH8OXiX7f5WGh6eVy1Y2_0wSWmdfsAksZ-Pg=, https://media.istockphoto.com/id/1288434083/vi/video/ng%C6%B0%E1%BB%9Di-ph%E1%BB%A5-n%E1%BB%AF-ch%C3%A2u-%C3%A1-th%C6%B0-gi%C3%A3n-t%E1%BA%A1i-sofa.mp4?s=mp4-640x640-is&k=20&c=uHl0HeisH8OXiX7f5WGh6eVy1Y2_0wSWmdfsAksZ-Pg=",
                            "video_female": "https://media.istockphoto.com/id/1288434083/vi/video/ng%C6%B0%E1%BB%9Di-ph%E1%BB%A5-n%E1%BB%AF-ch%C3%A2u-%C3%A1-th%C6%B0-gi%C3%A3n-t%E1%BA%A1i-sofa.mp4?s=mp4-640x640-is&k=20&c=uHl0HeisH8OXiX7f5WGh6eVy1Y2_0wSWmdfsAksZ-Pg=, https://media.istockphoto.com/id/1288434083/vi/video/ng%C6%B0%E1%BB%9Di-ph%E1%BB%A5-n%E1%BB%AF-ch%C3%A2u-%C3%A1-th%C6%B0-gi%C3%A3n-t%E1%BA%A1i-sofa.mp4?s=mp4-640x640-is&k=20&c=uHl0HeisH8OXiX7f5WGh6eVy1Y2_0wSWmdfsAksZ-Pg=",
                            "description": "null",
                            "description_vi": "null",
                            "link_description": "null",
                            "step": "null",
                            "step_vi": "null",
                            "GroupMuscle": {
                                "name": "Biceps",
                                "name_vi": "Bắp tay"
                            },
                            "Equipment": {
                                "name": "Barbell",
                                "name_vi": "Thanh tạ",
                                "icon": "\n<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 67 40\" fill=\"none\">\n    <g stroke=\"currentColor\" stroke-linecap=\"round\" stroke-linejoin=\"round\" clip-path=\"url(#a)\">\n        <path stroke-width=\"1.757\" d=\"M25.435 17.064c.23-1.459.36-3.086.36-4.8 0-6.29-1.73-11.382-3.862-11.382M13.548 13.477c.207 5.715 1.844 10.171 3.838 10.171 2.131 0 3.86-5.099 3.86-11.383 0-6.284-1.729-11.386-3.86-11.386-1.994 0-3.635 4.453-3.838 10.167M62.33.879c2.132 0 3.86 5.096 3.86 11.383 0 6.287-1.728 11.38-3.86 11.38M53.942 13.477c.206 5.715 1.843 10.168 3.838 10.168 2.131 0 3.86-5.096 3.86-11.38C61.64 5.98 59.91.882 57.78.882c-1.995 0-3.635 4.453-3.838 10.167M17.386.879h4.547M17.386 23.645h4.547M57.78.879h4.55M57.78 23.645h4.55\"></path>\n        <path stroke-width=\"1.757\" d=\"M25.795 11.046h30.773c.67 0 1.215.546 1.215 1.216 0 .67-.545 1.215-1.215 1.215H25.795v-2.43ZM11.56 13.477h4.61a1.216 1.216 0 1 0 0-2.43h-4.61a1.216 1.216 0 1 0 0 2.43Z\"></path>\n        <path stroke-width=\"1.757\" d=\"M11.56 13.477h.118a1.216 1.216 0 1 0 0-2.43h-.118a1.216 1.216 0 0 0 0 2.43ZM66.165 11.046h2.328c.337 0 .64.137.861.358.222.221.358.524.358.86 0 .67-.546 1.216-1.216 1.216h-2.328M55.81 30.7c0 1.27-3.032 2.297-6.776 2.297-3.743 0-6.772-1.028-6.772-2.298\"></path>\n        <path stroke-width=\"1.757\" d=\"M48.313 26.328c-3.401.121-6.054 1.097-6.054 2.285 0 1.268 3.035 2.298 6.776 2.298 3.74 0 6.775-1.027 6.775-2.298 0-1.188-2.65-2.161-6.05-2.285\"></path>\n        <path stroke-width=\"1.054\" d=\"M48.868 28.086c-.791.027-1.407.255-1.407.53 0 .295.706.534 1.577.534.87 0 1.576-.24 1.576-.534 0-.275-.615-.503-1.407-.53\"></path>\n        <path stroke-width=\"1.757\" d=\"M55.81 28.61v2.09M42.262 28.61v2.09M44.7 24.394c0 2.134-5.096 3.862-11.384 3.862-6.287 0-11.38-1.728-11.38-3.862M32.1 16.009c-5.713.206-10.17 1.843-10.17 3.837 0 2.132 5.1 3.86 11.383 3.86 6.285 0 11.384-1.728 11.384-3.86 0-1.994-4.454-3.634-10.168-3.837\"></path>\n        <path stroke-width=\"1.757\" d=\"M33.035 18.961c-1.328.049-2.365.428-2.365.892 0 .494 1.185.897 2.647.897 1.46 0 2.646-.403 2.646-.898 0-.463-1.034-.845-2.364-.89M44.7 19.846v4.548M21.933 19.846v4.548M21.936 29.138c0 2.131 5.096 3.862 11.38 3.862 3.814 0 7.188-.637 9.252-1.616M44.7 26.843v-2.252M21.933 24.59v4.548\"></path>\n    </g>\n    <defs>\n        <clipPath id=\"a\">\n            <path fill=\"#fff\" d=\"M0 0h70.591v39H0z\"></path>\n        </clipPath>\n    </defs>\n</svg>"
                            },
                            "Difficulty": {
                                "name": "Beginner",
                                "name_vi": "Tập sự"
                            }
                        }
                    }
                ]
            }
        ],
        "ImportantConsiderations": [
            {
                "description": "Consistency is key",
                "description_vi": "Tính nhất quán là chìa khóa"
            },
            {
                "description": "Modifications as needed",
                "description_vi": "Sửa đổi khi cần thiết"
            },
            {
                "description": "Healthy diet",
                "description_vi": "Chế độ ăn uống lành mạnh"
            },
            {
                "description": "Gradual progression",
                "description_vi": "Tiến triển dần dần"
            },
            {
                "description": "Medical clearance essential",
                "description_vi": "Giấy chứng nhận y tế cần thiết"
            }
        ],
        "BmiLevel": {
            "description": "BMI Level 4",
            "description_vi": "Mức BMI 4"
        }
    }
}
