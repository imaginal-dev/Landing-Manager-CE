import os
import shutil
from flask import current_app

class Landing:
    """Represents a single landing page."""
    def __init__(self, domain, www_root, sites_available, sites_enabled):
        self.domain = domain
        self.path = os.path.join(www_root, domain)
        self.index_path = os.path.join(self.path, "index.html")
        self.index_bak_path = os.path.join(self.path, "index.html.bak")
        self.nginx_conf_path = os.path.join(sites_available, domain)
        self.nginx_symlink_path = os.path.join(sites_enabled, domain)

    @property
    def status(self):
        """Determines the status of the landing."""
        if not os.path.exists(self.path):
            return "Not Found"
        if os.path.exists(self.index_bak_path):
            return "Maintenance"
        if os.path.exists(self.nginx_conf_path) and os.path.lexists(self.nginx_symlink_path):
            return "Active"
        if os.path.exists(self.nginx_conf_path):
            return "Configured (Inactive)"
        return "Discovered"

def get_landings():
    """Get a list of all landings and their statuses."""
    cfg = current_app.config
    logger = current_app.logger
    
    landings = []
    try:
        domains = [d for d in os.listdir(cfg['WWW_ROOT']) if os.path.isdir(os.path.join(cfg['WWW_ROOT'], d))]
        for domain in domains:
            landings.append(Landing(domain, cfg['WWW_ROOT'], cfg['NGINX_SITES_AVAILABLE'], cfg['NGINX_SITES_ENABLED']))
    except FileNotFoundError:
        logger.error(f"WWW_ROOT directory not found at {cfg['WWW_ROOT']}")
    return landings

def scan_and_create_new_configs():
    """
    Scans for new landings and creates Nginx configs for them.
    Returns the number of newly configured sites.
    """
    logger = current_app.logger
    cfg = current_app.config

    # --- For development, setup a test environment ---
    if cfg['DEBUG']:
        setup_test_environment()

    try:
        with open(cfg['NGINX_TEMPLATE_FILE'], 'r') as f:
            template_content = f.read()
    except FileNotFoundError:
        logger.error(f"Nginx template file not found at '{cfg['NGINX_TEMPLATE_FILE']}'")
        return 0

    landings = get_landings()
    sites_configured = []

    for landing in landings:
        if landing.status == "Discovered" and os.path.exists(landing.index_path):
            logger.info(f"New landing found: '{landing.domain}'. Configuring Nginx.")
            
            config_content = template_content.replace("{{DOMAIN}}", landing.domain)
            if cfg['DEBUG']:
                 config_content = config_content.replace(f"/var/www/{landing.domain}", landing.path)

            try:
                with open(landing.nginx_conf_path, 'w') as f:
                    f.write(config_content)
                logger.info(f"Created Nginx config for {landing.domain}")

                os.symlink(landing.nginx_conf_path, landing.nginx_symlink_path)
                logger.info(f"Enabled site for {landing.domain} via symlink.")
                
                sites_configured.append(landing.domain)
            except Exception as e:
                logger.error(f"Failed to configure '{landing.domain}': {e}")

    if sites_configured:
        logger.info(f"Configuration complete for: {', '.join(sites_configured)}")
    else:
        logger.info("No new sites to configure.")
    
    return len(sites_configured)

def toggle_maintenance(domain, enable_maintenance):
    """Enables or disables maintenance mode for a landing."""
    cfg = current_app.config
    logger = current_app.logger
    landing = Landing(domain, cfg['WWW_ROOT'], cfg['NGINX_SITES_AVAILABLE'], cfg['NGINX_SITES_ENABLED'])

    if not os.path.exists(landing.path):
        logger.error(f"Attempted to toggle maintenance for non-existent domain: {domain}")
        return False, f"Domain '{domain}' not found."

    if enable_maintenance:
        if landing.status == "Maintenance":
            return True, "Already in maintenance mode."
        # Rename index.html to index.html.bak
        shutil.move(landing.index_path, landing.index_bak_path)
        # Copy maintenance page
        shutil.copyfile('app/templates/maintenance.html', landing.index_path)
        logger.info(f"Enabled maintenance mode for {domain}")
        return True, f"Maintenance mode enabled for {domain}."
    else: # Disable maintenance
        if landing.status != "Maintenance":
            return True, "Not in maintenance mode."
        # Remove maintenance page and restore backup
        os.remove(landing.index_path)
        shutil.move(landing.index_bak_path, landing.index_path)
        logger.info(f"Disabled maintenance mode for {domain}")
        return True, f"Maintenance mode disabled for {domain}."

def setup_test_environment():
    """Creates dummy directories and a landing for testing."""
    cfg = current_app.config
    logger = current_app.logger
    logger.info("DEBUG mode: Setting up test environment.")
    os.makedirs(cfg['WWW_ROOT'], exist_ok=True)
    os.makedirs(cfg['NGINX_SITES_AVAILABLE'], exist_ok=True)
    os.makedirs(cfg['NGINX_SITES_ENABLED'], exist_ok=True)
    
    # Create a dummy landing page for testing
    dummy_landing_path = os.path.join(cfg['WWW_ROOT'], "example.com")
    os.makedirs(dummy_landing_path, exist_ok=True)
    if not os.path.exists(os.path.join(dummy_landing_path, "index.html")) and not os.path.exists(os.path.join(dummy_landing_path, "index.html.bak")):
        with open(os.path.join(dummy_landing_path, "index.html"), 'w') as f:
            f.write("<h1>Hello from example.com</h1>")
        logger.info("Created dummy landing 'example.com' for testing.")