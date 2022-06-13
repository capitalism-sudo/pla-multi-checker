from enum import Enum

class AppMode(Enum):
    WEB = "WEB"
    LOCAL = "LOCAL"
    DEV = "DEV"

_resources = {
    AppMode.WEB: '/home/cappy/pla-multi-checker-web/',
    AppMode.LOCAL: './static/',
    AppMode.DEV: '../static/'
}

APP_MODE = AppMode.LOCAL
RESOURCE_PATH = _resources[APP_MODE]