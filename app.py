from db_config import app, db 

from flask import Flask, Blueprint
from routes.home import home_route
from routes.auth import auth_route
from routes.chamados import chamados_route
from routes.admin_chamados import admin_chamado_route

app.register_blueprint(home_route)
app.register_blueprint(auth_route, url_prefix='/auth')
app.register_blueprint(chamados_route, url_prefix='/chamados')
app.register_blueprint(admin_chamado_route,url_prefix='/admin')
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)