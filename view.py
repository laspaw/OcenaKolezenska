import os

class ConsoleMenuItem:
    def __init__(self, display_text: str, action, *args, **kwargs):
        self.action = action
        self.display_text = display_text
        self.args = args
        self.kwargs = kwargs


class ConsoleMenu:
    def __init__(self, menu_items, header='', footer=''):
        self.menu_items = menu_items
        self.header = header
        self.footer = footer


class RunConsoleMenu:
    def __init__(self, menu):
        self.menu = menu

    def print_menu(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(self.menu.header)
        i = 0
        for menu_item in self.menu.menu_items:
            i += 1
            print(str(i) + '. ' + menu_item.display_text)
        print(self.menu.footer)

    def get_user_response(self):
        while True:
            user_option = input('Podaj numer wybranej opcji z menu: ')
            try:
                user_option = int(user_option)
            except ValueError:
                print(f'\"{user_option}\" nie jest liczbą')
            else:
                if 1 <= user_option <= len(self.menu.menu_items):
                    return_obj = self.menu.menu_items[int(user_option) - 1]
                    return {'action_type': return_obj.action, 'args': return_obj.args, 'kwargs': return_obj.kwargs}
                else:
                    print(f'Podaj liczbę z zakresu od 1 do {len(self.menu.menu_items)}')

    def launch(self):
        self.print_menu()
        return self.get_user_response()


class MenuLoop:
    def __init__(self, menu_tree, start_menu):
        self.start_menu = start_menu
        self.menu_tree = menu_tree

    # this method creates one instance per each single menu
    # runs recursion when goint to sub menus
    def menu_loop(self):
        while True:
            user_response = RunConsoleMenu(self.menu_tree[self.start_menu]).launch()
            if user_response['action_type'] == 'menu':
                MenuLoop(self.menu_tree, user_response['args'][0]).menu_loop()
            elif user_response['action_type'] == 'exit-menu':
                break
            elif user_response['action_type'] == 'call':
                user_response['args'][0](*user_response['args'][1:], **user_response['kwargs'])
