import flask
import json

from converter.AaxConverter import add_audiobook_to_queue, conversion_queue_running
from converter.ffmpeg import get_audiobook_file as gaf, generate_bytes_by_id, use_for_all_for_id, get_audiobook_by_id
from app.config import get_editable_config, get_upload_name, is_in_session_mode, \
    get_potential_audio_book_files as gpabf, set_config_value, save_file_config, get_config_descriptive_name, \
    get_config_descriptions
from misc.software import get_used_software


def init_routes(app: flask.app.Flask):
    @app.route("/")
    @app.route("/index")
    @app.route("/index.html")
    def home():
        return flask.render_template("index.html",
                                     audiobooks=[gaf(x) for x in gpabf(flask.session if is_in_session_mode() else None)])

    @app.route("/about")
    @app.route("/about.html")
    def about():
        return flask.render_template("about.html", softwares=get_used_software())

    @app.route("/settings", methods=['GET'])
    @app.route("/settings.html", methods=['GET'])
    def settings():
        return flask.render_template("settings.html",
                                     settings=get_editable_config(),
                                     get_config_descriptive_name=get_config_descriptive_name,
                                     get_config_descriptions=get_config_descriptions)

    @app.route("/settings", methods=['POST'])
    @app.route("/settings.html", methods=['POST'])
    def settings_post():
        form_data = flask.request.form
        for setting_name, setting_value_old in get_editable_config().items():
            if isinstance(setting_value_old, bool):
                settings_value_new = form_data.get(f"input_{setting_name}") is not None
            else:
                settings_value_new = str(form_data.get(f"input_{setting_name}"))
            set_config_value(setting_name, settings_value_new)
            print(f"Changing setting {setting_name} from {setting_value_old} to {settings_value_new}")
        save_file_config()
        return flask.render_template("settings.html",
                                     settings=get_editable_config(),
                                     get_config_descriptive_name=get_config_descriptive_name,
                                     get_config_descriptions=get_config_descriptions)

    @app.route("/upload", methods=['POST'])
    def upload_post():
        uploaded_files = flask.request.files.getlist("file[]")
        for file in uploaded_files:
            file.save(get_upload_name(flask.session if is_in_session_mode() else None))
        return flask.redirect("/", code=302)

    @app.route("/upload", methods=['GET'])
    def upload_get():
        return flask.render_template("upload.html")

    @app.route("/generate/activation/<string:audiobook_id>")
    def generate_activation_bytes(audiobook_id: str):
        generate_bytes_by_id(audiobook_id)
        return flask.redirect("/", code=302)

    @app.route("/generate/useforall/<string:audiobook_id>")
    def use_for_all(audiobook_id: str):
        use_for_all_for_id(audiobook_id)
        return flask.redirect("/", code=302)

    @app.route("/run/<string:audiobook_id>")
    def run_by_id(audiobook_id: str):
        session = flask.session if is_in_session_mode() else None
        ab = get_audiobook_by_id(audiobook_id, session)
        add_audiobook_to_queue(ab, session)
        return flask.redirect("/", code=302)

    @app.route("/run", methods=["GET"])
    def run_get():
        return flask.redirect("/", code=301)

    @app.route("/run", methods=["POST"])
    def run_post():
        form_data = flask.request.form
        for ab in (gaf(x) for x in gpabf(flask.session if is_in_session_mode() else None)):
            if form_data.get(f"convert_{ab.get_id()}"):
                ab.set_activation_bytes(form_data.get(f"activationbytes_{ab.get_id()}"))
                add_audiobook_to_queue(ab)
        return flask.redirect("/", code=302)

    @app.route("/cover/<string:audiobook_id>")
    def cover(audiobook_id: str):
        ab = get_audiobook_by_id(audiobook_id, flask.session if is_in_session_mode() else None)
        if ab:
            cover_file = ab.get_cover()
            if cover_file:
                return flask.send_file(cover_file)
            return f"No cover for {ab}"
        return "No cover"

    @app.route("/queue/status")
    def queue_status():
        if flask.request.args.get("simple") is not None:
            return "1" if conversion_queue_running() else "0"
        return "Queue working" if conversion_queue_running() else "Queue empty"

    @app.route("/download/<string:audiobook_id>")
    def download(audiobook_id: str):
        session = flask.session if is_in_session_mode() else None
        ab = get_audiobook_by_id(audiobook_id, session)
        if ab.already_converted():
            return flask.send_file(ab.get_whole_target_path(session), as_attachment=True)
        return flask.redirect("/", code=302)

    @app.route("/info/<string:audiobook_id>")
    def get_info(audiobook_id: str):
        session = flask.session if is_in_session_mode() else None
        ab = get_audiobook_by_id(audiobook_id, session)
        if ab:
            return flask.Response(json.dumps(ab.get_info()), content_type="application/json")
        return flask.Response(json.dumps({"Error": "No info"}), content_type="application/json")

    __error_handler = [
        {"error_code": 401,
         "error_name": "Unauthorized",
         "error_message": "Authentication missing for this page."},
        {"error_code": 403,
         "error_name": "Forbidden",
         "error_message": "You are not allowed on this page. Please check your access rights."},
        {"error_code": 404,
         "error_name": "Not Found",
         "error_message": "The page you are looking for does not exist."},
        {"error_code": 410,
         "error_name": "Gone",
         "error_message": "The page you are looking for does not exist anymore."},
        {"error_code": 500,
         "error_name": "Internal Server Error",
         "error_message": "There was an internal error. If you have access please chech the logs and try to fix it!!!"}
    ]

    def create_error_handler(error_info):
        def tmp_error(e):
            return flask.render_template("error/base_error.html", **error_info), error_info["error_code"]
        return tmp_error

    for error in __error_handler:
        app.register_error_handler(error["error_code"], create_error_handler(error))

