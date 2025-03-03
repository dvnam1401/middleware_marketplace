from django.shortcuts import render, redirect
from django.http import JsonResponse
from .api_handlers import get_all_products, server1_handler, server2_handler
from decouple import config
from django.views.decorators.csrf import csrf_exempt
import requests
def home(request):
    products = get_all_products()
    return render(request, 'home.html', {'products': products})

def product_detail(request, product_id):
    products = get_all_products()
    product = next((p for p in products if str(p.get('product_id')) == str(product_id)), None)
    if product:
        # Thay thế __NEWLINE__ bằng <br> để hiển thị xuống dòng
        product['description'] = product['description'].replace('__NEWLINE__', '<br>')
    api_orders_url = config('API_ORDERS_URL')
    access_token = config('SERVER1_API_TOKEN')
    return render(request, 'product_detail.html', {'product': product, 'api_orders_url': api_orders_url, 'access_token': access_token})

def workout_plan(request):
    if request.method == 'POST':
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
        api_workout_url = config('API_WORKOUT_URL')
        workout_token = config('WORKOUT_TOKEN')
        headers = {'Authorization': f'Bearer {workout_token}'}
        response = requests.post(api_workout_url, json=data, headers=headers)

        if response.status_code == 200:
            workout_data = response.json()
            return render(request, 'workout_plan.html', {'workout_data': workout_data})
        else:
            return JsonResponse({'error': 'Failed to fetch workout plan'}, status=500)

    return render(request, 'workout_form.html')

# View để hiển thị form nhập liệu
def workout_form(request):
    return render(request, 'workout_form.html')

def workout_details(request):
    if 'workout_data' not in request.session:
        return redirect('workout_form')
    workout_data = request.session['workout_data']
    return render(request, 'workout_details.html', {'workout_data': workout_data})

def workout_start(request):
    if 'workout_data' not in request.session:
        return redirect('workout_form')
    workout_data = request.session['workout_data']
    day = request.GET.get('day', 'Day 1')
    selected_day = next((d for d in workout_data['DT']['WorkoutDays'] if d['day_of_week'] == day), None)
    return render(request, 'workout_start.html', {'day': selected_day})

