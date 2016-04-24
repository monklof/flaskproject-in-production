# coding: utf-8
import logging
from flask import render_template, g
from base import AddStaticFileHashFlask
from auth import auth, login_manager, flask_login
app = AddStaticFileHashFlask(__name__)
# TODO secret_key in the configuration file
app.secret_key = 'the secret key :)'
login_manager.init_app(app)
app.register_blueprint(auth)

from api import api
app.register_blueprint(api, url_prefix="/api/v1")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/home")
@flask_login.login_required
def home():
    return render_template("home.html")

@app.route("/test")
def test():
    logging.info('test')
    raise Exception('test crash log')

if __name__ == "__main__":
    """TODO支持按照debug模式自动切换配置"""
    app.run(debug=True, host="0.0.0.0")
    
