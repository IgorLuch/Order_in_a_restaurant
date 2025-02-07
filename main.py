import json
from typing import List, Dict, Optional


class MenuItem:
    """Класс для представления элемента меню."""

    def __init__(self, name: str, price: float, category: str):
        self.name = name
        self.price = price
        self.category = category

    def __str__(self):
        return f"{self.name} ({self.category}) - {self.price} руб."


class Menu:
    """Класс для представления меню ресторана."""

    def __init__(self):
        self.items: List[MenuItem] = []

    def load_menu(self, filename: str) -> None:
        """Загружает меню из JSON-файла."""
        try:
            with open(filename, "r", encoding="utf-8") as file:
                menu_data = json.load(file)
                self.items = [
                    MenuItem(item["name"], item["price"], item["category"])
                    for item in menu_data
                ]
            print("Меню успешно загружено.")
        except FileNotFoundError:
            print("Файл меню не найден.")
        except json.JSONDecodeError:
            print("Ошибка чтения файла меню.")

    def show_menu(self, category: Optional[str] = None) -> None:
        """Показывает меню, возможно, отфильтрованное по категории."""
        print("Меню:")
        for item in self.items:
            if category is None or item.category == category:
                print(item)

    def get_items_by_category(self, category: str) -> List[MenuItem]:
        """Возвращает список блюд по категории."""
        return [item for item in self.items if item.category == category]

    def get_item_by_name(self, name: str) -> Optional[MenuItem]:
        """Возвращает элемент меню по имени. Если элемент не найден, возвращает None."""
        for item in self.items:
            if item.name == name:
                return item
        return None

    def get_categories(self) -> List[str]:
        """Возвращает список всех категорий в меню в порядке их появления."""
        categories = []
        seen = set()
        for item in self.items:
            if item.category not in seen:
                categories.append(item.category)
                seen.add(item.category)
        return categories


class Order:
    """Класс для представления заказа."""

    def __init__(self, table_number: int, customer_name: str):
        self.table_number = table_number
        self.customer_name = customer_name
        self.items: List[MenuItem] = []

    def add_item(self, item: MenuItem) -> None:
        """Добавляет элемент в заказ."""
        self.items.append(item)

    def remove_item(self, item_name: str) -> None:
        """Удаляет элемент из заказа по имени."""
        self.items = [item for item in self.items if item.name != item_name]

    def show_order(self) -> None:
        """Показывает текущий заказ."""
        if not self.items:
            print("Заказ пуст.")
        else:
            print(f"Заказ для стола №{self.table_number} (клиент: {self.customer_name}):")
            for item in self.items:
                print(item)
            print(f"Общая сумма: {self.total_price()} руб.")

    def total_price(self) -> float:
        """Возвращает общую сумму заказа."""
        return sum(item.price for item in self.items)

    def clear_order(self) -> None:
        """Очищает заказ."""
        self.items = []

    def to_dict(self) -> Dict:
        """Преобразует заказ в словарь для сохранения в JSON."""
        return {
            "table_number": self.table_number,
            "customer_name": self.customer_name,
            "items": [{"name": item.name, "price": item.price, "category": item.category} for item in self.items],
        }


class Restaurant:
    """Класс для управления рестораном."""

    def __init__(self):
        self.menu = Menu()
        self.orders: Dict[int, Order] = {}
        self.available_tables = {1, 2, 3, 4, 5}  # Пример списка столиков

    def load_menu(self, filename: str) -> None:
        """Загружает меню из файла."""
        self.menu.load_menu(filename)

    def create_order(self, table_number: int, customer_name: str) -> bool:
        """
        Создает новый заказ для стола, если он свободен.
        Возвращает True, если заказ создан, и False, если нет.
        """
        if table_number not in self.available_tables:
            print(f"Столик №{table_number} не существует.")
            return False

        if table_number in self.orders:
            print(f"Столик №{table_number} уже занят.")
            return False

        self.orders[table_number] = Order(table_number, customer_name)
        self.available_tables.remove(table_number)
        print(f"Заказ для стола №{table_number} создан на имя {customer_name}.")
        return True

    def add_to_order(self, table_number: int, item_name: str) -> None:
        """Добавляет элемент в заказ."""
        if table_number not in self.orders:
            print(f"Заказ для стола №{table_number} не найден.")
            return

        item = self.menu.get_item_by_name(item_name)
        if item:
            self.orders[table_number].add_item(item)
            print(f"{item_name} добавлен в заказ для стола №{table_number}.")
        else:
            print(f"Элемент '{item_name}' не найден в меню.")

    def remove_from_order(self, table_number: int, item_name: str) -> None:
        """Удаляет элемент из заказа."""
        if table_number not in self.orders:
            print(f"Заказ для стола №{table_number} не найден.")
            return

        self.orders[table_number].remove_item(item_name)
        print(f"{item_name} удален из заказа для стола №{table_number}.")

    def show_order(self, table_number: int) -> None:
        """Показывает заказ для стола."""
        if table_number not in self.orders:
            print(f"Заказ для стола №{table_number} не найден.")
        else:
            self.orders[table_number].show_order()

    def cancel_order(self, table_number: int) -> None:
        """Отменяет заказ для стола и освобождает столик."""
        if table_number not in self.orders:
            print(f"Заказ для стола №{table_number} не найден.")
        else:
            self.orders[table_number].clear_order()
            del self.orders[table_number]
            self.available_tables.add(table_number)
            print(f"Заказ для стола №{table_number} отменен.")

    def show_available_tables(self) -> None:
        """Показывает свободные столики."""
        print("Свободные столики:", ", ".join(map(str, sorted(self.available_tables))))

    def save_orders(self, filename: str) -> None:
        """Сохраняет все заказы в файл."""
        orders_data = [order.to_dict() for order in self.orders.values()]
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(orders_data, file, ensure_ascii=False, indent=4)
        print("Заказы успешно сохранены.")

    def load_orders(self, filename: str) -> None:
        """Загружает заказы из файла."""
        try:
            with open(filename, "r", encoding="utf-8") as file:
                orders_data = json.load(file)
                for order_data in orders_data:
                    table_number = order_data["table_number"]
                    customer_name = order_data["customer_name"]
                    order = Order(table_number, customer_name)
                    for item_data in order_data["items"]:
                        item = MenuItem(item_data["name"], item_data["price"], item_data["category"])
                        order.add_item(item)
                    self.orders[table_number] = order
                    self.available_tables.discard(table_number)
            print("Заказы успешно загружены.")
        except FileNotFoundError:
            print("Файл заказов не найден.")
        except json.JSONDecodeError:
            print("Ошибка чтения файла заказов.")

    def show_category_menu(self) -> Optional[str]:
        """Показывает меню категорий и возвращает выбранную категорию."""
        categories = self.menu.get_categories()
        if not categories:
            print("Категории не найдены.")
            return None

        print("\nВыберите категорию:")
        russian_letters = "АБВГДЕЖЗИКЛМНОПРСТУФХЦЧШЩЭЮЯ"  # Русские буквы для обозначения категорий
        for i, category in enumerate(categories):
            if i < len(russian_letters):
                print(f"{russian_letters[i]}. {category}")
            else:
                print(f"{i + 1}. {category}")  # Если категорий больше, чем букв, используем числа

        choice = input("Введите букву или номер категории (или 0 чтобы выйти): ").strip().upper()

        if choice == "0":
            return None

        # Проверяем, является ли выбор буквой
        if choice in russian_letters:
            index = russian_letters.index(choice)
            if index < len(categories):
                return categories[index]
        # Проверяем, является ли выбор числом
        elif choice.isdigit():
            index = int(choice) - 1
            if 0 <= index < len(categories):
                return categories[index]

        print("Неверный выбор.")
        return None

    def order_creation_wizard(self) -> None:
        """Пошаговый мастер создания заказа."""
        self.show_available_tables()

        # Проверка корректности ввода номера столика
        try:
            table_number = int(input("Выберите столик: "))
        except ValueError:
            print("Ошибка: номер столика должен быть числом.")
            return

        # Проверка существования и занятости столика
        if table_number not in self.available_tables:
            if table_number in self.orders:
                print(f"Столик №{table_number} уже занят.")
            else:
                print(f"Столик №{table_number} не существует.")
            return

        # Ввод имени заказчика
        customer_name = input("Введите имя заказчика: ")
        if not self.create_order(table_number, customer_name):
            return  # Если заказ не создан, завершаем функцию

        # Выбор блюд по категориям
        while True:
            category = self.show_category_menu()
            if category is None:
                break  # Выход из цикла, если пользователь выбрал "0"

            print(f"\nВыберите блюдо из категории '{category}':")
            items = self.menu.get_items_by_category(category)
            for i, item in enumerate(items, 1):
                print(f"{i}. {item}")
            choice = input("Введите номер блюда (или 0 чтобы пропустить): ")
            if choice.isdigit() and 0 < int(choice) <= len(items):
                selected_item = items[int(choice) - 1]
                self.add_to_order(table_number, selected_item.name)
            else:
                print("Категория пропущена.")

        # Сохранение заказов
        self.save_orders("orders.json")


def main():
    """Основная функция для взаимодействия с пользователем."""
    restaurant = Restaurant()
    restaurant.load_menu("menu.json")  # Загрузка меню из файла
    restaurant.load_orders("orders.json")  # Загрузка заказов из файла

    while True:
        print("\n1. Создать заказ")
        print("2. Показать меню")
        print("3. Показать заказ")
        print("4. Отменить заказ")
        print("5. Показать свободные столики")
        print("6. Выйти")

        choice = input("Выберите действие: ")

        if choice == "1":
            restaurant.order_creation_wizard()

        elif choice == "2":
            category = restaurant.show_category_menu()
            if category:
                restaurant.menu.show_menu(category)

        elif choice == "3":
            table_number = int(input("Введите номер стола: "))
            restaurant.show_order(table_number)

        elif choice == "4":
            table_number = int(input("Введите номер стола: "))
            restaurant.cancel_order(table_number)
            restaurant.save_orders("orders.json")  # Сохранение заказов в файл

        elif choice == "5":
            restaurant.show_available_tables()

        elif choice == "6":
            restaurant.save_orders("orders.json")  # Сохранение заказов перед выходом
            print("Выход из программы.")
            break

        else:
            print("Неверный выбор. Пожалуйста, выберите действие от 1 до 6.")


if __name__ == "__main__":
    main()