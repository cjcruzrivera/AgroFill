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


@main.route('/vertedero')
def vertedero():
    return render_template('vertedero.html')


@main.route('/partidor')
def partidor():
    return render_template('partidor.html')

