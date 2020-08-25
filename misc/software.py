from typing import Set, List, Dict, Optional

used_software: "Set[__Software]" = set()


class __Software:

    def __init__(self, name: str, license_name: str, license_page: str, homepage: str = None):
        self.__name = name
        self.__license_name = license_name
        self.__license_page = license_page
        self.__homepage = homepage
        used_software.add(self)

    def get_name(self) -> str:
        return self.__name

    def get_license(self) -> str:
        return self.__license_name

    def get_license_page(self) -> str:
        return self.__license_page

    def get_homepage(self) -> Optional[str]:
        return self.__homepage

    def to_dict(self) -> Dict[str, Optional[str]]:
        return {
            "homepage": self.get_homepage(),
            "name": self.get_name(),
            "license_page": self.get_license_page(),
            "license": self.get_license()
        }

    def __hash__(self):
        return hash(tuple(x.__hash__() for x in self.to_dict().values()))

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            self_dict = self.to_dict()
            other_dict = other.to_dict()
            return all(self_dict[x].__eq__(other_dict[x]) for x in self_dict.keys())
        return False


def get_used_software() -> List[Dict[str, Optional[str]]]:
    return [x.to_dict() for x in sorted(used_software, key=lambda x: x.get_name().lower())]


__Software(
    name="Bootstrap",
    homepage="https://getbootstrap.com",
    license_name="MIT License",
    license_page="https://github.com/twbs/bootstrap/blob/main/LICENSE"
)

__Software(
    name="Bootstrap icons",
    homepage="https://icons.getbootstrap.com",
    license_name="MIT License",
    license_page="https://github.com/twbs/icons/blob/main/LICENSE.md"
)

__Software(
    name="Flask",
    homepage="https://flask.palletsprojects.com",
    license_name="Flask-License",
    license_page="https://flask.palletsprojects.com/en/1.1.x/license/"
)

__Software(
    name="Flask-Session",
    homepage="https://github.com/fengsp/flask-session",
    license_name="Flask-Session-License",
    license_page="https://raw.githubusercontent.com/fengsp/flask-session/master/LICENSE"
)

__Software(
    name="config-path",
    homepage="https://github.com/barry-scott/config-path",
    license_name="Apache-2.0",
    license_page="https://raw.githubusercontent.com/barry-scott/config-path/master/LICENSE"
)

__Software(
    name="inAudible-NG/RainbowCrack-NG",
    homepage="https://github.com/inAudible-NG/RainbowCrack-NG",
    license_name="Custom license",
    license_page="https://github.com/inAudible-NG/tables/blob/master/README.md"
)
