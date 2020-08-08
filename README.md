# CARD:Live Dashboard

This repository contains code for the CARD:Live Dashboard.

# Dependencies

Please install dependencies using **conda** from the file `conda.env`.

# Running

## Production

To run the production server, please run:

```bash
./run-prod
```

This will serve the CARD:Live dashboard on port 8050. Underneath, this runs [gunicorn][]. You can run the `gunicorn` command directly to adjust the port, number of workers, etc.

## Development

To run the development server please run:

```bash
./run-dev
```

Note, as per the [Dash documentation][dash-deployment] (which references the Flash documentation) it is not recommended to run the development (built-in) server for a production machine since it doesn't scale well.

>While lightweight and easy to use, Flask's built-in server is not suitable for production as it doesn't scale well and by default serves only one request at a time.

# Tests

To run the tests, please run:

```bash
pytest
```

[dash-deployment]: https://dash.plotly.com/deployment
[gunicorn]: https://docs.gunicorn.org
