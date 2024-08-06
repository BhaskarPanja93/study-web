from pathlib import Path

from internal.SecretEnums import *


for location in HostDetails.possibleFolderLocation.value:
    if Path(location).is_dir():
        folderLocation = location
        break
else:
    input("Project directory not found in SecretEnum...")


class RequiredFiles(Enum):
    webServerRunnable = str(Path(folderLocation, r"internal\_webserver_worker.py"))
    webServerRequired = [
        str(Path(folderLocation, r"internal\_webserver_worker.py")),
        str(Path(folderLocation, r"run_servers.py"))
    ]
    apiServerRunnable = str(Path(folderLocation, r"internal\_api_worker.py"))
    apiServerRequired = [
        str(Path(folderLocation, r"internal\_api_worker.py")),
        str(Path(folderLocation, r"run_servers.py"))
    ]
    cdnServerRunnable = str(Path(folderLocation, r"internal\_cdn_worker.py"))
    cdnServerRequired = [
        str(Path(folderLocation, r"internal\_cdn_worker.py")),
        str(Path(folderLocation, r"run_servers.py"))
    ]
    connServerRunnable = str(Path(folderLocation, r"internal\_connection_worker.py"))
    connServerRequired = [
        str(Path(folderLocation, r"internal\_connection_worker.py")),
        str(Path(folderLocation, r"run_servers.py"))
    ]


class FormPurposes(Enum):
    register = "register"
    login = "login"


class Routes(Enum):
    webHomePage = "/better-education"
    webWS = f"{webHomePage}-ws"
    cdnMemoryContent = f"{webHomePage}-content-cache"
    cdnFileContent = f"{webHomePage}-content-raw"
    connCheck = f"{webHomePage}-conn-check"
    connChange = f"{webHomePage}-conn-check"
    connCreate = f"{webHomePage}-conn-create"
    connDestroy = f"{webHomePage}-conn-destroy"


class WebsiteRelated(Enum):
    appName = "Gambit"
    title = "Study Well"


class CDNFileType(Enum):
    font = "font"
    image = "image"
    video = "video"
    css = "css"
    html = "html"
    js = "js"


class Fonts(Enum):
    GothamBlack = f"/{Routes.cdnFileContent.value}?type={CDNFileType.font.value}?name=GothamBlack.ttf"

