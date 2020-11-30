import argparse

if __name__ == '__main__':
    main_parser = argparse.ArgumentParser(prog='AAXtoMP3')
    subparsers = main_parser.add_subparsers(help='Modes this program can start as', required=True, title="Start modes")
    web_interface = subparsers.add_parser("interface", help="Use the webinterface [Currently disabled]")
    auto_watcher = subparsers.add_parser("auto", help="Start watch on a folder and convert every item inside. "
                                                      "Deletes after conversion")

    main_parser.add_argument("-d", "--debug", dest="debug", action='store_true',
                             help="Set the port for the webinterface")

    web_interface.add_argument("-p", "--port", dest="webui_port", type=int, required=True,
                               help="Set the port for the webinterface")

    auto_watcher.add_argument("-w", "--watch", dest="watch_orig", type=str, required=True,
                              help="Set path to watch and get files from")
    auto_watcher.add_argument("-t", "--target", dest="watch_dest", type=str, required=True,
                              help="Set path to save the converted files to")

    args = main_parser.parse_args()

    try:
        watch_folder = args.watch_orig
        destination_folder = args.watch_dest
        from watchapp import app
        app.run(watch_folder=watch_folder, destination_folder=destination_folder, debug=args.debug)
    except AttributeError as e:
        print("Web interface is currently disabled")
        exit(1)
        from webapp import app, config as app_config
        if args.debug:
            app_config.set_config_value("DEBUG", args.debug)
        app.run(port=args.webui_port, debug=app_config.get_config_value("DEBUG"))
