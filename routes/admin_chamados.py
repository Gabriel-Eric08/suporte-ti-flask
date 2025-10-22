from flask import Blueprint,request,render_template
from models.models import Chamado

admin_chamado_route=Blueprint('Admin_chamados',__name__)

@admin_chamado_route.route('/')
def admin_page():
    chamados = Chamado.query.order_by(Chamado.datetime).all()
    return render_template('admin_page.html', chamados=chamados)