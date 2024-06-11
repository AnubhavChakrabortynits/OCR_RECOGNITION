from flask import Flask
from views import views

app = Flask(__name__)
app.register_blueprint(views,url_prefix='/views')
app.config['MAX_CONTENT_LENGTH'] = 128 * 1024 * 1024

if __name__ == '__main__':
    app.run(debug=True)