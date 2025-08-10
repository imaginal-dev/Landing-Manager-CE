from flask import render_template, flash, redirect, url_for, session, request, current_app
from . import main
from .decorators import login_required
from app.services import nginx_manager

@main.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('logged_in'):
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        token = request.form.get('token')
        if token == current_app.config['APP_TOKEN']:
            session['logged_in'] = True
            session.permanent = True # Make session last for a long time
            flash('You were successfully logged in', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid token', 'danger')
    return render_template('login.html')

@main.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    flash('You were logged out', 'info')
    return redirect(url_for('main.login'))

@main.route('/')
@login_required
def index():
    landings = nginx_manager.get_landings()
    return render_template('index.html', landings=landings)

@main.route('/scan', methods=['POST'])
@login_required
def scan_landings():
    configured_count = nginx_manager.scan_and_create_new_configs()
    if configured_count > 0:
        plural_form = "landing" if configured_count == 1 else "landings"
        flash(f"Found and configured {configured_count} new {plural_form}. They have been added to the table.", 'success')
    else:
        flash("No new landings were found to configure.", 'info')
    return redirect(url_for('main.index'))

@main.route('/landing/<domain>/disable', methods=['POST'])
@login_required
def disable_landing(domain):
    success, message = nginx_manager.toggle_maintenance(domain, enable_maintenance=True)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('main.index'))

@main.route('/landing/<domain>/enable', methods=['POST'])
@login_required
def enable_landing(domain):
    success, message = nginx_manager.toggle_maintenance(domain, enable_maintenance=False)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('main.index'))

