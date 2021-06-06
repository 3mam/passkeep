from array import array
from os import error, set_blocking
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

    def is_password_correct(self, password):
        token = self._query.execute(
            'SELECT value FROM settings WHERE name="token"').fetchone()[0]
        salt = self._query.execute(
            'SELECT value FROM settings WHERE name="salt"').fetchone()[0]
        key = crypto.Key(password, salt)
        try:
            decrypt_token = key.decrypt(token).decode('utf-8')
            return decrypt_token == 'this is test token'
        except UnicodeDecodeError:
            return False

    def create_item(self, name):
        try:
            self._query.execute(
                'INSERT INTO items (name) VALUES (?)', (name,))
            self._connect.commit()
            print(f'add {name} to items')
            return self.get_item(name)
        except:
            print(f'{name} exist')
            return -1

    def get_item_id(self, name):
        try:
            return self._query.execute(
                'SELECT id FROM items WHERE name=?', (name,)).fetchone()[0]
        except:
            print(f'item {name} not exist')
            return -1

    def create_account(self, item_name, login, password):
        try:
            item_id = self.create_item(item_name)
            if item_id == -1:
                item_id = self.get_item_id(item_name)
            self._query.execute(
                'INSERT INTO accounts (login, password, item_id) VALUES (?, ?, ?)', (login, password, item_id))
            self._connect.commit()
            print(f'create account {login} in {item_name}')
            return self.get_account_id(item_name, login)
        except:
            print(f'login {login} in item {item_name} exist')
            return -1

    def get_account_id(self, item, login):
        try:
            item_id = self.get_item_id(item)
            return self._query.execute(
                'SELECT id FROM accounts WHERE login=? AND item_id=?', (login, item_id)).fetchone()[0]
        except:
            print(f'login {login} not exist')
            return -1


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
