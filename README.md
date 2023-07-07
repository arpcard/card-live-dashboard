# CARD:Live Dashboard
[![python-test](https://github.com/arpcard/card-live-dashboard/workflows/python-test/badge.svg?branch=development)](https://github.com/arpcard/card-live-dashboard/actions/)
[![pypi](https://badge.fury.io/py/card-live-dashboard.svg)](https://badge.fury.io/py/card-live-dashboard)

**Click this link to access the [CARD:Live Dashboard][] server.**

[![card-live-overview.png][]][CARD:Live Dashboard]

This repository contains code for the [CARD:Live Dashboard][]. This is used to summarize and display data from [CARD:Live][] in a dashboard.

# Install

This application uses [Python Dash][] and so requires Python to be installed (Python 3.7+). It is recommended that you use a Python virtual environment (or conda) to install. To set this up and install the application please run:

```bash
# Setup virtual environment
virtualenv card-live-venv
source card-live-venv

python -m pip install card-live-dashboard
python -m pip install 'pandas<2.0.0' # Resolves deprecation of DataFrame.append in pandas
```

*Note: If you encounter an error related to __libgeos_c.so__, you may need to install this separately. One option is to install the `geos` package via conda (`conda install geos`) which should include __libgeos_c__. See issue [#18](https://github.com/arpcard/card-live-dashboard/issues/18)*.

## Development

If, instead, you want to install and do development on the code you can instead run (after creating a virtual environment):

```bash
# Clone project
git clone https://github.com/arpcard/card-live-dashboard
cd card-live-dashboard

# Change to main project directory
cd card-live-dashboard

python -m pip install -e .
python -m pip install 'pandas<2.0.0' # Resolves deprecation of DataFrame.append in pandas
```

This will make the installed application reflect any code changes made within `card-live-dashboard/`.

# Running

## Create CARD:Live Dashboard home directory

Before running, you will have to create a CARD:Live dashboard home directory. This directory will be used to store the CARD:Live data as well as the NCBI taxnomy database and configuration. Please run the below command to create this directory:

```bash
card-live-dash-init [cardlive-home]
```

By default this will download a copy of the most recent data from CARD:Live (available at <https://bergen.mcmaster.ca/cardlive/data/all>).

If, instead, you wish to start with an empty data directory you can use `--no-download-data`. In this case, you will have to copy data to `[cardlive-home]/data/card_live` before the application starts up.

### Data for development

If you are intending to do development or wishing to test out CARD:Live, it is recommended you downsample the data prior to running the application. This will make everything run quicker and smoother.

To do this, please run the following commands:

```bash
# Rename full data directory
mv [cardlive-home]/data/card_live [cardlive-home]/data/card_live.all

# Create new directory for downsampled data
mkdir [cardlive-home]/data/card_live

# Select a random subset of 500 samples and link them in the appropriate directory
find [cardlive-home]/data/card_live.all/ | shuf | head -n 500 | xargs -I {} ln {} [cardlive-home]/data/card_live/
```

Make sure to replace `[cardlive-home]` with your chosen directory name when running `card-live-dash-init`.

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

# Data

If you wish to make use of the data, it is all available for download from the main application (<https://bergen.mcmaster.ca/cardlive/>):

![data-download.png][]

This will give you a zip file of the results (in JSON format) of RGI,LMAT,MLST tools.

## API/Data processing tutorial

If you wish to make use of the data (e.g., load into dataframes for plotting) then feel free to following along with the following Juptyer notebook for how to convert the JSON results files to a dataframe using the CARD:Live Dashboard API.

* [CARD:Live API/Data Tutorial][]

For more general information on working with Plotly/Dash to construct figures (including producing the chropleth map) you can look at the below Juptyer notebook which was used for a previous CARD:Live presentation.

* [Plotly/Dash tutorial][]

A lot more details are found in the [Dash Documentation][Python Dash].

# Tests

To run the tests, please first install the application (to get the dependencies installed) and run:

```bash
pytest
```

# Contact

For more information you can contact <card@mcmaster.ca> or <aaron.petkau@gmail.com>.

[dash-deployment]: https://dash.plotly.com/deployment
[gunicorn]: https://docs.gunicorn.org
[gunicorn-prod-conf]: card_live_dashboard/service/config/gunicorn.conf.py
[gunicorn-conf-doc]: https://docs.gunicorn.org/en/latest/configure.html
[CARD:Live]: https://card.mcmaster.ca/live
[Python Dash]: https://plotly.com/dash/
[CARD:Live API/Data Tutorial]: doc/api/data-api-tutorial.ipynb
[card-live-overview.png]: doc/images/card-live-overview.png
[data-download.png]: doc/images/data-download.png
[CARD:Live Dashboard]: https://bergen.mcmaster.ca/cardlive/
[Plotly/Dash tutorial]: https://github.com/apetkau/cardlive-presentation-2020
