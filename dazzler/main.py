from fastapi import FastAPI
import uvicorn

from dazzler import __version__
from dazzler.dash.wiring import DashboardSubApp
import dazzler.dash.board.dbc_demo as demo
import dazzler.dash.board.roughnator as roughnator
import dazzler.dash.board.viqe as viqe


app = FastAPI()


@app.get('/')
def read_root():
    return {'dazzler': __version__}


@app.get("/version")
def read_version():
    return read_root()


def mount_dashboards():
    subAppBuilder = DashboardSubApp(app, __name__)
    subAppBuilder.assemble('/dazzler/manufracture/', roughnator.dash_builder)
    subAppBuilder.assemble('/dazzler/smithereens/', viqe.dash_builder)
    subAppBuilder.assemble('/dazzler/x/', viqe.dash_builder)
    subAppBuilder.assemble('/dazzler/demo/', demo.dash_builder)


mount_dashboards()


if __name__ == '__main__':
    uvicorn.run(app)
