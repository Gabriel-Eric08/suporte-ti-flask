from db_config import app, db 

from flask import Flask, Blueprint
from routes.home import home_route
from routes.auth import auth_route
from routes.chamados import chamados_route
from routes.admin_chamados import admin_chamado_route
from routes.client_page import cliente_route
from routes.user import user_route

app.register_blueprint(auth_route)
app.register_blueprint(home_route, url_prefix='/home')
app.register_blueprint(chamados_route, url_prefix='/chamados')
app.register_blueprint(admin_chamado_route,url_prefix='/admin')
app.register_blueprint(cliente_route,url_prefix='/cliente')
app.register_blueprint(user_route, url_prefix='/usuario')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)