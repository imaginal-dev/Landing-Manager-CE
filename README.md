# Landings Manager

A Flask application to manage static landing pages on a server with Nginx. It includes a web dashboard for monitoring and an API for handling contact form submissions.

## Features

- **Web Dashboard:** A simple, token-protected dashboard to view the status of all landing pages.
- **Auto-Discovery:** Automatically scans the web root directory `/var/www` to find new landing pages.
- **Nginx Configuration:** Generates Nginx configuration files for newly discovered landings.
- **Maintenance Mode:** Allows enabling/disabling a maintenance page for any landing with a single click.
- **Secure Form API:** Provides a API endpoint to handle contact form submissions from any landing.
- **Captcha Protection:** Secures the form API using Cloudflare Turnstile to prevent spam.
- **Production-Ready:** Includes templates for `systemd` and `nginx` for easy deployment.

---

## Production Deployment Instructions

These instructions guide you through deploying the Landings Manager on a standard Linux server (e.g., Ubuntu/Debian).

### Prerequisites

- A server with `git`, `python` (3.8+), `uv`, and `nginx` installed.
- A dedicated non-root user to run the application (e.g., `{username}`).

### Step 1: Clone the Repository

Clone the project to your server, typically in the home directory of your dedicated user.

```bash
git clone https://github.com/namvera/Landings-Manager-CE.git
cd Landings-Manager-CE
```

### Step 2: Set Up Python Environment

Create a virtual environment and install the required dependencies using `uv`.

```bash
uv venv
uv sync
```

### Step 3: Configure Environment Variables

Copy the example `.env` file and fill in your actual secrets and configuration.

```bash
cp provisioning/.env.example .env
nano .env
```
**This is a critical step.** You must fill in all the required variables, especially for `SECRET_KEY`, `APP_TOKEN`, `MAIL_*`, and `CLOUDFLARE_*`.

### Step 4: Configure and Install the Systemd Service

This service will ensure your application runs in the background and restarts automatically.

1.  **Set Permissions:** Ensure the user you'll run the service as owns the project directory.
    ```bash
    # Example:
    sudo chown -R {username}:{username} /home/{username}/Landings-Manager-CE
    ```

2.  **Configure the Service File:** Open the `provisioning/landings-manager.service.template` file and replace the placeholders (`{{USER}}`, `{{GROUP}}`, `{{PROJECT_PATH}}`, `{{SOCKET_PATH}}`) with your actual values.

    *   `{{USER}}`: `{username}`
    *   `{{GROUP}}`: `{username}`
    *   `{{PROJECT_PATH}}`: `/home/{username}/Landings-Manager-CE` (absolute path)
    *   `{{SOCKET_PATH}}`: `/home/{username}/Landings-Manager-CE/landings.sock`

3.  **A Note on the Socket File:** You **do not** need to create the socket file yourself. The `ExecStart` command in the service file tells Gunicorn to create and bind to this file. The service will fail to start if the `{{USER}}` does not have permission to write to this location.

4.  **Install the Service:** Copy your configured file to the systemd directory.
    ```bash
    # Assuming you saved your configured template as 'landings-manager.service'
    sudo cp landings-manager.service /etc/systemd/system/
    ```

### Step 5: Configure Nginx

For each landing page you host, you need to create an Nginx configuration file.

1.  **Configure the Template:** Open `provisioning/nginx_template.conf` and replace `{{DOMAIN}}` with your landing page's domain and `{{SOCKET_PATH}}` with the same socket path you used in the `systemd` service file.

2.  **Create the Nginx Config:** Save the configured content to a new file in `sites-available`.
    ```bash
    # Example for 'example.com'
    sudo nano /etc/nginx/sites-available/example.com.conf
    ```

3.  **Enable the Site:** Create a symbolic link to `sites-enabled`.
    ```bash
    sudo ln -s /etc/nginx/sites-available/example.com.conf /etc/nginx/sites-enabled/
    ```

### Step 6: Go Live!

Now, start the services.

1.  **Reload Systemd:**
    ```bash
    sudo systemctl daemon-reload
    ```
2.  **Start and Enable Your App:**
    ```bash
    sudo systemctl start landings-manager
    sudo systemctl enable landings-manager
    ```
3.  **Restart Nginx:**
    ```bash
    sudo systemctl restart nginx
    ```

### Step 7: Verify

Check that everything is running correctly.

```bash
# Check your app's status (should be 'active (running)')
sudo systemctl status landings-manager

# Check Nginx configuration
sudo nginx -t

# Check Nginx status
sudo systemctl status nginx
```

Your Landings Manager dashboard should now be accessible, and the form submission API should be live.
