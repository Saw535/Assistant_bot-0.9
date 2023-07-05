import pickle
import re
import os
import shutil
from datetime import datetime
from collections import UserDict
from copy import deepcopy
from difflib import SequenceMatcher
from abc import ABC, abstractmethod


class DisplayView(ABC):
    @abstractmethod
    def display(self):
        pass

class ConsoleView(DisplayView):
    def display(self, data):
        print(data)

class Name():
    def __init__(self, name: str) -> None:
        self.name = name

    def __str__(self) -> str:
        return f'{self.name}'


class Address():
    def __init__(self, address: str) -> None:
        self.address = address

    def __str__(self) -> str:
        return f'{self.address}'


class Phone():
    def __init__(self, phone: str) -> None:
        self.phone = phone

    @staticmethod
    def phone_validator(phone: str):
        if re.fullmatch(r'\+[\d]{2}\([\d]{3}\)[\d]{7}', phone):
            return True

    def __str__(self) -> str:
        return f'{self.phone}'


class Email():
    def __init__(self, email: str) -> None:
        self.email = email

    @staticmethod
    def email_validator(email: str):
        if re.fullmatch(r'[a-zA-Z]{1}[\w\.]+@[a-zA-Z]+\.[a-zA-Z]{2,3}', email):
            return True

    def __str__(self) -> str:
        return f'{self.email}'


class Birthday():
    def __init__(self, birthday: str) -> None:
        self.birthday = datetime.strptime(birthday, '%Y.%m.%d').date()

    @staticmethod
    def date_validator(birthday: str):
        try:
            if 100*365 > (datetime.today() - datetime.strptime(birthday, '%Y.%m.%d')).days > 0:
                return True
        except:
            return False

    def __str__(self) -> str:
        return f'{self.birthday}'


class Hashtag():
    def __init__(self, hashtag: str) -> None:
        self.hashtag = hashtag

    def __str__(self) -> str:
        return f'{self.hashtag}'


class Note():
    def __init__(self, note: str) -> None:
        self.note = note

    def __str__(self) -> str:
        return f'{self.note}'


class Record:
    def __init__(self, name: Name, address: Address = None, phone: list[Phone] = None, email: Email = None, birthday: Birthday = None):
        self.name = name
        self.address = address
        self.phones = []
        self.email = email
        self.birthday = birthday

        if address is not None:
            self.add_address(address)

        if phone is not None:
            for p in phone:
                self.add_phone(p)

        if email is not None:
            self.add_email(email)

        if birthday is not None:
            self.add_birthday(birthday)

    def add_address(self, address: Address):
        self.address = address

    def add_phone(self, phone: Phone):
        self.phones.append(phone)

    def add_email(self, email: Email):
        self.email = email

    def add_birthday(self, birthday: Birthday):
        self.birthday = birthday

    def __str__(self) -> str:
        record_str = f"Name: {self.name}\n"

        if self.address is not None:
            record_str += f"Address: {self.address}\n"

        if self.phones:
            record_str += "Phone(s):\n"
            for phone in self.phones:
                record_str += f"- {phone}\n"

        if self.email is not None:
            record_str += f"Email: {self.email}\n"

        if self.birthday is not None:
            record_str += f"Birthday: {self.birthday}\n"

        return record_str

class Notice:
    def __init__(self, hashtag: Hashtag, note: Note = None):

        self.hashtag = hashtag

        self.notes = []
        if note is not None:
            self.add_note(note)

    def add_hashtag(self, hashtag: Hashtag):
        self.hashtag = hashtag

    def add_note(self, note: Note | str):
        if isinstance(note, str):
            note = self.create_note(note)
        self.notes.append(note)

    def create_note(self, note: str):
        return Note(note)

    def show(self):         # returns notes in nice formating
        if self.notes:
            result = ''
            for inx, n in enumerate(self.notes):
                result += f' {inx+1}: {n}'
        else:
            result = None
        return result

    def __str__(self) -> str:
        return f'Hashtag: {self.hashtag},\nNotes: {self.show()}\n'


class AddressBook(UserDict):

    def __init__(self, record: Record | None = None, notice: Notice | None = None) -> None:
        self.records = {}
        if record is not None:
            self.add_record(record)

        self.notes = {}
        if notice is not None:
            self.add_notice(notice)

    def add_record(self, record: Record):
        self.records[record.name.name] = record

    def add_notice(self, notice: Notice):
        self.notes[notice.hashtag.hashtag] = notice

    def note_searcher(self, keyword: str):
        result = []
        for notice in self.notes.values():
            for note in notice.notes:
                if keyword.lower() in note.note.lower():
                    result.append(note)
        return result

    def hashtag_searcher(self, keyword: str):
        result = []
        for notice in self.notes.values():
            if keyword.lower() in notice.hashtag.hashtag.lower():
                result.append(notice)
        return result

    def sort_notes(self):
        sorted_notes = sorted(self.notes.values(),
                              key=lambda notice: str(notice.hashtag))
        return sorted_notes

    def iterator(self, N, essence):
        counter = 0
        result = f'\nPrinting {N} contacts'
        for item, record in essence.items():
            result += f'\n{str(record)}'
            counter += 1
            if counter >= N:
                yield result
                counter = 0
                result = f'\nPrinting next {N} contacts'

    def __str__(self) -> str:
        return '\n'.join(str(record) for record in self.records.values())

    def __deepcopy__(self, memodict={}):
        copy_ab = AddressBook(self, self.records, self.notes)
        memodict[id(self)] = copy_ab
        for el in self.records:
            copy_ab.append(deepcopy(el, memodict))
        for el in self.notes:
            copy_ab.append(deepcopy(el, memodict))
        return copy_ab


address_book = AddressBook()


# General functionality


def copy_class_addressbook(address_book):
    return deepcopy(address_book)


def unknown_command(command: str) -> str:
    if len(command) < 4:
        return f'\nUnknown command "{command}"\n'
    else:
        result = ''
        subcomands = command.split(' ')
        for key, value in commands.items():

            for el in subcomands:
                if len(el) > 2 and el in key:
                    if key not in result:
                        result += f'{key}{value[1]}\n'

            if len(key) >= len(command):
                start = 0
                end = len(command) - 1
                while True:
                    if SequenceMatcher(a=command, b=key[start:end]).ratio() > 0.6 and key not in result:
                        result += f'{key}{value[1]}\n'
                    start += 1
                    end += 1
                    if end > len(key) - 1:
                        break

        if result:
            return f'\nUnknown command "{command}"\nPossibel commands:\n{result}'
        else:
            return f'\nUnknown command "{command}"\n'


def hello_user() -> str:
    return '\nHow can I help you?\n'


def exit_func() -> str:
    a = input('Would you like to save changes (Y/N)? ')
    if a == 'Y' or a == 'y':
        print(saver())
    return 'Goodbye!\n'


def saver() -> str:
    if address_book.records:
        with open('backup.dat', 'wb') as file:
            pickle.dump(address_book, file)
        return '\nAddress Book successfully saved to backup.dat'
    else:
        return '\nAddress Book is empty, no data to be saved to file'


def loader() -> str:
    try:
        with open('backup.dat', 'rb') as file:
            global address_book
            address_book = pickle.load(file)
        return '\nAddress Book successfully loaded from backup.dat\n'
    except:
        return ''


def helper():
    result = 'List of all supported commands:\n\n'
    for key in commands:
        result += '{:<13} {:<50}\n'.format(key, commands[key][1])
    return result


# Contacts processing


def phone_adder(record) -> None:
    while True:
        phone = input(
            'Enter phone (ex. +38(099)1234567) or press Enter to skip: ')
        if phone == '':
            break
        elif Phone.phone_validator(phone) == True:
            record.add_phone(Phone(phone))
            break
        else:
            print('Wrong phone format')


def email_adder(record) -> None:
    while True:
        email = input('Enter email or press Enter to skip: ')
        if email == '':
            break
        elif Email.email_validator(email) == True:
            record.add_email(Email(email))
            break
        else:
            print('Wrong email format')


def birthday_adder(record) -> None:
    while True:
        birthday = input(
            'Enter birthday (ex. 2023.12.25) or press Enter to skip: ')
        if birthday == '':
            break
        elif Birthday.date_validator(birthday) == True:
            record.add_birthday(Birthday(birthday))
            break
        else:
            print('Wrong date format')


def contact_adder() -> str:
    name = input('Enter contact name (obligatory field): ')
    while True:
        if name == '':
            name = input(
                'Contact name cannot be empty, enter contact name o Enter to exit: ')
            if name == '':
                return 'Adding new contact was skipped\n'
        elif name in address_book.records.keys():
            name = input(
                f'Contact "{name}" already exists, enter new name o press Enter to exit: ')
            if name == '':
                return 'Adding new contact was skipped\n'
        else:
            break

    record = Record(Name(name))

    address = input('Enter address or press Enter to skip: ')
    if address:
        record.add_address(Address(address))

    while True:
        phone = input(
            'Enter phone (ex. +38(099)1234567) or press Enter to skip: ')
        if phone == '':
            break
        elif Phone.phone_validator(phone) == True:
            record.add_phone(Phone(phone))
        else:
            print('Wrong phone format')

    email_adder(record)
    birthday_adder(record)

    address_book.add_record(record)

    return f'\nAdded contact\n{record}'


def show_all_contacts() -> str:
    if address_book.records:
        N = int(input('How many contacts to show? '))
        if N < 1:
            return 'Input cannot be less that 1'
        elif N >= len(address_book.records):
            result = '\nPrintting all records:\n'
            for key, value in address_book.records.items():
                result += f'\n{value}'
            result += '\nEnd of address book\n'
            return result
        else:
            iter = address_book.iterator(N, address_book.records)
            for i in iter:
                print(i)
                input('Press any key to continue: ')
            if len(address_book.records) % 2 == 0:
                return '\nEnd of address book\n'
            else:
                return f'{str(list(address_book.records.values())[-1])}\nEnd of address book\n'
    else:
        return 'No contacts, please add\n'


def contact_search() -> str:
    search_query = input('Enter search query: ')
    search_query = search_query.lower()

    search_results = []
    for record in address_book.records.values():
        if (record.name.name and search_query in record.name.name.lower()) or \
           (record.address and search_query in record.address.lower()) or \
           (record.email and search_query in record.email.lower()) or \
           (record.birthday and search_query in str(record.birthday)) or \
                any(search_query in phone.phone for phone in record.phones):
            search_results.append(record)

    if search_results:
        contacts_info = '\n'.join(str(record) for record in search_results)
        return f'\nContacts found:\n{contacts_info}'

    return f'No contacts found for "{search_query}"'


def contact_modifier():
    name = input('Enter contact name: ')
    for record_name, contact in address_book.records.items():
        if contact.name.name.lower() == name.lower():
            print(f'Current contact information:\n{contact}')
            field = input(
                'Enter the field you want to modify (name/address/phone/email/birthday): ')

            if field.lower() == 'name':
                value = input('Enter the new value: ')
                contact.name.name = value
                address_book.records[value] = contact
                del address_book.records[record_name]
                return f'Contact "{name}" has been modified. New name: "{value}"'
            elif field.lower() == 'address':
                value = input('Enter the new value: ')
                contact.address = Address(value)
                return f'Contact "{name}" has been modified. New address: "{value}"'
            elif field.lower() == 'phone':
                phone_count = len(contact.phones)
                if phone_count == 0:
                    action = input('Enter "add" to add a new phone number: ')
                    if action.lower() == 'add':
                        phone = input(
                            'Enter the new phone number (ex. +38(099)1234567): ')
                        if Phone.phone_validator(phone):
                            contact.phones.append(Phone(phone))
                            return f'Contact "{name}" has been modified. New phone number added: {phone}'
                        else:
                            return 'Wrong phone format'
                    else:
                        return 'Invalid action. Modification failed.'
                else:
                    print('Current phone numbers:')
                    for i, phone in enumerate(contact.phones):
                        print(f'{i + 1}. {phone}')
                    selection = int(input(
                        f'Select the phone number you want to modify or enter "{phone_count + 1}" to add a new phone number: '))
                    if 1 <= selection <= phone_count:
                        action = input(
                            'Enter "replace" to replace the phone number: ')
                        if action.lower() == 'replace':
                            phone = input(
                                'Enter the new phone number (ex. +38(099)1234567): ')
                            if Phone.phone_validator(phone):
                                contact.phones[selection - 1] = Phone(phone)
                                return f'Contact "{name}" has been modified. New phone number: {phone}'
                            else:
                                return 'Wrong phone format'
                        else:
                            return 'Invalid action. Modification failed.'
                    elif selection == phone_count + 1:
                        phone = input(
                            'Enter the new phone number (ex. +38(099)1234567): ')
                        if Phone.phone_validator(phone):
                            contact.phones.append(Phone(phone))
                            return f'Contact "{name}" has been modified. New phone number added: {phone}'
                        else:
                            return 'Wrong phone format'
                    else:
                        return 'Invalid selection. Modification failed.'

            elif field.lower() == 'email':
                value = input('Enter the new value: ')
                if Email.email_validator(value) == True:
                    contact.email = Email(value)
                    return f'Contact "{name}" has been modified. New email: "{value}"'
                else:
                    return 'Wrong email format'
            elif field.lower() == 'birthday':
                value = input('Enter the new value (ex. 2023.12.25): ')
                if Birthday.date_validator(value) == True:
                    contact.birthday = Birthday(value)
                    return f'Contact "{name}" has been modified. New birthday: "{value}"'
                else:
                    return 'Wrong date format'
            else:
                return 'Invalid field name. Modification failed.'
    return f'Contact "{name}" not found'


def contact_remover() -> str:
    name = input('Enter contact name: ')
    for record_name, record in address_book.records.items():
        if record.name.name == name:
            print(f'Contact found: {record.name.name}')
            choice = input(
                'Enter the field to remove (1- contact, 2 - number, 3 - email, 4 - adress, 5 - birthday) ')
            if choice == '1':
                del address_book.records[record_name]
                return f'Contact "{name} has been removed'
            elif choice == '2':
                print('Phone numbers:')
                for i, phone in enumerate(record.phones):
                    print(f'{i+1}. {phone}')
                phone_choice = int(input(
                    'Enter the number of the phone to remove, or enter 0 to remove all phone numbers: '))
                if phone_choice == 0:
                    record.phones = []
                    return f'All phone numbers removed from contact {name}'
                elif 1 <= phone_choice <= len(record.phones):
                    del record.phones[phone_choice - 1]
                    return f'Phone number {phone_choice} removed from contact {name}'
                else:
                    return 'Invalid phone number choice'
            elif choice == '3':
                record.email = None
                return f'Email removed from contact {name}'
            elif choice == '4':
                record.address = None
                return f'Address removed from contact {name}'
            elif choice == '5':
                record.birthday = None
                return f'Birthday removed from contact {name}'
            else:
                return f'Invalid choice'
        return f'Contact "{name}" not found'


def days_to_birthdays() -> str:
    days = int(input('Enter the number of days: '))
    today = datetime.today().date()
    result = ''

    for record in address_book.records.values():
        if record.birthday is not None:
            dob = record.birthday.birthday
            dob_this_year = dob.replace(year=today.year)

            if dob_this_year < today:
                dob_this_year = dob_this_year.replace(year=today.year + 1)

            days_to_birthday = (dob_this_year - today).days
            if days_to_birthday <= days:
                result += f'\n{record}'
    if result == '':
        return "\nNo contacts with upcoming birthdays\n"
    else:
        return f"\nContacts with upcoming birthdays in the next {days} days:\n{result}"


# Notes processing


def note_adder():
    hashtag = input('Enter hashtag for your note (ex. #todo): ')
    if hashtag in address_book.notes.keys():
        return f'Note with hashtag {hashtag} already exists'

    if not hashtag:
        hashtag = '#None'

    notice = Notice(Hashtag(hashtag))

    note = input('Enter note: ')
    if note:
        notice.add_note(Note(note))

    address_book.add_notice(notice)

    return f'\nAdded reccord with {notice}'


def show_all_notes() -> str:
    if address_book.notes:
        N = int(input('How many records to show? '))
        if N < 1:
            return 'Input cannot be less that 1'
        elif N >= len(address_book.notes):
            result = '\nPrintting all records:\n'
            for key, value in address_book.notes.items():
                result += f'\n{value}'
            result += '\nEnd of records\n'
            return result
        else:
            iter = address_book.iterator(N, address_book.notes)
            for i in iter:
                print(i)
                input('Press any key to continue: ')
            if len(address_book.notes) % 2 == 0:
                return '\nEnd of records\n'
            else:
                return f'{str(list(address_book.notes.values())[-1])}\nEnd of records\n'
    else:
        return 'No records, please add\n'


def note_search_handler():
    keyword = input('Enter a keyword to search: ')
    if keyword:
        result = address_book.note_searcher(keyword)
        if result:
            return f'\nFound {len(result)} notes:\n' + '\n'.join(str(note) for note in result)
        else:
            return 'No notes found.'
    else:
        return 'Keyword cannot be empty.'


def hashtag_search_handler():
    keyword = input('Enter a hashtag to search: ')
    if keyword:
        result = address_book.hashtag_searcher(keyword)
        if result:
            return f'\nFound {len(result)} notes:\n' + '\n'.join(str(note) for note in result)
        else:
            return 'No notes found.'
    else:
        return 'Hashtag cannot be empty.'


def sort_notes_handler():
    sorted_notes = address_book.sort_notes()
    if sorted_notes:
        return f'\nSorted notes:\n' + '\n'.join(str(note) for note in sorted_notes)
    else:
        return 'No notes found.'


# File sorting


def sort_files():
    folder_path = input(
        "Enter the absolute path of the folder you want to sort (example: C:\Desktop\project): ")
    folder_path = folder_path.strip()

    if not os.path.isdir(folder_path):
        return "Invalid folder path."

    categorized_files = {}

    for file_name in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, file_name)):
            if file_name in ("butler.py", "backup.dat"):
                continue

            file_extension = os.path.splitext(file_name)[1]
            category = "Other"
            if file_extension in (".jpg", ".png", ".gif"):
                category = "Images"
            elif file_extension in (".doc", ".docx", ".pdf"):
                category = "Documents"
            elif file_extension in (".mp4", ".avi", ".mov"):
                category = "Videos"

            if category not in categorized_files:
                categorized_files[category] = []

            categorized_files[category].append(file_name)

    if not categorized_files:
        return "No files found for sorting."

    for category in categorized_files.keys():
        category_folder = os.path.join(folder_path, category)
        os.makedirs(category_folder, exist_ok=True)

    for category, files in categorized_files.items():
        category_folder = os.path.join(folder_path, category)
        for file_name in files:
            source_path = os.path.join(folder_path, file_name)
            destination_path = os.path.join(category_folder, file_name)
            shutil.move(source_path, destination_path)

    return "File sorting completed successfully."


commands = {
    'hello':        (hello_user,            ' -> just greating'),
    'exit':         (exit_func,             ' -> exit from the bot with or without saving'),
    'close':        (exit_func,             ' -> exit from the bot with or without saving'),
    'save':         (saver,                 ' -> saves to file all changes'),
    'load':         (loader,                ' -> loads last version of the Address Book'),
    'help':         (helper,                ' -> shows the list of all supported commands'),
    'add contact':  (contact_adder,         ' -> adds new contact'),
    '+c':           (contact_adder,         ' -> adds new contact (short command)'),
    'show contacts': (show_all_contacts,    ' -> shows all contacts'),
    '?c':           (show_all_contacts,     ' -> shows all contacts (short command)'),
    'search':       (contact_search,        ' -> search for a contact by name'),
    'modify':       (contact_modifier,      ' -> modify an existing contact'),
    'remove':       (contact_remover,       ' -> remove an existing contact'),
    'to birthdays': (days_to_birthdays,     ' -> days to birthgays'),
    'add note':     (note_adder,            ' -> adds note with o without hashtag'),
    '+n':           (note_adder,            ' -> adds note with o without hashtag (short command)'),
    'show notes':   (show_all_notes,        ' -> shows all notes'),
    '?n':           (show_all_notes,        ' -> shows all notes (short command)'),
    'search notes': (note_search_handler,   ' -> searches for notes containing a keyword'),
    '?s':           (note_search_handler,   ' -> searches for notes containing a keyword (short command)'),
    'search hashtag': (hashtag_search_handler, ' -> search notes by hashtag'),
    '?h':           (hashtag_search_handler, ' -> search notes by hashtag (short command)'),
    'sort notes':   (sort_notes_handler,    ' -> sort notes by title'),
    'so':           (sort_notes_handler,    ' -> sort notes by title (short command)'),
    'sort files':   (sort_files,            ' -> sorts files into categories'),
}


def main():
    print(loader())
    while True:
        phrase = input('Please enter command or type "help": ').strip()
        command = None
        for key in commands:
            if phrase.lower() == key:
                command = key
                break

        if not command:
            result = unknown_command(phrase)
        else:
            handler = commands.get(command)[0]
            result = handler()
            if result == 'Goodbye!\n':
                print(result)
                break
        print(result)


if __name__ == '__main__':
    main()