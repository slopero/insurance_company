from django.shortcuts import render, redirect
import json
import bcrypt
from django.http import JsonResponse
from django.db import connection
from .models import User, Contract, Employee


def index(request):
    """Главная страница - редирект на логин если не авторизован"""
    if 'user_id' not in request.session:
        return redirect('login')
    return redirect('dashboard')


def login_view(request):
    """Страница входа"""
    if request.method == 'POST':
        data = json.loads(request.body)
        login = data.get('username')  
        password = data.get('password')
        
        try:
            user = User.objects.using('auth_db').get(login=login)
            # Проверка пароля с bcrypt
            if bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
                request.session['user_id'] = user.id
                request.session['login'] = user.login
                request.session['id_employee'] = user.id_employee_id  # сохраняем id сотрудника
                return JsonResponse({'status': 'success', 'message': 'Авторизация успешна'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Неверный пароль'}, status=401)
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Пользователь не найден'}, status=404)
    
    return render(request, 'login.html')


def logout_view(request):
    """Выход из системы"""
    request.session.flush()
    return redirect('login')


def register_view(request):
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        data = json.loads(request.body)
        login = data.get('username')
        password = data.get('password')
        ser_pass = data.get('ser_pass')  # серия паспорта
        num_pass = data.get('num_pass')  # номер паспорта
        
        # Проверка существования пользователя
        if User.objects.using('auth_db').filter(login=login).exists():
            return JsonResponse({'status': 'error', 'message': 'Пользователь с таким логином уже существует'}, status=400)
        
        # Поиск сотрудника по паспортным данным (используем auth_db - postgres)
        try:
            employee = Employee.objects.using('auth_db').get(ser_pass=ser_pass, num_pass=num_pass)
        except Employee.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Сотрудник с такими паспортными данными не найден'}, status=404)
        
        # Проверка, не зарегистрирован ли уже этот сотрудник
        if User.objects.using('auth_db').filter(id_employee=employee.id_employee).exists():
            return JsonResponse({'status': 'error', 'message': 'Для этого сотрудника уже создан аккаунт'}, status=400)
        
        # Хеширование пароля с bcrypt
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        user = User(
            login=login,
            password_hash=password_hash,
            id_employee_id=employee.id_employee
        )
        user.save(using='auth_db')
        
        return JsonResponse({
            'status': 'success',
            'message': f'Регистрация успешна. Добро пожаловать, {employee.name_employee}!',
            'user_id': user.id
        })
    
    return render(request, 'register.html')


def dashboard_view(request):
    """Личный кабинет пользователя"""
    if 'user_id' not in request.session:
        return redirect('login')
    
    return render(request, 'dashboard.html', {
        'username': request.session.get('login')
    })


def get_contracts(request):
    """Получение списка договоров для текущего сотрудника"""
    if 'user_id' not in request.session:
        return JsonResponse({'status': 'error', 'message': 'Не авторизован'}, status=401)
    
    id_employee = request.session.get('id_employee')
    
    # Устанавливаем параметр для RLS политики PostgreSQL
    with connection.cursor() as cursor:
        cursor.execute("SET app.current_id_employee = %s", [str(id_employee)])
    
    # Получаем договоры с данными клиента через select_related
    contracts = Contract.objects.filter(id_employee=id_employee).using('auth_db').select_related('id_client')
    
    # Форматируем данные с кастомными названиями колонок
    contracts_list = []
    for contract in contracts:
        client = contract.id_client
        # Формируем ФИО клиента
        client_fio = f"{client.surname_client} {client.name_client} {client.patronymic}"
        
        contracts_list.append({
            '№ договора': contract.id_contract,
            'Клиент': client_fio,
            'Дата начала': contract.date_start.strftime('%d.%m.%Y') if contract.date_start else None,
            'Дата окончания': contract.date_end.strftime('%d.%m.%Y') if contract.date_end else None,
            'Сумма страховки': contract.cost_insurance,
            'Вид страхования': contract.kind_insurance,
        })
    
    return JsonResponse({
        'status': 'success',
        'contracts': contracts_list
    })


def save_user(request):
    """Создание пользователя с хешированием bcrypt"""
    if request.method == 'POST':
        data = json.loads(request.body)
        password = data.get('password')
        
        # Хеширование пароля с bcrypt
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        user = User(username=data.get('username'), password_hash=password_hash)
        user.save(using='auth_db')

        return JsonResponse({
            'status': 'success', 
            'user_id': user.id
        })


def get_users(request):
    """Получение списка пользователей (только для авторизованных)"""
    if 'user_id' not in request.session:
        return JsonResponse({'status': 'error', 'message': 'Не авторизован'}, status=401)
    
    users = User.objects.using('auth_db').all().values("id", "username")
    return JsonResponse({
        'users': list(users)
    })


def get_user(request, user_id):
    """Получение информации о пользователе"""
    if 'user_id' not in request.session:
        return JsonResponse({'status': 'error', 'message': 'Не авторизован'}, status=401)
    
    try:
        user = User.objects.using('auth_db').get(id=user_id)
        return JsonResponse({
            'id': user.id,
            'username': user.username
        })
    except User.DoesNotExist:
        return JsonResponse({
            'error': 'User not found'
        }, status=404)
    

