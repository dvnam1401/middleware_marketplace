from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('workout-form/', views.workout_form, name='workout_form'),
    path('workout-plan/', views.workout_plan, name='workout_plan'),
    path('workout-details/', views.workout_details, name='workout_details'),
    path('workout-start/', views.workout_start, name='workout_start'),
    path('save-workout-data/', views.save_workout_data, name='save_workout_data'),
]