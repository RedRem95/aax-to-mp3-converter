![Build docker and publish - rcrack](https://github.com/RedRem95/aax-to-mp3-web-converter/workflows/Build%20docker%20and%20publish%20-%20rcrack/badge.svg)
![Build docker and publish - no rcrack](https://github.com/RedRem95/aax-to-mp3-web-converter/workflows/Build%20docker%20and%20publish%20-%20no%20rcrack/badge.svg)
# AAXtoMp3 - Web converter

This project aims to let you easily convert your aax files to mp3.

You should only use this on AAX files you defienetly own. It is not permitted to use it on files you dont own or redistribute copyrighted files

## Getting Started

To get a copy of the source code up and running simply clone the repository and init the [inAudible-NG/tables](https://github.com/inAudible-NG/tables) submodule

### Prerequisites

This Software is written for python3. For import and conversion it uses a recent version of [ffmpeg](https://ffmpeg.org/) and the [inAudible-NG/tables](https://github.com/inAudible-NG/tables) project if you want to try and guess your activation bytes. This is implemented as a submodule but you can also define a different place for either ffmpeg and inAudible-NG/tables using environment variables. 

### Installing

To run a development instance of this project simply execute main.py.

## Deployment

The easiest way to deploy an instance of this software is to use the provided Dockerfile based directly on alpine.

You can also use every wsgi server by directing it to the app:app flask application

## Built With

* [Flask](https://flask.palletsprojects.com) - The web framework used
* [pipenv](https://github.com/pypa/pipenv) - Dependency Management
* [Bootstrap](https://getbootstrap.com) - Used HTML, CSS and JS library
* [jQuery](https://jquery.com/) - Used JS library
* [Bootstrap icons](https://icons.getbootstrap.com) - Used icons
* [Flask-Session](https://github.com/fengsp/flask-session) - Flask plugin to handle sessions. Only used in enabled session mode
* [config-path](https://github.com/barry-scott/config-path) - application to find os-dependant paths for config files
* [inAudible-NG/RainbowCrack-NG](https://github.com/inAudible-NG/RainbowCrack-NG) - Used to try and guess activation bytes

## Versioning

We use [SemVer](http://semver.org/) for versioning. 

## Authors

* **Alexander Vollmer** - *Initial work* - [RedRem95](https://github.com/RedRem95)

## License

This project is licensed under the GPL-3.0 License - see the [LICENSE](LICENSE) file for details

