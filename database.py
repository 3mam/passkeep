from array import array
from os import access, error, set_blocking
import sqlite3
import input
import crypto


class DataBase:
    def __init__(self):
        self._connect = sqlite3.connect('database')
        self._query = self._connect.cursor()

    def __exit__(self):
        self._connect.close()

    def init(self):
        self._query.execute(
            'CREATE TABLE IF NOT EXISTS items(id INTEGER PRIMARY KEY, name TEXT UNIQUE)')
        self._query.execute(
            'CREATE TABLE IF NOT EXISTS accounts(id INTEGER PRIMARY KEY, login TEXT, password BLOB, item_id INTEGER, UNIQUE(login, item_id))')
        self._query.execute(
            'CREATE TABLE IF NOT EXISTS settings(name TEXT UNIQUE, value BLOB)')
        self._connect.commit()
        return self

    def set_settings(self, test_token: bytearray, salt: bytearray):
        self._query.execute(
            'INSERT INTO settings (name, value) VALUES (?, ?)', ('token', test_token))
        self._query.execute(
            'INSERT INTO settings (name, value) VALUES (?, ?)', ('salt', salt))
        self._connect.commit()

        return self

    def get_token(self) -> bytearray:
        token = self._query.execute(
            'SELECT value FROM settings WHERE name="token"').fetchone()[0]
        return token

    def get_salt(self) -> bytearray:
        salt = self._query.execute(
            'SELECT value FROM settings WHERE name="salt"').fetchone()[0]
        return salt

    def is_password_correct(self, password: bytearray):
        key = crypto.Key(password, self.get_salt())
        token = self.get_token()
        try:
            decrypt_token = key.decrypt(token).decode('utf-8')
            is_ok = decrypt_token == 'this is test token'
            if is_ok:
                print('access granted')
            else:
                print('wrong password')
            return (key, True) if is_ok else (None, False)
        except UnicodeDecodeError:
            print('wrong password')
            return (None, False)

    def create_item(self, name):
        try:
            self._query.execute(
                'INSERT INTO items (name) VALUES (?)', (name,))
            self._connect.commit()
            print(f'add {name} to items')
            return self.get_item(name)
        except:
            print(f'{name} exist')
            return 0

    def edit_item(self, name, new_name):
        id = self.get_item_id(name)
        if id:
            self._query.execute(
                'UPDATE items SET name=? WHERE id=?', (new_name, id))
            self._connect.commit()
            print(f'{name} is now {new_name} in item')

    def get_item_id(self, name):
        try:
            return self._query.execute(
                'SELECT id FROM items WHERE name=?', (name,)).fetchone()[0]
        except:
            print(f'item {name} not exist')
            return 0

    def create_account(self, item, login):
        item_id = self.get_item_id(item)
        try:
            if item_id:
                self._query.execute(
                    'INSERT INTO accounts (login, item_id) VALUES (?, ?)', (login, item_id))
                self._connect.commit()
                print(f'create account {login} in {item}')
                return self.get_account_id(item, login)
        except:
            print(f'login {login} in item {item} exist')
            return 0

    def get_account_id(self, item, login):
        try:
            item_id = self.get_item_id(item)
            return self._query.execute(
                'SELECT id FROM accounts WHERE login=? AND item_id=?', (login, item_id)).fetchone()[0]
        except:
            print(f'login {login} not exist')
            return 0

    def edit_account(self, item, login, new_name):
        item_id = self.get_item_id(item)
        account_id = self.get_account_id(item, login)
        if item_id and account_id:
            self._query.execute(
                'UPDATE accounts SET login=? WHERE id=? AND item_id=?', (new_name, account_id, item_id))
            self._connect.commit()
            print(f'login {login} in {item} is now {new_name}')

    def edit_password(self, item: str, login: str, password: bytearray):
        item_id = self.get_item_id(item)
        account_id = self.get_account_id(item, login)
        if item_id and account_id:
            self._query.execute(
                'UPDATE accounts SET password=? WHERE id=? AND item_id=?', (password, account_id, item_id))
            self._connect.commit()
            print(
                f'password is set for login {login} in {item} item')

    def read_password(self, item: str, login: str)->bytearray:
        item_id = self.get_item_id(item)
        login_id = self.get_account_id(item, login)
        return self._query.execute(
            'SELECT password FROM accounts WHERE id=? AND item_id=?', (login_id, item_id)).fetchone()[0]


def load():
    return DataBase()


def create():
    print('create database')
    db = DataBase().init()
    password = input.enter_new_password()
    salt = crypto.generate_salt()
    key = crypto.Key(password, salt)
    test_token = key.encrypt('this is test token')
    db.set_settings(test_token, salt)


def is_exist():
    try:
        open('database')
        return True
    except:
        return False
