import sqlite3
import os


class SQLiteDatabase:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def connect_and_commit(self, command, arg=None):
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            if arg is None:
                cursor.execute(command)
            else:
                cursor.execute(command, arg)
            connection.commit()

    def connect_and_fetchall(self, command, arg=None):
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            if arg is None:
                cursor.execute(command)
            else:
                cursor.execute(command, arg)
            return cursor.fetchall()

    def connect_and_fetchone(self, command, arg=None):
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            if arg is None:
                cursor.execute(command)
            else:
                cursor.execute(command, arg)
            return cursor.fetchone()


class ApplicationDatabase(SQLiteDatabase):
    def create_tables(self):
        tables_creation_command = ["""
                CREATE TABLE user_accounts(
                    `user_id` INTEGER PRIMARY KEY AUTOINCREMENT,
                    `creation_ts` NOT_NULL TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    `last_logon_ts` TIMESTAMP,
                    `last_pwd_set` NOT_NULL TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    `first_name` NOT_NULL VARCHAR(64),
                    `last_name` NOT_NULL VARCHAR(64),
                    `email` NOT_NULL VARCHAR(128) UNIQUE,
                    `password` NOT_NULL VARCHAR(64)
                )"""]
        for table_creation_command in tables_creation_command:
            self.connect_and_commit(table_creation_command)

    def register_user(self, first_name, last_name, email, password):
        self.connect_and_commit(
            "INSERT INTO user_accounts(`first_name`, `last_name`, `email`, `password`) VALUES(?,?,?,?)",
            (first_name, last_name, email, password)
        )

    def check_consistency(self):
        # to be implemented
        pass

    def initialize(self):
        if os.path.exists(self.db_path):
            self.check_consistency()
        else:
            self.create_tables()

    def check_credentials(self, email, password):
        sqlcmd = f'SELECT `user_id` FROM user_accounts WHERE `email`="{email}" AND `password`="{password}"'
        return True if len(self.connect_and_fetchall(sqlcmd)) == 1 else False

    def get_user_id(self, email, password):
        sqlcmd = f'SELECT `user_id` FROM user_accounts WHERE `email`="{email}" AND `password`="{password}"'
        return self.connect_and_fetchone(sqlcmd)[0]

    def user_already_exist(self, email):
        sqlcmd = f'SELECT `email` FROM user_accounts WHERE `email`="{email}"'
        return True if len(self.connect_and_fetchall(sqlcmd)) > 0 else False

    def get_user_password_by_email(self, email):
        sqlcmd = f'SELECT `password` FROM user_accounts WHERE `email`="{email}"'
        return self.connect_and_fetchall(sqlcmd)

    def get_user_personal_data_by_id(self, user_id):
        sqlcmd = f'SELECT `creation_ts`, `last_logon_ts`, `last_pwd_set`, `first_name`, `last_name`, `email` FROM user_accounts WHERE `user_id`="{user_id}"'
        return self.connect_and_fetchone(sqlcmd)

    def get_all_users(self):
        sqlcmd = f'SELECT `first_name`, `last_name`,  `creation_ts`, `email`, `password` FROM user_accounts'
        return self.connect_and_fetchall(sqlcmd)



