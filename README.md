# AAXtoMp3 - converter

This project aims to let you easily convert your aax files to mp3.

You should only use this on AAX files you definitely own. It is not permitted to use it on files you dont own or redistribute copyrighted files

## Getting Started

To run this software simply clone the repository and run the main.py file with the -h option to see the currently available options.

The simples way to run it is by using docker. Simply use ``docker run redrem/aax-to-mp3-converter:latest -h`` to see options.

If you want to run it natively use the provided [Pipfile](Pipfile) and [pipenv](https://pipenv.pypa.io/en/latest/) to create a python environment with all dependencies.
Additionally you need a recent installation of [ffmpeg](https://ffmpeg.org/) and [inAudible-NG/tables](https://github.com/inAudible-NG/tables) or [inAudible-NG/RainbowCrack-NG](https://github.com/inAudible-NG/RainbowCrack-NG)

* ffmpeg: Either make ffmpeg and ffprobe accessible from ``PATH`` or set  ``AC_FFMPEG`` and ``AC_FFPROBE`` environment variables to the corresponding executables
* inAudible-NG: Set environment variable ``AC_RCRACK`` to the root path the selected inAudible-NG project. This should contain the rcrack executable and the *.rt or *.rtc files 

### Notifications

Some modes support notifications. If so, use --notification to setup urls to send to. See [url-reference](https://github.com/caronc/apprise#supported-notifications) to see what urls and services are supported.

### Watch-Mode

Use watch to select the watch mode.

Here you can select a watch and a target folder. The program will automatically select every *.aax and *.mp3 file in this folder.
Then if it is a *.aax file convert it to mp3 and copy it inside the target folder in a predefined folder structure.
The structure is ``<artist>/<album>/<title>.mp3`` per default. If the conversion and copy succeeded the original file in the watch folder will be deleted.
Also a cover will be saved in the same directory.

##### Example

``` shell script
docker run redrem/aax-to-mp3-converter:latest watch -w /path/to/input -t /path/to/output
```

### Owncloud-Mode

Use owncloud to select owncloud mode.

Here you can select a watch and a target folder inside your owncloud instance. The program will automatically select every *.aax and *.mp3 file in this folder and download it to convert it.
Then if it is a *.aax file convert it to mp3 and upload it inside the target folder in a predefined folder structure.
The structure is ``<artist>/<album>/<title>.mp3`` per default. If the conversion and copy succeeded the original file in the watch folder will be deleted.
Also a cover will be uploaded in the same directory.

Also you have to define the owncloud-instance, username and password so the script has access to the files.

##### Example

``` shell script
docker run redrem/aax-to-mp3-converter:latest owncloud -w /path/to/input -t /path/to/output -u username -p password  -host owncloud.yourdomain.com
```

## Built With

* [pipenv](https://github.com/pypa/pipenv) - Dependency Management
* [inAudible-NG/tables](https://github.com/inAudible-NG/tables.git) or [inAudible-NG/RainbowCrack-NG](https://github.com/inAudible-NG/RainbowCrack-NG) - Used to try and guess activation bytes
* [pyocclient](https://github.com/owncloud/pyocclient) - Used to connect to owncloud if that's wanted
* [apprise](https://github.com/caronc/apprise) - Used to send notifications

## Versioning

We use [SemVer](http://semver.org/) for versioning. 

## Authors

* **Alexander Vollmer** - *Initial work* - [RedRem95](https://github.com/RedRem95)

## License

This project is licensed under the GPL-3.0 License  - see the [LICENSE](LICENSE) file for details

