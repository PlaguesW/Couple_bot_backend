from database import engine, SessionLocal
from models import Base, User, Pair, Idea, DateProposal, ProposalStatus
from datetime import datetime, date, time

def init_database():
    """Создание таблиц базы данных"""
    print("Создание таблиц...")
    Base.metadata.create_all(bind=engine)
    print("✅ Таблицы созданы успешно!")

def add_sample_ideas():
    """Добавление примеров идей для свиданий"""
    db = SessionLocal()
    
    #* Check ideas
    if db.query(Idea).first():
        print("⚠️  Идеи уже существуют в базе данных")
        db.close()
        return
    
    sample_ideas = [
        #* Romantic
        {
            "title": "Романтический ужин при свечах",
            "description": "Приготовьте ужин вместе и устройте романтический вечер дома",
            "category": "romantic",
            "duration": "2-3 hours",
            "cost_level": "medium"
        },
        {
            "title": "Прогулка под звездами",
            "description": "Вечерняя прогулка в красивом месте с видом на звездное небо",
            "category": "romantic",
            "duration": "1-2 hours",
            "cost_level": "free"
        },
        {
            "title": "Пикник в парке",
            "description": "Приготовьте корзину с едой и проведите время на природе",
            "category": "romantic",
            "duration": "3-4 hours",
            "cost_level": "low"
        },
        
        #* Home
        {
            "title": "Киномарафон",
            "description": "Выберите любимые фильмы и проведите уютный вечер дома",
            "category": "home",
            "duration": "4+ hours",
            "cost_level": "free"
        },
        {
            "title": "Готовка нового блюда",
            "description": "Найдите новый рецепт и приготовьте что-то вкусное вместе",
            "category": "home",
            "duration": "1-2 hours",
            "cost_level": "low"
        },
        {
            "title": "Настольные игры",
            "description": "Устройте турнир по любимым настольным играм",
            "category": "home",
            "duration": "2-3 hours",
            "cost_level": "free"
        },
        
        #* Cultural
        {
            "title": "Посещение музея",
            "description": "Изучите новую выставку в местном музее",
            "category": "cultural",
            "duration": "2-3 hours",
            "cost_level": "medium"
        },
        {
            "title": "Театральное представление",
            "description": "Сходите на спектакль или мюзикл",
            "category": "cultural",
            "duration": "2-3 hours",
            "cost_level": "high"
        },
        {
            "title": "Мастер-класс",
            "description": "Запишитесь на совместный мастер-класс (рисование, танцы, кулинария)",
            "category": "cultural",
            "duration": "2-3 hours",
            "cost_level": "medium"
        },
        
        #* Active
        {
            "title": "Велопрогулка",
            "description": "Прокатитесь на велосипедах по живописным местам",
            "category": "active",
            "duration": "2-4 hours",
            "cost_level": "low"
        },
        {
            "title": "Боулинг",
            "description": "Устройте соревнование в боулинге",
            "category": "active",
            "duration": "1-2 hours",
            "cost_level": "medium"
        },
        {
            "title": "Пеший поход",
            "description": "Отправьтесь в небольшой поход по красивым тропам",
            "category": "active",
            "duration": "4+ hours",
            "cost_level": "free"
        },
        
        #* Cheap one
        {
            "title": "Посещение бесплатного мероприятия",
            "description": "Найдите бесплатные мероприятия в вашем городе",
            "category": "budget",
            "duration": "2-3 hours",
            "cost_level": "free"
        },
        {
            "title": "Фотосессия в городе",
            "description": "Устройте импровизированную фотосессию в интересных местах",
            "category": "budget",
            "duration": "2-3 hours",
            "cost_level": "free"
        },
        {
            "title": "Посещение местного рынка",
            "description": "Прогуляйтесь по рынку, попробуйте местные деликатесы",
            "category": "budget",
            "duration": "1-2 hours",
            "cost_level": "low"
        }
    ]
    
    print("Добавление примеров идей...")
    for idea_data in sample_ideas:
        idea = Idea(**idea_data)
        db.add(idea)
    
    db.commit()
    db.close()
    print(f"✅ Добавлено {len(sample_ideas)} идей для свиданий!")

def add_test_users():
    """Добавление тестовых пользователей"""
    db = SessionLocal()
    
    # Проверяем, есть ли уже пользователи
    if db.query(User).first():
        print("⚠️  Пользователи уже существуют в базе данных")
        db.close()
        return
    
    test_users = [
        {
            "telegram_id": 123456789,
            "username": "test_user1",
            "first_name": "Анна",
            "last_name": "Тестовая"
        },
        {
            "telegram_id": 987654321,
            "username": "test_user2",
            "first_name": "Петр",
            "last_name": "Тестовый"
        }
    ]
    
    print("Добавление тестовых пользователей...")
    for user_data in test_users:
        user = User(**user_data)
        db.add(user)
    
    db.commit()
    db.close()
    print(f"✅ Добавлено {len(test_users)} тестовых пользователей!")

def main():
    """Основная функция инициализации"""
    print("🚀 Инициализация базы данных Couple Bot...")
    
    #* Create tabels
    init_database()
    
    #* Add test ideas
    add_sample_ideas()
    add_test_users()
    
    print("\n✅ Инициализация завершена!")
    print("📝 Не забудьте:")
    print("   1. Настроить переменные окружения в .env")
    print("   2. Изменить API_TOKEN на безопасный")
    print("   3. Настроить правильные параметры базы данных")

if __name__ == "__main__":
    main()