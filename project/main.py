from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from .models import User
from . import db

main = Blueprint('main', __name__)

@main.route('/inicio')
def index():
    return render_template('index.html')

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)


@main.route('/admin')
@login_required
def admin():
    users = User.query.order_by(User.id).all()
    return render_template('admin.html', isAdmin=current_user.isAdmin, usuarios=users)



@main.route('/eliminar/<user_id>')
@login_required
def eliminarUsuario(user_id):

    if not current_user.isAdmin:
        return render_template('admin.html', isAdmin=current_user.isAdmin, usuarios=[])
    #BORRAR USUARIO
    user = User.query.filter_by(id=user_id).first_or_404(description='No se encuentra ningún usuario registrado con id {}'.format(user_id))
    db.session.delete(user)
    db.session.commit()
    flash('Usuario "{}" eliminado correctamente'.format(user.name), 'warning')
    return redirect(url_for('main.admin'))

@main.route('/historial/<user_id>')
@login_required
def historial(user_id):
    user = User.query.filter_by(id=user_id).first_or_404(description='No se encuentra ningún usuario registrado con id {}'.format(user_id))

    return render_template('historial.html', usuario=user)


@main.route('/vertedero')
def vertedero():
    return render_template('vertedero.html')


@main.route('/vertedero', methods=['POST'])
def vertedero_post():
    data = {
        "caudalMax" : request.form.get("caudalMax"),
        "caudalDis" : request.form.get("caudalDis"),
        "pendiente" : request.form.get("pendiente"),
        "base" : request.form.get("base"),
        "rugosidad" : request.form.get("rugosidad"),
        "talud" : request.form.get("talud"),
        "altura" : request.form.get("altura"),
    }
    # TODO: Realizar los calculos y retornarlos.

    resultados = {
        "longitud" : "25",
        "angulo" : "25",
        "ancho" : "25",
        "anchoEntrada" : "25",
        "tirante" : "25",
        "tiranteNormal" : "25",
        "alturaVer" : "25",
        "alturaAgua" : "25",
    }

    return render_template('vertedero.html', data=data,resultados=resultados)


@main.route('/partidor')
def partidor():
    return render_template('partidor.html')


@main.route('/partidor', methods=['POST'])
def partidor_post():
    data = {
        "caudal" : request.form.get("caudal"),
        "tiranteEstruct" : request.form.get("tiranteEstruct"),
        "solera" : request.form.get("solera"),
        "talud" : request.form.get("talud"),
        "rugosidad" : request.form.get("rugosidad"),
        "ancho" : request.form.get("ancho"),
        "cotaPartidor" : request.form.get("cotaPartidor"),
        "caudal1" : request.form.get("caudal1"),
        "tiranteAgua" : request.form.get("tiranteAgua"),
        "cotaAgua" : request.form.get("cotaAgua"),
        "caudal2" : request.form.get("caudal2"),
        "tiranteCanal" : request.form.get("tiranteCanal"),
        "cotaCanal" : request.form.get("cotaCanal"),
    }
    # TODO: Realizar los calculos y retornarlos.

    resultados = {
        "energia" : "35.000",
        "altura" : "100",
        "anchos" : "53",
        "froude" : "35"
    }
    return render_template('partidor.html', data=data,resultados=resultados)




