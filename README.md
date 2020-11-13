# CARD:Live Dashboard
[![python-test](https://github.com/arpcard/card-live-dashboard/workflows/python-test/badge.svg?branch=development)](https://github.com/arpcard/card-live-dashboard/actions/)
[![pypi](https://badge.fury.io/py/card-live-dashboard.svg)](https://badge.fury.io/py/card-live-dashboard)

**A test server for the CARD:Live Dashboard is available at <https://bergen.mcmaster.ca/cardlive/>. Please let us know if you have any feedback (via GitHub or email <card@mcmaster.ca>).**

This repository contains code for the CARD:Live Dashboard. This is used to summarize and display data from [CARD:Live][] in a dashboard.

![card-live-overview.png][]

# Install

This application uses [Python Dash][] and so requires Python to be installed (Python 3.7+). It is recommended that you use a Python virtual environment (or conda) to install. To set this up and install the application please run:

```bash
# Setup virtual environment
virtualenv card-live-venv
source card-live-venv

python -m pip install card-live-dashboard
```

## Development

If, instead, you want to install and do development on the code you can instead run (after creating a virtual environment):

```bash
# Clone project
git clone https://github.com/arpcard/card-live-dashboard
cd card-live-dashboard

# Change to main project directory
cd card-live-dashboard

python -m pip install -e .
```

This will make the installed application reflect any code changes made within `card-live-dashboard/`.

# Running

## Create CARD:Live Dashboard home directory

Before running, you will have to create a CARD:Live dashboard home directory. This directory will be used to store the CARD:Live data as well as the NCBI taxnomy database and configuration. Please run the below command to create this directory:

```bash
card-live-dash-init [cardlive-home]
```

Once this is created, please copy over the CARD:Live data (JSON files) to `[cardlive-home]/data/card_live`.

## Production

### Running

To run the production server, please run:

```bash
card-live-dash-prod start [cardlive-home]
```

Where `[cardlive-home]` is the CARD:Live home directory.

This will serve the CARD:Live dashboard on port 8050 by default. Underneath, this runs [gunicorn][].

### Check status

To check the status of the CARD:Live application you can run:

```bash
card-live-dash-prod status [cardlive-home]
```

This will let you know if the application is running.

### Stopping the application

To stop the application you can run:

```
card-live-dash-prod stop [cardlive-home]
```

This will kill the main application and any workers. Note this requires the application to be started in **daemon** mode to work properly.

### Configuration

#### Gunicorn config

The file `[cardlive-home]/config/gunicorn.conf.py` can be used to adjust many configuration options for running the web server. An example of this file can be found [here][gunicorn-prod-conf]. A subset of the options is shown below and a more detailed list can be found in the [gunicorn configuration documentation][gunicorn-conf-doc].

```
bind = '127.0.0.1:8050'
workers = 2
...
```

Please modify this file to adjust configuration.

#### Application config

There also exists a separate YAML configuration file for the application. Right now this is only used to specify a path where the application can run. This will be stored in `[cardlive-home]/config/cardlive.yaml` and will look like:

```yaml
---
## A URL path under which the application should run (e.g., http://localhost/app/).
## Defaults to '/'. Uncomment if you want to run under a new path.
#url_base_pathname: /app/
```

If you wish to run the application under some non-root directory (e.g., under `http://localhost:8050/app`) you can modify the `url_base_pathname` here.

### Running directly using gunicorn

You can also run the `gunicorn` command directly to override configuration settings.

```bash
gunicorn --workers 2 -b 0.0.0.0:8050 "card_live_dashboard.app:flask_app(card_live_home='[cardlive-home]')" --timeout 600 --log-level debug
```

## Development

To run the development server please run:

```bash
card-live-dash-dev [cardlive-home]
```

**Note**: As per the [Dash documentation][dash-deployment] (which references the Flash documentation) it is not recommended to run the development (built-in) server for a production machine since it doesn't scale well. **Important**: also, since debug mode is turned on this will expose certain information about the underlying server. Please do not use development mode in production.

## Profiling

There is also a server used to profile requests coming to the server (for looking at time of requests). This can be run like:

```bash
card-live-dash-profiler [cardlive-home]
```

The same caveats as for the Development server still apply (it also turns on Debug mode and should not be run for a production server).

# Tests

To run the tests, please first install the application (to get the dependencies installed) and run:

```bash
pytest
```

[dash-deployment]: https://dash.plotly.com/deployment
[gunicorn]: https://docs.gunicorn.org
[gunicorn-prod-conf]: card_live_dashboard/service/config/gunicorn.conf.py
[gunicorn-conf-doc]: https://docs.gunicorn.org/en/latest/configure.html
[CARD:Live]: https://card.mcmaster.ca/live
[Python Dash]: https://plotly.com/dash/
[card-live-overview.png]: images/card-live-overview.png
