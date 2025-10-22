from flask import Flask, Blueprint
from routes.home import home_route

# Cria a instância do Flask
app = Flask(__name__)

app.register_blueprint(home_route)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)