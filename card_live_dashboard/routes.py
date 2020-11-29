from os.path import basename
from pathlib import Path
from io import BytesIO
from glob import glob
import zipfile

import flask


def create_flask_routes(flask_app: flask.app.Flask, base_pathname: str, card_live_data_dir: Path) -> None:
    """
    Creates flask routes outside of Dash application. Mainly used to provided a route to
    download all data.
    :param flask_app: The Flask application.
    :param base_pathname: The base path the application is running under.
    :param card_live_data_dir: The data directory containing CARD:Live data.
    :return: Returns nothing.
    """
    if base_pathname is None:
        base_pathname = '/'
    elif not base_pathname.startswith('/'):
        base_pathname = '/' + base_pathname

    if base_pathname.endswith('/'):
        base_pathname = base_pathname.rstrip('/')

    # Code derived from https://stackoverflow.com/a/27337047
    @flask_app.route(f'{base_pathname}/data/current')
    def download_data():
        memory_file = BytesIO()
        with zipfile.ZipFile(memory_file, 'w', compression=zipfile.ZIP_STORED) as zf:
            files = glob(str(card_live_data_dir / '*'))
            for file in files:
                zf.write(file, arcname=basename(file))
        memory_file.seek(0)
        return flask.send_file(memory_file, attachment_filename='card-live-data.zip', as_attachment=True)
