from app.db.session import SessionLocal
from app.models import Category
from app.models import Dish


def seed_categories_and_dishes():
    db = SessionLocal()

    try:
        # =========================
        # 1. Seed Categories
        # =========================
        categories_data = [
            "Appetizer",
            "Main Course",
            "Dessert",
            "Drink",
        ]

        categories = {}
        for name in categories_data:
            category = db.query(Category).filter(Category.name == name).first()
            if not category:
                category = Category(name=name)
                db.add(category)
                db.flush()  # lấy id ngay
            categories[name] = category

        # =========================
        # 2. Seed Dishes
        # =========================
        dishes_data = [
            {
                "name": "Spring Rolls",
                "price": 5.5,
                "imgUrl": "https://example.com/spring_rolls.jpg",
                "describe": "Crispy spring rolls with vegetables",
                "status": 1,
                "category": "Appetizer",
            },
            {
                "name": "Grilled Chicken",
                "price": 12.9,
                "imgUrl": "https://example.com/grilled_chicken.jpg",
                "describe": "Grilled chicken with special sauce",
                "status": 1,
                "category": "Main Course",
            },
            {
                "name": "Chocolate Cake",
                "price": 6.0,
                "imgUrl": "https://example.com/chocolate_cake.jpg",
                "describe": "Rich chocolate cake",
                "status": 1,
                "category": "Dessert",
            },
            {
                "name": "Lemon Tea",
                "price": 3.0,
                "imgUrl": "https://example.com/lemon_tea.jpg",
                "describe": "Fresh lemon tea",
                "status": 1,
                "category": "Drink",
            },
        ]

        for item in dishes_data:
            exists = db.query(Dish).filter(Dish.name == item["name"]).first()
            if exists:
                continue

            dish = Dish(
                name=item["name"],
                price=item["price"],
                imgUrl=item["imgUrl"],
                describe=item["describe"],
                status=item["status"],
                category=categories[item["category"]],  # dùng relationship
            )

            db.add(dish)

        db.commit()
        print("✅ Seed categories & dishes successfully")

    except Exception as e:
        db.rollback()
        print("❌ Seed failed:", e)

    finally:
        db.close()


if __name__ == "__main__":
    seed_categories_and_dishes()
