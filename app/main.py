from version import get_version as version
import argparse
from typing import Callable, List
import misc.logging as logging
from misc.logging.notifications import APPRISE_SUPPORTED_FORMATS_URL
from misc import InterruptableRepeatingThread

if __name__ == '__main__':

    main_parser = argparse.ArgumentParser(prog='AAXtoMP3')
    start_mode_parser = main_parser.add_subparsers(help='Modes this program can start as', required=False,
                                                   title="Start modes")
    auto_watcher = start_mode_parser.add_parser("watch", help="Start watch on a folder and convert every item inside. "
                                                              "Deletes after conversion")
    owncloud_watcher = start_mode_parser.add_parser("owncloud",
                                                    help="Start watch on owncloud and convert every item inside. "
                                                         "Deletes after conversion")

    main_parser.add_argument("-v", "--version", dest="show_version", action='store_true', required=False,
                             help="Show current version")
    main_parser.add_argument("-d", "--debug", dest="debug", action='store_true', required=False,
                             help="Set the port for the webinterface")

    _notification_enabled_parser = [auto_watcher, owncloud_watcher]

    for _parser in _notification_enabled_parser:
        _parser.add_argument("--notification", dest="notification_urls", metavar="URL", nargs='*', default=[], type=str,
                             required=False, help=f"Set urls for apprise to send notifications. "
                                                  f"See \"{APPRISE_SUPPORTED_FORMATS_URL}\" for supported urls")

    _scanning_parser = [auto_watcher, owncloud_watcher]
    for _parser in _scanning_parser:
        _parser.add_argument("-i", "--interval", dest="scanning_interval", metavar="INTERVAL", required=False, type=int,
                             help="Set interval to search for new files if none was found")

    default_format = "{artist}/{album}/{title}.mp3"

    auto_watcher.add_argument("-w", "--watch", dest="watch_orig", type=str, required=True,
                              help="Set path to watch and get files from")
    auto_watcher.add_argument("-t", "--target", dest="watch_dest", type=str, required=True,
                              help="Set path to save the converted files to")
    auto_watcher.add_argument("-f", "--format", dest="format", type=str, required=False, default=default_format,
                              help=f"Format for finished files. Default: {default_format}")

    owncloud_watcher.add_argument("-u", "--user", dest="owncloud_username", type=str, required=True,
                                  help="Set username of owncloud user")
    owncloud_watcher.add_argument("-p", "--password", dest="owncloud_password", type=str, required=True,
                                  help="Set password of owncloud user")
    owncloud_watcher.add_argument("-w", "--watch", dest="owncloud_orig", type=str, required=True,
                                  help="Original folder in owncloud")
    owncloud_watcher.add_argument("-t", "--target", dest="owncloud_dest", type=str, required=True,
                                  help="Target folder in owncloud")
    owncloud_watcher.add_argument("-host", "--host", dest="owncloud_host", type=str, required=True,
                                  help=f"Owncloud host url")
    owncloud_watcher.add_argument("-f", "--format", dest="template", type=str, required=False, default=default_format,
                                  help=f"Format for finished files. Default: {default_format}")

    args = main_parser.parse_args()

    if args.show_version:
        print(f"Version: {version()}")
        exit(0)

    if args.debug:
        logging.set_commandline_level(logging.DEBUG_LEVEL)
    else:
        logging.set_commandline_level(logging.INFO_LEVEL)

    try:
        logging.add_notification_url(args.notification_urls)
    except AttributeError:
        pass


    def watch_app_creator(_args: argparse.Namespace) -> InterruptableRepeatingThread:
        _watch_folder = args.watch_orig
        _destination_folder = args.watch_dest
        _interval = args.scanning_interval
        _template = args.template
        from watchapp import WatchingApp

        return WatchingApp(watch_folder=_watch_folder, target_folder=_destination_folder, debug=_args.debug,
                           recursive=False, scanning_interval=_interval, template=_template)


    def owncloud_app_creator(_args: argparse.Namespace) -> InterruptableRepeatingThread:
        _username = args.owncloud_username
        _password = args.owncloud_password
        _watch_folder = args.owncloud_orig
        _destination_folder = args.owncloud_dest
        _host = args.owncloud_host
        _interval = args.scanning_interval
        _template = args.template
        from owncloudapp import OwncloudApp

        return OwncloudApp(watch_folder=_watch_folder, destination_folder=_destination_folder, username=_username,
                           password=_password, host=_host, debug=_args.debug, scanning_interval=_interval,
                           template=_template)


    apps: List[InterruptableRepeatingThread] = []
    for _creator in [watch_app_creator, owncloud_app_creator]:
        _creator: Callable[[argparse.Namespace], InterruptableRepeatingThread]
        try:
            apps.append(_creator(args))
        except AttributeError:
            pass

    if len(apps) > 0:
        for _app in apps:
            _app.run()
        try:
            for _app in apps:
                _app.join()
        except KeyboardInterrupt:
            for _app in apps:
                _app.interrupt()
                _app.join()
