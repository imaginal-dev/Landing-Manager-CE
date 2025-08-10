import os
from app import create_app

# FLASK_CONFIG is an environment variable that can be set to specify the configuration
app = create_app(os.getenv('FLASK_CONFIG') or 'default')

if __name__ == '__main__':
    app.run()
