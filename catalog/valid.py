import re


def phone(string):
    return len(re.findall(r'\d', string)) >= 11


def email(string):
    return bool(re.search(r'^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$', string, re.I))
