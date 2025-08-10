import os
import requests
from flask import request, jsonify, current_app
from flask_mail import Message
from . import api
from app import mail

def get_turnstile_secret_key(domain):
    """
    Gets the Turnstile secret key for a given domain using the hybrid approach.
    1. Look for a domain-specific key: CF_SECRET_{DOMAIN_NAME}
    2. Fall back to the default key: CLOUDFLARE_DEFAULT_SECRET_KEY
    """
    # Sanitize domain to create a valid env var name (e.g., example.com -> EXAMPLE_COM)
    sanitized_domain = domain.replace('.', '_').replace('-', '_').upper()
    specific_key_name = f"CF_SECRET_{sanitized_domain}"
    
    secret_key = os.environ.get(specific_key_name)
    if secret_key:
        current_app.logger.info(f"Using specific Turnstile secret for domain '{specific_key_name}'")
        return secret_key
    
    default_key = current_app.config.get('CLOUDFLARE_DEFAULT_SECRET_KEY')
    if default_key:
        current_app.logger.info(f"Using default Turnstile secret for domain '{domain}'")
        return default_key
        
    return None

def verify_turnstile(token, secret_key, remote_ip):
    """Verifies the Cloudflare Turnstile token."""
    if not token:
        return False, "Captcha token is missing."
    if not secret_key:
        return False, "Captcha secret key is not configured on the server."

    try:
        response = requests.post(
            'https://challenges.cloudflare.com/turnstile/v0/siteverify',
            data={
                'secret': secret_key,
                'response': token,
                'remoteip': remote_ip,
            }
        )
        response.raise_for_status()
        result = response.json()
        if result.get('success'):
            return True, "Captcha verified."
        else:
            error_codes = ', '.join(result.get('error-codes', []))
            return False, f"Captcha verification failed: {error_codes}"
    except requests.RequestException as e:
        current_app.logger.error(f"Could not contact Cloudflare for Turnstile verification: {e}")
        return False, "Could not verify captcha. Please try again later."


@api.route('/submit/<string:domain>', methods=['POST'])
def submit_form(domain):
    logger = current_app.logger
    data = request.form
    
    # --- 1. Verify Captcha ---

    if data.get('captcha_load_error') == 'true':
        logger.warning(f"Captcha load error for {domain}. Skipping verification.")
    
    else:
        turnstile_token = data.get('cf-turnstile-response')
        secret_key = get_turnstile_secret_key(domain)
        remote_ip = request.remote_addr
        is_valid, message = verify_turnstile(turnstile_token, secret_key, remote_ip)
        if not is_valid:
            logger.warning(f"Captcha failed for {domain}: {message}")
            
            # return jsonify({'success': False, 'message': message}), 400

    # --- 2. Extract Form Data ---
    name = data.get('name')
    email = data.get('email')
    message_body = data.get('message')

    if not all([name, email, message_body]):
        return jsonify({'success': False, 'message': 'Missing form data. Please fill out all fields.'}), 400

    # --- 3. Send Email ---
    recipient = current_app.config.get('MAIL_RECIPIENT')
    sender = current_app.config.get('MAIL_USERNAME')
    if not recipient:
        logger.error("MAIL_RECIPIENT is not configured. Cannot send email.")
        return jsonify({'success': False, 'message': 'Server error: Mail recipient not configured.'}), 500

    msg = Message(
        subject=f"New Form Submission from {domain}",
        sender=sender,
        recipients=[recipient]
    )
    msg.body = f"""
    You have a new message from your landing page '{domain}'.

    Name: {name}
    Email: {email}

    Message:
    {message_body}
    """
    try:
        mail.send(msg)
        logger.info(f"Sent form submission email from {domain} to {recipient}")
        return jsonify({'success': True, 'message': 'Thank you for your message! We will get back to you soon.'})
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return jsonify({'success': False, 'message': 'An error occurred while sending your message. Please try again.'}), 500


@api.route('/logs', methods=['GET'])
def get_logs():
    """Reads the last 200 lines from the log file."""
    log_file_path = os.path.join(current_app.root_path, '..', 'logs', 'landings_manager.log')
    if not os.path.exists(log_file_path):
        return "Log file not found.", 404
    
    try:
        with open(log_file_path, 'r') as f:
            # Read all lines and return the last 200
            lines = f.readlines()
            last_lines = lines[-200:]
            return "".join(last_lines), 200, {'Content-Type': 'text/plain; charset=utf-8'}
    except Exception as e:
        current_app.logger.error(f"Could not read log file: {e}")
        return "Error reading log file.", 500
