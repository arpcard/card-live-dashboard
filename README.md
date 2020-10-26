# CARD:Live Dashboard

**A test server for the CARD:Live Dashboard is available at <https://bergen.mcmaster.ca/app2/>. Please let us know if you have any feedback (via a GitHub issue).**

This repository contains code for the CARD:Live Dashboard. This is used to summarize and display data from [CARD:Live][] in a dashboard.

![card-live-overview.png][]

# Install

This application uses [Python Dash][] and so requires Python to be installed (Python 3). It is recommended that you use a Python virtual environment (or conda) to install. To set this up and install the application please run:

```bash
git clone https://github.com/arpcard/card-live-dashboard
cd card-live-dashboard

# Setup virtual environment
virtualenv card-live-venv
source card-live-venv

pip install .
```

## Development

If, instead, you want to install and do development on the code you can instead run (after creating a virtual environment):

```bash
# Change to main project directory
cd card-live-dashboard

pip install -e .
```

This will make the installed application reflect any code changes made within `card-live-dashboard/`.

# Running

## Create CARD:Live Dashboard home directory

Before running, you will have to create a CARD:Live dashboard home directory. This directory will be used to store the CARD:Live data as well as the NCBI taxnomy database. Please run the below command to create this directory:

```bash
cardlive-dash-init [cardlive-home]
```

Once this is created, please copy over the CARD:Live data (JSON files) to `[cardlive-home]/data/card_live`.

## Production

To run the production server, please run:

```bash
cardlive-dash-prod [cardlive-home]
```

Where `[cardlive-home]` is the CARD:Live home directory.

This will serve the CARD:Live dashboard on port 8050. Underneath, this runs [gunicorn][]. You can also run the `gunicorn` command directly to adjust the port, number of workers, etc.

```bash
gunicorn --workers 2 -b 0.0.0.0:8050 "card_live_dashboard.app:flask_app(card_live_home='[cardlive-home]')" --timeout 600 --log-level debug
```

## Development

To run the development server please run:

```bash
cardlive-dash-dev [cardlive-home]
```

This assumes that you've installed the application with `pip install -e card-live-dashboard`.

**Note**: As per the [Dash documentation][dash-deployment] (which references the Flash documentation) it is not recommended to run the development (built-in) server for a production machine since it doesn't scale well. **Important**: also, since debug mode is turned on this will expose certain information about the underlying server. Please do not use development mode in production.

## Profiling

There is also a server used to profile requests coming to the server (for looking at time of requests). This can be run like:

```bash
cardlive-dash-profiler [cardlive-home]
```

The same caveats as for the Development server still apply (it also turns on Debug mode and should not be run for a production server).

# Tests

To run the tests, please first install the application (to get the dependencies installed) and run:

```bash
pytest
```

[dash-deployment]: https://dash.plotly.com/deployment
[gunicorn]: https://docs.gunicorn.org
[CARD:Live]: https://card.mcmaster.ca/live
[Python Dash]: https://plotly.com/dash/
[card-live-overview.png]: images/card-live-overview.png
