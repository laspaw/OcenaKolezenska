from view import *
from model import *
from controller import *


class MainApp:
    @staticmethod
    def run():
        # create database /checks tables structure
        database_path = 'OK.db'
        (app_database := ApplicationDatabase(database_path)).initialize()

        anonymous_user = AnonymousUser(app_database)

        # menu tree implementation for anonymous user (before authentication)
        """
        MENU ENGINE description:
        exaple of call: MenuLoop(<menu tree dictionary>, <name of key representing main (starting) menu>).menu_loop()
        menu tree dictionary = {<name of menu>:<ConsoleMenu object>, ..} -> defines multiple menus to be used sa a batch for MenuLoop class' object
        ConsoleMenu(<list of ConsoleMenuItem objects>, <menu options as kwargs>)) -> defines single menu
        ConsoleMenuItem(<text that will be shown as menu item>, <action to be done when user choose this option>, 
                        <*args to be passeed to choosed action>, <**kwargs to be passed to choosed action>)
            -> defines single menu item
        possible actions:
        - 'call' -> given functions will be executed with all following args and kwargs
        - 'menu' -> menu_loop method will launch sub menu with key-name given as next arg (all other args ang kwargs will be ignored)
        - 'exit-menu' -> backs to previous menu if used in sub-menu -OR- quits menu loop if used in main menu; (all args ang kwargs will be ignored)
        """
        before_logon_menu_tree = {
            'restore_credentials_menu': ConsoleMenu([
                ConsoleMenuItem('Nie pamiętam loginu', 'call', anonymous_user.restore_login),
                ConsoleMenuItem('Nie pamiętam hasła', 'call', anonymous_user.restore_password),
                ConsoleMenuItem('Powrót do poprzedniego menu', 'exit-menu'),
            ],
                header='Menu ozdyskiwania loginu lub hasła\n' + '-' * 40,
                footer='-' * 40),

            'logon_menu': ConsoleMenu([
                ConsoleMenuItem('Logowanie', 'call', anonymous_user.login),
                ConsoleMenuItem('Rejestracja', 'call', anonymous_user.register),
                ConsoleMenuItem('Zapomniałem login/hasła', 'menu', 'restore_credentials_menu'),
                ConsoleMenuItem('Opcje administatora', 'call', anonymous_user.admin_options),
                ConsoleMenuItem('Zakończ aplikację', 'call', quit, 0)
            ],
                header='Menu logowania\n' + '-' * 40,
                footer='-' * 40)
        }

        # starts menu loop
        MenuLoop(before_logon_menu_tree, 'logon_menu').menu_loop()


if __name__ == '__main__':
    try:
        MainApp.run()
    except Exception as e:
        print('Wystąpił niespodziewany wyjątek:',e)
