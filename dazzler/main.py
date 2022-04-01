from fastapi import FastAPI

from dazzler import __version__


app = FastAPI()


@app.get('/')
def read_root():
    return {'dazzler': __version__}


@app.get("/version")
def read_version():
    return read_root()
