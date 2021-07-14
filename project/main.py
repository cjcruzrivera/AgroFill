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
from .calculos.partidor import (
    calculo_partidor,
    partidor_movil
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
        valorTirante = parametrosRect(
            data['caudalDis'], data['rugosidad'], data['pendiente'], data['base'], data['alturaMuro'])
    else:
        valorTirante = parametrosTrap(data['caudalDis'], data['rugosidad'],
                                      data['pendiente'], data['base'], data['talud'], data['alturaMuro'])

    valoresDisVertedero = DisVertedero(
        valorTirante[0], data['carga'], data['caudalDis'], data['base'], data['talud'])
    valoresCotas = Cotas(data['cotaA'], data['carga'], valoresDisVertedero[0])

    if data['tipo'] == "rectangular":
        valores_y2_Desnivel = y2_Desnivelrec(
            valoresDisVertedero[6], data['rugosidad'], data['pendiente'], data['base'], valorTirante[0], data['caudalDis'], data['carga'])
    else:
        valores_y2_Desnivel = y2_DesnivelTrap(
            valoresDisVertedero[6], data['rugosidad'], data['pendiente'], data['base'], data['talud'], valorTirante[0], data['caudalDis'], data['carga'])

    resultados = {
        "tirante_normal": round(valorTirante[0], 3),
        "tirante_critico": round(valorTirante[4], 3),
        "velocidad": round(valorTirante[1], 3),
        "borde_libre": round(valorTirante[2], 3),
        "froude": round(valorTirante[3], 3),
        "energia": round(valores_y2_Desnivel[1], 3),
        "angulo": round(valoresDisVertedero[5], 3),
        "altura": round(valoresDisVertedero[0], 3),
        "ancho": round(valoresDisVertedero[1], 3),
        "tirante_final": round(valores_y2_Desnivel[0], 3),
        "longitud_total": round(valoresDisVertedero[2], 3),
        "longitud_1": round(valoresDisVertedero[3], 3),
        "longitud_2": 0.4,  # Fijo
        "longitud_3": abs(valoresDisVertedero[4]),
        "desnivel": round(valores_y2_Desnivel[2], 3),
        "caudal": round(valoresDisVertedero[6], 3),
        "velocidad_vertedero": round(valoresDisVertedero[7], 3),
        "cotaA": round(valoresCotas[0], 3),
        "cotaB": round(valoresCotas[1], 3),
        "cotaC": round(valoresCotas[2], 3),
        "cotaD": round(valoresCotas[3], 3),
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
        "tipo": request.form.get("tipo"),
        "tipoPart": request.form.get("tipoPart"),
        "caudal_entrante": request.form.get("caudal_entrante"),
        "base_entrante": request.form.get("base_entrante"),
        "tirante_entrante": request.form.get("tirante_entrante"),
        "pendiente": request.form.get("pendiente"),
        "rugosidad": request.form.get("rugosidad"),
        "talud_entrante": request.form.get("talud_entrante") or 0,
        "long_vertedero": request.form.get("base_entrante"),
        "angulo_transicion": request.form.get("angulo_transicion") or 0,
        "cota_a": request.form.get("cota_a"),
        "caudal_pasante": request.form.get("caudal_pasante"),
        "base_pasante": request.form.get("base_pasante"),
        "tirante_pasante": request.form.get("tirante_pasante"),
        "talud_pasante": request.form.get("talud_pasante") or 0,
        "cota_b": request.form.get("cota_b"),
        "caudal_saliente": request.form.get("caudal_saliente"),
        "base_saliente": request.form.get("base_saliente"),
        "tirante_saliente": request.form.get("tirante_saliente"),
        "talud_saliente": request.form.get("talud_saliente") or 0,
        "cota_c": request.form.get("cota_c"),
    }
    print(json.dumps(data, sort_keys=False, indent=4))

    resultado_partidor = calculo_partidor(float(data['caudal_entrante']),
                                          float(data['tirante_entrante']),
                                          float(data['base_entrante']),
                                          float(data['talud_entrante']),
                                          float(data['long_vertedero']),
                                          float(data['rugosidad']),
                                          float(data['cota_a']),
                                          float(data['pendiente']),
                                          float(data['caudal_pasante']),
                                          float(data['tirante_pasante']),
                                          float(data['base_pasante']),
                                          float(data['talud_pasante']),
                                          float(data['caudal_saliente']),
                                          float(data['tirante_saliente']),
                                          float(data['base_saliente']),
                                          float(data['talud_saliente']),
                                          float(data['angulo_transicion']),
                                          float(data['cota_b']),
                                          float(data['cota_c']))

    velocidad_trape = "No aplica"
    energia_trape = "No aplica"
    ycrt_trape = "No aplica"
    ecrt_trape = "No aplica"
    tirante_partidor = "No aplica"
    long_transicion = "No aplica"
    long_transicionp = "No aplica"
    long_transicions = "No aplica"

    if data["tipo"] == "trapezoidal":
        velocidad_trape = resultado_partidor['vel_trape']
        energia_trape = resultado_partidor['ener_trape']
        ycrt_trape = resultado_partidor['tirante_crt']
        ecrt_trape = resultado_partidor['ener_crt']
        tirante_partidor = resultado_partidor['tirante_partidor']
        long_transicion = resultado_partidor['long_transicion1']
        long_transicionp = resultado_partidor['long_transpa']
        long_transicions = resultado_partidor['long_transsa']

    angulo = "No aplica"
    altura_vert = ""
    carga_part = ""
    if data['tipoPart'] == "movil":
        resultado_movil = partidor_movil(float(data['caudal_entrante']),
                                          float(data['tirante_entrante']),
                                          float(data['base_entrante']),
                                          float(data['talud_entrante']),
                                          float(data['long_vertedero']),
                                          float(data['rugosidad']),
                                          float(data['cota_a']),
                                          float(data['pendiente']),
                                          float(data['caudal_pasante']),
                                          float(data['tirante_pasante']),
                                          float(data['base_pasante']),
                                          float(data['talud_pasante']),
                                          float(data['caudal_saliente']),
                                          float(data['tirante_saliente']),
                                          float(data['base_saliente']),
                                          float(data['talud_saliente']),
                                          float(data['angulo_transicion']),
                                          float(data['cota_b']),
                                          float(data['cota_c']))
        angulo = resultado_movil["angulo_final"]
        carga_part = resultado_movil['carga_movil']
    else:
        carga_part = resultado_partidor['carga_hidrau']
    
    altura_vert = resultado_partidor['altura_verte']
    resultados = {
        "velocidad_trape": velocidad_trape,
        "energia_trape": energia_trape,
        "ycrt_trape": ycrt_trape,
        "ecrt_trape": ecrt_trape,
        "tirante_partidor": tirante_partidor,
        "long_transicion": long_transicion,
        "long_transicionp": long_transicionp,
        "long_transicions": long_transicions,
        "velocidad": resultado_partidor['velocidad'],
        "energia_especifica": resultado_partidor['energia_especifica'],
        "tirante_critico": resultado_partidor['tirante_critico'],
        "energia_critica": resultado_partidor['energia_critica'],
        "froude": resultado_partidor['numero_froude'],
        "altura_vertedero": altura_vert,
        "carga_hidraulica": carga_part,
        "angulo_inclinacion": angulo,
        "longitud_lamina": resultado_partidor['long_hoja'],
        "ancho_vertedero": resultado_partidor['ancho_verte'],
        "long_vertedero_max": resultado_partidor['max_vertedero'],
        "Ancho_qpasante": resultado_partidor['long_pasante'],
        "Ancho_qsaliente": resultado_partidor['long_saliente'],
        "prof_colchon": resultado_partidor.get('espesor','0'),
        "long_colchon": resultado_partidor.get('long_colchon', '0'),
        "carga_hidraulicap": resultado_partidor['carga_pasante'],
        "carga_hidraulicas": resultado_partidor['carga_saliente'],
        "cota_3": resultado_partidor.get('cota_3', data['cota_a']),
        "cota_1": resultado_partidor['cota_1'],
        "cota_2": resultado_partidor['cota_2'],
        "cota_4": resultado_partidor['cota_4'],
        "cota_5": resultado_partidor['cota_5'],
    }

    if current_user.is_authenticated:
        fecha = datetime.now()
        new_calculo = Calculo(fecha=fecha, id_usuario=current_user.id, tipoEstructura="Partidor Proporcional", data=json.dumps(
            data), resultados=json.dumps(resultados))
        db.session.add(new_calculo)
        db.session.commit()

    return render_template('partidor.html', data=data, resultados=resultados)
