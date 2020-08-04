from app import app, config as app_config


if __name__ == '__main__':
    app.run(port=8080, debug=app_config.get_config_value("DEBUG"))
