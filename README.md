KITT4SME Dazzler
----------------
> Dazzling Dash-boards for KITT4SME services.

Multi-tenant, interactive [KITT4SME][k4s] dashboards powered by
[Dash][dash] and [FastAPI][fapi].


### Hacking

Install Python (`>= 3.8`), Poetry (`>=1.1`) and the usual Docker
stack (Engine `>= 20.10`, Compose `>= 2.1`). If you've got Nix, you
get a dev shell with the right Python and Poetry versions simply by
running

```console
$ nix shell github:c0c0n3/kitt4sme.dazzler?dir=nix
```

Otherwise, install the usual way you do on your platform. Then clone
this repo, `cd` into its root dir and install the Python dependencies

```console
$ git clone https://github.com/c0c0n3/kitt4sme.dazzler.git
$ cd kitt4sme.dazzler
$ poetry install
```

Finally drop into a virtual env shell to hack away

```bash
$ poetry shell
$ charm .
# ^ Pycharm or whatever floats your boat
```

Run all the test suites:

```console
$ pytest tests
```

or just the unit tests

```console
$ pytest tests/unit
```

Measure global test coverage and generate an HTML report

```console
$ coverage run -m pytest -v tests
$ coverage html
```

Run Dazzler locally on port 8080

```console
$ poetry shell
$ python -m dazzler.main
# ^ same as: uvicorn dazzler.main:app --host 0.0.0.0 --port 8000
```

Build and run the Docker image

```console
$ docker build -t kitt4sme/dazzler .
$ docker run -p 8000:8000 kitt4sme/dazzler
```




[dash]: https://plotly.com/dash/
[fapi]: https://fastapi.tiangolo.com/
[k4s]: https://kitt4sme.eu/
