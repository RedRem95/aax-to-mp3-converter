import flask
import os

import app.config as app_config
from app.routes import init_routes
from converter.AaxConverter import conversion_queue_running
from misc import BytesConverter

app = flask.Flask(__name__.split('.')[0],
                  template_folder=os.path.join(os.path.abspath(os.path.dirname(__file__)), "templates"),
                  static_folder=os.path.join(os.path.abspath(os.path.dirname(__file__)), "static"))

app.url_map.converters['bytes'] = BytesConverter

for key, value in app_config.get_flask_config().items():
    app.config[str(key).upper()] = value
if app_config.is_in_session_mode():
    from flask_session import Session
    Session(app)

init_routes(app)


@app.context_processor
def __context():
    return dict(
        name=app_config.get_config_value("NAME"),
        isinstance=isinstance,
        str=str,
        bool=bool,
        queue_running=conversion_queue_running,
        get_session=lambda: flask.session if app_config.is_in_session_mode() else None,
        is_none=lambda x: x is None,
        version=app_config.VERSION
    )
