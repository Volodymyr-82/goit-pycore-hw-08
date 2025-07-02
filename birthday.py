from collections import UserDict
import re
from datetime import datetime, timedelta
import pickle 

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value):
        if not value.strip():
            raise ValueError("Name cannot be empty")
        super().__init__(value.strip())

class Phone(Field):
    def __init__(self, value):
        # Clean the phone number (remove spaces, dashes, etc.)
        cleaned_value = re.sub(r'[^\d]', '', value)
        if not cleaned_value.isdigit() or len(cleaned_value) != 10:
            raise ValueError('Phone number must consist of exactly 10 digits')
        super().__init__(cleaned_value)

class Birthday(Field):
    def __init__(self, value):
        date_format = "%d.%m.%Y"
        try:
            # Validate and store the datetime object
            self.date = datetime.strptime(value, date_format).date()
            super().__init__(value)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None
    
    def add_phone(self, phone_number):
        self.phones.append(Phone(phone_number))

    def add_birthday(self, birthday_str):
        self.birthday = Birthday(birthday_str)

    def remove_phone(self, phone_number):
        # Clean the input for comparison
        cleaned_number = re.sub(r'[^\d]', '', phone_number)
        for phone in self.phones:
            if phone.value == cleaned_number:
                self.phones.remove(phone)
                return True
        return False
    
    def edit_phone(self, old_phone_number, new_phone_number):
        cleaned_old = re.sub(r'[^\d]', '', old_phone_number)
        for idx, phone in enumerate(self.phones):
            if phone.value == cleaned_old:
                self.phones[idx] = Phone(new_phone_number)
                return
        raise ValueError('Old phone number not found')
    
    def find_phone(self, phone_number):
        cleaned_number = re.sub(r'[^\d]', '', phone_number)
        for phone in self.phones:
            if phone.value == cleaned_number:
                return phone
        return None
    
    def __str__(self):
        phone_str = "; ".join(phone.value for phone in self.phones) if self.phones else "No phones"
        birthday_str = f", birthday: {self.birthday.value}" if self.birthday else ""
        return f'Contact name: {self.name.value}, phones: {phone_str}{birthday_str}'


class AddressBook(UserDict):
    FILE = "addressbook.pkl"
    def add_record(self, record):
        self.data[record.name.value] = record
    
    def find(self, name):
        return self.data.get(name, None)
    
    def delete(self, name):
        if name in self.data:
            del self.data[name]
            return True
        return False
    
    def get_upcoming_birthdays(self):
        upcoming_birthdays = []
        today = datetime.today().date()

        for record in self.data.values():
            if record.birthday is None:
                continue
            try:
                birthday_date = record.birthday.date
                birthday_this_year = birthday_date.replace(year=today.year)

                if birthday_this_year < today:
                    birthday_this_year = birthday_date.replace(year=today.year + 1)

                days_until_birthday = (birthday_this_year - today).days

                if 0 <= days_until_birthday <= 7:
                    congratulation_date = birthday_this_year
                    if birthday_this_year.weekday() == 5:  # Saturday
                        congratulation_date += timedelta(days=2)
                    elif birthday_this_year.weekday() == 6:  # Sunday
                        congratulation_date += timedelta(days=1)

                    upcoming_birthdays.append({
                        "name": record.name.value,
                        "birthday": congratulation_date.strftime("%d.%m.%Y")
                    })

            except (ValueError, AttributeError):
                continue

        return upcoming_birthdays


    def save_data(book, filename="addressbook.pkl"):
        with open(filename, "wb") as f:
            pickle.dump(book, f)

    def load_data(filename="addressbook.pkl"):
        try:
            with open(filename, "rb") as f:
                return pickle.load(f)
        except FileNotFoundError:
            return AddressBook()

    
    
    def __str__(self):
        if not self.data:
            return "Address book is empty"
        return "\n".join(str(record) for record in self.data.values())


            



if __name__ == "__main__":

    # Створення нової адресної книги
    book = AddressBook()

    # Створення запису для John
    john_record = Record("John")
    john_record.add_phone("1234567890")
    john_record.add_phone("5555555555")
    john_record.add_birthday("12.12.2024")
    # Додавання запису John до адресної книги
    book.add_record(john_record)

    # Створення та додавання нового запису для Jane
    jane_record = Record("Jane")
    jane_record.add_phone("9876543210")
    book.add_record(jane_record)

    # Виведення всіх записів у книзі
        
    print(book)

    # Знаходження та редагування телефону для John
    john = book.find("John")
    john.edit_phone("1234567890", "1112223333")

    print(john)  # Виведення: Contact name: John, phones: 1112223333; 5555555555

    # Пошук конкретного телефону у записі John
    found_phone = john.find_phone("5555555555")
    print(f"{john.name}: {found_phone}")  # Виведення: John: 5555555555

    # Видалення запису Jane
    book.delete("Jane")
    book.save_data()
        
        

