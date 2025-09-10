'''
This is the entry point of the Flask application.

It creates an instance of the application and runs it.

@author Emmanuel Olowu
@link: https://github.com/zeddyemy
'''
from app import create_app

flask_app = create_app()

if __name__ == "__main__":
    # For local development
    flask_app.run(host="0.0.0.0", port=5000, debug=flask_app.config.get("DEBUG", True))