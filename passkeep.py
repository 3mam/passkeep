#!/usr/bin/env python3

import database
import input
import crypto
import argparse
import pyperclip


def arg_edit_password(db: database.DataBase, args):
    main_password = input.enter_password()
    key, password_ok = db.is_password_correct(main_password)
    if password_ok:
        password = crypto.generate_password() if args.generate else input.enter_new_password()
        db.edit_password(args.item, args.login, key.encrypt(password))


def arg_add_login(db: database.DataBase, args):
    if db.create_account(args.item, args.login) == 0:
        return
    arg_edit_password(db, args)


def arg_read_password(db: database.DataBase, args):
    main_password = input.enter_password()
    key, password_ok = db.is_password_correct(main_password)
    if password_ok:
        password = key.encrypt(db.read_password(args.item, args.login)).decode()
        print(f'password is {password}')
        pyperclip.copy(password)


def main():
    db = database.load() if database.is_exist() else database.create()

    parser = argparse.ArgumentParser(
        prog='passkeep', description='passkeep is tool to store and manage passwords')
    parser.add_argument('-a', '--add', action='store_true',
                        help='add item or login to database')
    parser.add_argument('-l', '--login', action='store', type=str,
                        help='login related to item')
    parser.add_argument('-g', '--generate', action='store_true',
                        help='generate password')
    parser.add_argument('-p', '--password', action='store_true',
                        help='edit password')
    parser.add_argument('-r', '--read', action='store_true',
                        help='read password')
    parser.add_argument('-i', '--item', action='store', type=str,
                        help='item name')
    parser.add_argument('-e', '--edit', action='store', type=str,
                        help='edit item or login')
    args = parser.parse_args()
    if args.add:
        if args.login and args.item:
            db.create_item(args.item)
            arg_add_login(db, args)
        elif args.item:
            db.create_item(args.item)
    elif args.add:
        db.create_item(args.add)
    elif args.edit:
        if args.item and args.login:
            db.edit_account(args.item, args.login, args.edit)
        elif args.item:
            db.edit_item(args.item, args.edit)
    elif args.item and args.login and args.password:
        arg_edit_password(db, args)
    elif args.read and args.login and args.item:
        arg_read_password(db, args)
    else:
        print(parser.print_help())


if __name__ == "__main__":
    main()
