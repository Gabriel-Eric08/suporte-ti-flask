from flask import request


def getUsername():
    username = request.cookies.get('username')
    return username
