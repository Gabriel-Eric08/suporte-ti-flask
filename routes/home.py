from flask import Flask, Blueprint, render_template

home_route=Blueprint('Home',__name__)

@home_route.route('/')
def home_page():
    return render_template('home.html')