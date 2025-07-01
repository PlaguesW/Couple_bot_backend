import requests
import json
from datetime import datetime

# Базовый URL вашего API
BASE_URL = "http://127.0.0.1:8000"

def test_user_registration():
    """Тест регистрации пользователя"""
    print("=== Тестирование регистрации пользователя ===")
    url = f"{BASE_URL}/users/register"
    
    user_data = {
        "user_id": f"test_user_{int(datetime.now().timestamp())}",
        "telegram_id": 123456789,
        "name": "Test User",
        "username": "test_username"
    }
    
    try:
        response = requests.post(url, json=user_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Регистрация пользователя успешна")
            return user_data["user_id"]
        else:
            print("❌ Ошибка при регистрации пользователя")
            return None
    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")
        return None

def test_get_user(user_id):
    """Тест получения пользователя по ID"""
    print(f"\n=== Тестирование получения пользователя {user_id} ===")
    url = f"{BASE_URL}/users/{user_id}"
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Получение пользователя успешно")
        else:
            print("❌ Ошибка при получении пользователя")
    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")

def test_get_all_users():
    """Тест получения всех пользователей"""
    print("\n=== Тестирование получения всех пользователей ===")
    url = f"{BASE_URL}/users/"
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Получение всех пользователей успешно")
        else:
            print("❌ Ошибка при получении пользователей")
    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")

def test_update_user(user_id):
    """Тест обновления пользователя"""
    print(f"\n=== Тестирование обновления пользователя {user_id} ===")
    url = f"{BASE_URL}/users/{user_id}"
    
    update_data = {
        "name": "Updated Test User",
        "username": "updated_username"
    }
    
    try:
        response = requests.put(url, json=update_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Обновление пользователя успешно")
        else:
            print("❌ Ошибка при обновлении пользователя")
    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")

def test_delete_user(user_id):
    """Тест удаления пользователя"""
    print(f"\n=== Тестирование удаления пользователя {user_id} ===")
    url = f"{BASE_URL}/users/{user_id}"
    
    try:
        response = requests.delete(url)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Удаление пользователя успешно")
        else:
            print("❌ Ошибка при удалении пользователя")
    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")

def test_health_check():
    """Тест health check endpoint"""
    print("\n=== Тестирование health check ===")
    url = f"{BASE_URL}/"
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Health check успешен")
        else:
            print("❌ Ошибка health check")
    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")

def test_docs():
    """Тест доступности документации"""
    print("\n=== Тестирование документации ===")
    url = f"{BASE_URL}/docs"
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Документация доступна")
            print(f"Документация: {BASE_URL}/docs")
        else:
            print("❌ Ошибка доступа к документации")
    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")

def run_all_tests():
    """Запуск всех тестов"""
    print("🚀 Начинаем тестирование API...")
    
    # Проверяем доступность сервера
    test_health_check()
    test_docs()
    
    # Тестируем пользователей
    user_id = test_user_registration()
    
    if user_id:
        test_get_user(user_id)
        test_get_all_users()
        test_update_user(user_id)
        test_get_user(user_id)  
        test_delete_user(user_id)
        test_get_user(user_id)  
    
    print("\n🎉 Тестирование завершено!")

if __name__ == "__main__":
    run_all_tests()