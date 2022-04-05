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
    subAppBuilder.assemble(viqe.dash_builder, tenant_name='itek')
    subAppBuilder.assemble(roughnator.dash_builder, tenant_name='csic')

    subAppBuilder.assemble(demo.dash_builder, tenant_name='demo')
    # subAppBuilder.assemble(viqe.dash_builder, tenant_name='demo')
    # subAppBuilder.assemble(roughnator.dash_builder, tenant_name='demo')


mount_dashboards()


if __name__ == '__main__':
    uvicorn.run(app)
