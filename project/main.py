from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from .models import User, Calculo
from . import db
from datetime import datetime
import json

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



@main.route('/usuarios/eliminar/<user_id>')
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

@main.route('/historial/eliminar/<calculo_id>')
@login_required
def eliminarHistorial(calculo_id):

    #BORRAR USUARIO
    calculo = Calculo.query.filter_by(id=calculo_id).first_or_404(description='No se encuentra ningún calculo registrado con id {}'.format(calculo_id))
    id_user = calculo.id_usuario
    db.session.delete(calculo)
    db.session.commit()
    flash('Calculo con id "{}" eliminado correctamente'.format(calculo_id), 'warning')
    return redirect(url_for('main.historial', user_id=id_user))


@main.route('/historial/<user_id>')
@login_required
def historial(user_id):
    user = User.query.filter_by(id=user_id).first_or_404(description='No se encuentra ningún usuario registrado con id {}'.format(user_id))
    calculos = Calculo.query.filter_by(id_usuario=user_id).all()
    return render_template('historial.html', usuario=user, calculos=calculos)


@main.route('/vertedero')
def vertedero():
    return render_template('vertedero.html')

@main.route('/vertedero/<calculo_id>')
@login_required
def vertedero_consulta(calculo_id):
    calculo = Calculo.query.filter_by(id=calculo_id).first_or_404(description='No se encuentra ningún calculo registrado con id {}'.format(calculo_id))
    data = json.loads(calculo.data)
    resultados = json.loads(calculo.resultados)
    return render_template('vertedero.html', data=data,resultados=resultados, history=True)

@main.route('/partidor/<calculo_id>')
@login_required
def partidor_consulta(calculo_id):
    calculo = Calculo.query.filter_by(id=calculo_id).first_or_404(description='No se encuentra ningún calculo registrado con id {}'.format(calculo_id))
    data = json.loads(calculo.data)
    resultados = json.loads(calculo.resultados)
    return render_template('partidor.html', data=data,resultados=resultados, history=True)


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
    # TODO: Realizar los calculos
        
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


    if current_user.is_authenticated:
        fecha = datetime.now()
        new_calculo = Calculo(fecha=fecha, id_usuario=current_user.id, tipoEstructura="Vertedero de Cresta Larga", data=json.dumps(data) , resultados=json.dumps(resultados) )
        db.session.add(new_calculo)
        db.session.commit()
    
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
    # TODO: Realizar los calculos 

    resultados = {
        "energia" : "35.000",
        "altura" : "100",
        "anchos" : "53",
        "froude" : "35"
    }

    if current_user.is_authenticated:
        fecha = datetime.now()
        new_calculo = Calculo(fecha=fecha, id_usuario=current_user.id, tipoEstructura="Partidor Proporcional", data=json.dumps(data) , resultados=json.dumps(resultados) )
        db.session.add(new_calculo)
        db.session.commit()

    return render_template('partidor.html', data=data,resultados=resultados)




