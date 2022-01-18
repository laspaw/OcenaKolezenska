from getpass import getpass
from view import *


class FormRestriction:
    lower_letters = 'abcdefghijklmnopqrstuwvxyzęóąśłżźćń'
    upper_letters = 'ABCDEFGHIJKLMNOPQRSTUWVXYZĘÓĄŚŁŻŹĆŃ'
    special = '!#$%&*+-/=?^_`{|}~().,:;<>@[]\'\\'
    digits = '0123456789'

    def __init__(self, min_len: int = 4, max_len: int = 40, allowed_chars: str = lower_letters + upper_letters + special + digits,
                 mandatory_chars: str = ''):
        self.mandatory_chars = mandatory_chars
        self.allowed_chars = allowed_chars
        self.max_len = max_len
        self.min_len = min_len
        self.found_violations = []
        self.value = ''

    def meet_restrictions(self, text):
        flag = True
        if len(text) < self.min_len:
            flag = False
            self.found_violations.append(f'wprowadzony ciąg znaków jest zbyt krótki: {len(text)} < {self.min_len}')
        if len(text) > self.max_len:
            flag = False
            self.found_violations.append(f'wprowadzony ciąg znaków jest zbyt długi: {len(text)} > {self.max_len}')
        for char in text:
            if char not in self.allowed_chars:
                flag = False
                self.found_violations.append(f'niedozwolony znak: \'{char}\'')
        for char in self.mandatory_chars:
            if char not in text:
                flag = False
                self.found_violations.append(f'brak obowiązkowego znaku: \'{char}\'')
        return flag

    def get_violations(self):
        msg = ''
        if len(self.found_violations) == 0:
            return 'żadna zasada nie została naruszona'
        elif len(self.found_violations) == 1:
            msg = 'wprowadzony ciąg naruszył następującą zasade: ' + self.found_violations[0]
        elif len(self.found_violations) > 1:
            msg = 'wprowadzony ciąg naruszył następujące zasady: \n'
            for found_violation in self.found_violations:
                msg += '\t' + found_violation + '\n'
        return msg


class AnonymousUser:
    user_data_form = {
        'imię': FormRestriction(allowed_chars=FormRestriction.lower_letters + FormRestriction.upper_letters + " "),
        'nazwisko': FormRestriction(allowed_chars=FormRestriction.lower_letters + FormRestriction.upper_letters + " "),
        'e-mail': FormRestriction(min_len=6, mandatory_chars='@.'),
    }
    user_password = None

    def __init__(self, database):
        self.database = database

    def login(self):
        user_login = input('Podaj e-mail: ')
        user_password = getpass('Podaj hasło: ')
        if not self.database.check_credentials(user_login, user_password):
            input('Podany login i/lub hasło są niepoprawne.\nNaciśnij <Enter> aby kontynuować')
        else:
            authenticated_user = AuthenticatedUser(self.database, self.database.get_user_id(user_login, user_password))
            after_logon_menu_tree = {
                'main_menu': ConsoleMenu([
                    ConsoleMenuItem('Pokaż dane użytkownika', 'call', authenticated_user.show_personal_data),
                    ConsoleMenuItem('Notatki osobiste', 'menu', 'note_menu'),
                    ConsoleMenuItem('Wyloguj', 'exit-menu')
                ],
                    header='Główne menu\n' + '-' * 40,
                    footer='-' * 40),
                'note_menu': ConsoleMenu([
                    ConsoleMenuItem('Wyświetl notatki', 'call', input, 'Ta opcja nie została jeszcze zaimplementowana.\nNaciśnij <Enter> aby kontynuować'),
                    ConsoleMenuItem('Usuń notatki', 'call', input, 'Ta opcja nie została jeszcze zaimplementowana.\nNaciśnij <Enter> aby kontynuować'),
                    ConsoleMenuItem('Powrót do poprzedniego menu', 'exit-menu')
                ],
                    header='Notatki osobiste\n' + '-' * 40,
                    footer='-' * 40)
            }
            MenuLoop(after_logon_menu_tree, 'main_menu').menu_loop()

    def register(self):
        for field, form_restriction in self.user_data_form.items():
            while not form_restriction.meet_restrictions(value := input(f'Podaj {field}: ')):
                print(form_restriction.get_violations())
            else:
                self.user_data_form[field].value = value

        if self.database.user_already_exist(self.user_data_form['e-mail'].value):
            input(f'Użytkownik o podanym adresie e-mail istnieje już w bazie. Spróbuj opcji odzyskiwania hasła.\nNaciśnij <Enter> aby kontynuować')
            return

        while True:
            while not (password_restriction := FormRestriction()).meet_restrictions(password := getpass('Podaj hasło: ')):
                print(password_restriction.get_violations())
            else:
                self.user_password = password

            if getpass('Wprowadź ponownie hasło: ') != self.user_password:
                print('Wprowadzone hasła różnią się od siebie. Spróbuj jeszcze raz.')
            else:
                break

        try:
            self.database.register_user(
                self.user_data_form['imię'].value,
                self.user_data_form['nazwisko'].value,
                self.user_data_form['e-mail'].value,
                self.user_password)
        except Exception as e:
            input(e)
        else:
            input(f'Użytkownik {self.user_data_form["e-mail"].value} dodany do bazy.\nNaciśnij <Enter> aby kontynuować')

    def restore_login(self):
        input(f'Szkoda na to czasu... szybciej będzie założyć nowe konto :)\nNaciśnij <Enter> aby kontynuować')

    def restore_password(self):
        user_passwords = self.database.get_user_password_by_email(input('Podaj swój adres e-mail: '))
        if len(user_passwords) == 0:
            print(f'Sorry, nie mam takiego adresu e-mail w bazie.')
        else:
            for user_password in user_passwords:
                print(f'Twoje hasło to: "{user_password[0]}"')
        input('Naciśnij <Enter> aby kontynuować')

    def admin_options(self):
        if getpass('Podaj hasło administratora: ') != chr(100) + chr(117) + chr(112) + chr(97):
            input('Wprowadzone hasło jest niepoprawne.\n(wskazówka dotycząca hasła: "tam, gdzie plecy tracą swą szlachetną nazwę\nNaciśnij <Enter> aby kontynuować")')
        else:
            admin_menu_tree = {
                'admin_menu': ConsoleMenu([
                    ConsoleMenuItem('Wyświetl wszystkich użytkowników', 'call', self.show_all_users),
                    ConsoleMenuItem('Powrót do poprzedniego menu', 'exit-menu'),
                ],
                    header='Menu administratora\n' + '-' * 40,
                    footer='-' * 40)}
            MenuLoop(admin_menu_tree, 'admin_menu').menu_loop()

    def show_all_users(self):
        print('-' * 40)
        for first_name, last_name, creation_ts, email, password in self.database.get_all_users():
            print(f'Data utworzenia konta: {creation_ts}')
            print(f'imię: {first_name}')
            print(f'nazwisko: {last_name}')
            print(f'e-mail: {email}')
            print(f'Hasło: {password}')
            print('-' * 40)
        input('Naciśnij <Enter> aby kontynuować')


class AuthenticatedUser:
    def __init__(self, database, user_id):
        self.user_id = user_id
        self.database = database

    def show_personal_data(self):
        creation_ts, last_logon_ts, last_pwd_set, first_name, last_name, email = self.database.get_user_personal_data_by_id(self.user_id)
        print(f'imię: {first_name}')
        print(f'nazwisko: {last_name}')
        print(f'e-mail: {email}')
        print(f'Data utworzenia konta: {creation_ts}')
        print(f'Data ostatniego logowania: {last_logon_ts}')
        print(f'Data ostatniego ustawienia hasła: {last_pwd_set}')
        input('Naciśnij <Enter> aby kontynuować')
        pass
