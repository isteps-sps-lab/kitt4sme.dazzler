from fastapi import FastAPI
import uvicorn

from dazzler import __version__
from dazzler.config import dazzler_config
from dazzler.dash.wiring import DashboardSubApp


app = FastAPI()
DashboardSubApp(app, __name__).mount_dashboards(dazzler_config())


@app.get('/')
def read_root():
    return {'dazzler': __version__}


@app.get("/version")
def read_version():
    return read_root()


if __name__ == '__main__':
    uvicorn.run(app)
