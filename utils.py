import sys
import random
import string
import requests

def get_random_proxy():
    """
    get random proxy from proxypool
    :return: proxy
    """
    return "http://" + requests.get("https://proxypool.scrape.center/random").text.strip()

def sure():
    res = input("Are you sure to pull them? [y/N] ").lower()
    return res == "y"


def random_string(length=16):
    """
    Generate a random string of given length
    """
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(length))