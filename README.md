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


### Demo dashboard

So we piggyback on Dash and its Bootstrap Components extension to
get dazzling dashboards. If you're new to this visualisation framework,
start Dazzler (either directly or through Docker) and browse to

- http://localhost:8000/dazzler/demo/-/

to see some of the Dash Bootstrap goodies. Then have a look under the
bonnet to check out the implementation. (Code adapted from the [Dash
Bootstrap Theme Explorer][dash.explorer].)


### Live simulator

We've also whipped together a test bed to simulate a live environment
similar to that of the KITT4SME cluster. In the `tests/sim` directory,
you'll find a Docker compose file with

* Quantum Leap with a CrateDB backend
* Our Dazzler service
* Dazzler config to make the VIQE and Roughnator dashboards available
  to a tenant named "demo".

To start the show, run (Ctrl+C to stop)

```console
$ poetry shell
$ python tests/sim
```

This will bring up the Docker compose environment (assuming you've got a
Docker engine running already) and then will start sending Quantum Leap
Roughnator estimate and VIQE inspection report entities. To see what's
going on, browse to the CrateDB Web UI at: http://localhost:4200.

Now browse to the Roughnator dashboard at:

- http://localhost:8000/dazzler/demo/-/roughnator

You should see the dashboard with an explanation of what it is and
how it works. Load the available estimate entity IDs, then select
one to plot the data. The dashboard fetches new data from Quantum
Leap every few seconds, so as the simulator sends entities you should
be able to see the new data points reflected in the plot.

Likewise, if you browse to the Sleuth dashboard at:

- http://localhost:8000/dazzler/demo/-/sleuth

You should be able to monitor in real-time inspection reports as the
simulator produces them. (Sleuth is a made-up AI service that inspects
parts being machined to sniff out surface areas where defects are likely
to be. Loosely based on the first implementation of VIQE.)

Finally, there's a tech-preview dashboard for Insight Generator at

- http://localhost:8000/dazzler/demo/-/insight/




[dash]: https://plotly.com/dash/
[dash.explorer]: https://hellodash.pythonanywhere.com/figure_templates
[fapi]: https://fastapi.tiangolo.com/
[k4s]: https://kitt4sme.eu/
