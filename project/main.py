from datetime import datetime
import json

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user

from .models import User, Calculo
from . import db
from .calculos.vertedero import (
    DisVertedero,
    Cotas,
    parametrosTrap,
    parametrosRect,
    y2_DesnivelTrap,
    y2_Desnivelrec
)

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
    # BORRAR USUARIO
    user = User.query.filter_by(id=user_id).first_or_404(
        description='No se encuentra ningún usuario registrado con id {}'.format(user_id))
    db.session.delete(user)
    db.session.commit()
    flash('Usuario "{}" eliminado correctamente'.format(user.name), 'warning')
    return redirect(url_for('main.admin'))


@main.route('/historial/eliminar/<calculo_id>')
@login_required
def eliminarHistorial(calculo_id):

    calculo = Calculo.query.filter_by(id=calculo_id).first_or_404(
        description='No se encuentra ningún calculo registrado con id {}'.format(calculo_id))
    id_user = calculo.id_usuario
    db.session.delete(calculo)
    db.session.commit()
    flash('Calculo con id "{}" eliminado correctamente'.format(calculo_id), 'warning')
    return redirect(url_for('main.historial', user_id=id_user))


@main.route('/historial/<user_id>')
@login_required
def historial(user_id):
    user = User.query.filter_by(id=user_id).first_or_404(
        description='No se encuentra ningún usuario registrado con id {}'.format(user_id))
    calculos = Calculo.query.filter_by(id_usuario=user_id).all()
    return render_template('historial.html', usuario=user, calculos=calculos)


@main.route('/vertedero')
def vertedero():
    return render_template('vertedero.html')


@main.route('/vertedero/<calculo_id>')
@login_required
def vertedero_consulta(calculo_id):
    calculo = Calculo.query.filter_by(id=calculo_id).first_or_404(
        description='No se encuentra ningún calculo registrado con id {}'.format(calculo_id))
    data = json.loads(calculo.data)
    resultados = json.loads(calculo.resultados)
    return render_template('vertedero.html', data=data, resultados=resultados, history=True)


@main.route('/partidor/<calculo_id>')
@login_required
def partidor_consulta(calculo_id):
    calculo = Calculo.query.filter_by(id=calculo_id).first_or_404(
        description='No se encuentra ningún calculo registrado con id {}'.format(calculo_id))
    data = json.loads(calculo.data)
    resultados = json.loads(calculo.resultados)
    return render_template('partidor.html', data=data, resultados=resultados, history=True)


@main.route('/vertedero', methods=['POST'])
def vertedero_post():
    data = {
        "tipo": request.form.get("tipo"),
        "caudalDis": float(request.form.get("caudalDis")),
        "base": float(request.form.get("base")),
        "talud": float(request.form.get("talud")),
        "rugosidad": float(request.form.get("rugosidad")),
        "pendiente": float(request.form.get("pendiente")),
        "alturaMuro": float(request.form.get("alturaMuro")),
        "cotaA": float(request.form.get("cotaA")),
        "carga": float(request.form.get("carga")),
    }

    if data['tipo'] == "rectangular":
        valorTirante = parametrosRect(data['caudalDis'],data['rugosidad'],data['pendiente'],data['base'],data['alturaMuro'])
    else:
        valorTirante=parametrosTrap(data['caudalDis'],data['rugosidad'],data['pendiente'],data['base'],data['talud'],data['alturaMuro'])
    
    valoresDisVertedero = DisVertedero(valorTirante[0],data['carga'], data['caudalDis'], data['base'], data['talud'])
    valoresCotas= Cotas(data['cotaA'],data['carga'], valoresDisVertedero[1])

    if  data['tipo'] == "rectangular": 
        valores_y2_Desnivel=y2_Desnivelrec(valoresDisVertedero[0], data['rugosidad'],data['pendiente'],data['base'],valorTirante[0],data['caudalDis'],data['carga'])
    else:
        valores_y2_Desnivel= y2_DesnivelTrap(valoresDisVertedero[0], data['rugosidad'],data['pendiente'],data['base'],data['talud'],valorTirante[0],data['caudalDis'],data['carga'])
    
    resultados = {
        "tirante_normal": valorTirante[0],
        "tirante_critico": valorTirante[4],
        "velocidad": valorTirante[1],
        "borde_libre": valorTirante[2],
        "froude": valorTirante[3],
        "energia": valores_y2_Desnivel[1],
        "angulo": valoresDisVertedero[5],
        "altura": valoresDisVertedero[0],
        "ancho": valoresDisVertedero[1],
        "tirante_final": valores_y2_Desnivel[0],
        "longitud_total": valoresDisVertedero[2],
        "longitud_1": valoresDisVertedero[3],
        "longitud_2": 0.4,#Fijo
        "longitud_3": abs(valoresDisVertedero[4]),
        "desnivel": valores_y2_Desnivel[2],
        "caudal": valoresDisVertedero[6],
        "velocidad_vertedero": valoresDisVertedero[7],
        "cotaA": valoresCotas[0],
        "cotaB": valoresCotas[1],
        "cotaC": valoresCotas[2],
        "cotaD": valoresCotas[3],
    }

    if current_user.is_authenticated:
        fecha = datetime.now()
        new_calculo = Calculo(fecha=fecha, id_usuario=current_user.id, tipoEstructura="Vertedero de Cresta Larga", data=json.dumps(
            data), resultados=json.dumps(resultados))
        db.session.add(new_calculo)
        db.session.commit()

    return render_template('vertedero.html', data=data, resultados=resultados)


@main.route('/partidor')
def partidor():
    return render_template('partidor.html')


@main.route('/partidor', methods=['POST'])
def partidor_post():
    data = {
        "caudal": request.form.get("caudal"),
        "tiranteEstruct": request.form.get("tiranteEstruct"),
        "solera": request.form.get("solera"),
        "talud": request.form.get("talud"),
        "rugosidad": request.form.get("rugosidad"),
        "ancho": request.form.get("ancho"),
        "cotaPartidor": request.form.get("cotaPartidor"),
        "caudal1": request.form.get("caudal1"),
        "tiranteAgua": request.form.get("tiranteAgua"),
        "cotaAgua": request.form.get("cotaAgua"),
        "caudal2": request.form.get("caudal2"),
        "tiranteCanal": request.form.get("tiranteCanal"),
        "cotaCanal": request.form.get("cotaCanal"),
    }
    # TODO: Realizar los calculos

    resultados = {
        "energia": "35.000",
        "altura": "100",
        "anchos": "53",
        "froude": "35"
    }

    if current_user.is_authenticated:
        fecha = datetime.now()
        new_calculo = Calculo(fecha=fecha, id_usuario=current_user.id, tipoEstructura="Partidor Proporcional", data=json.dumps(
            data), resultados=json.dumps(resultados))
        db.session.add(new_calculo)
        db.session.commit()

    return render_template('partidor.html', data=data, resultados=resultados)
