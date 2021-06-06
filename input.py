import getpass


def enter_new_password():
    return bytearray(input('enter NEW password:'), 'utf-8')


def enter_password():
    return bytearray(getpass.getpass('enter main password:'), 'utf-8')
