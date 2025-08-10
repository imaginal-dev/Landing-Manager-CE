import os

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    APP_TOKEN = os.environ.get('APP_TOKEN') or 'default-super-secret-token'
    
    # --- Mail Configuration ---
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.googlemail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_RECIPIENT = os.environ.get('MAIL_RECIPIENT')

    # --- Cloudflare Turnstile Configuration ---
    CLOUDFLARE_SITE_KEY = os.environ.get('CLOUDFLARE_SITE_KEY') # Public key for the widget
    CLOUDFLARE_DEFAULT_SECRET_KEY = os.environ.get('CLOUDFLARE_DEFAULT_SECRET_KEY') # Fallback secret

    # --- Nginx Manager Configuration ---
    # NOTE: These paths are for a standard Linux (Debian/Ubuntu) environment.
    WWW_ROOT = "/var/www"
    NGINX_SITES_AVAILABLE = "/etc/nginx/sites-available"
    NGINX_SITES_ENABLED = "/etc/nginx/sites-enabled"
    NGINX_TEMPLATE_FILE = "provisioning/nginx_template.conf"

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    # In development, we might want to use a local test environment
    BASE_PATH = os.path.join(os.getcwd(), "temp_test_env")
    WWW_ROOT = os.path.join(BASE_PATH, "var", "www")
    NGINX_SITES_AVAILABLE = os.path.join(BASE_PATH, "etc", "nginx", "sites-available")
    NGINX_SITES_ENABLED = os.path.join(BASE_PATH, "etc", "nginx", "sites-enabled")

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
