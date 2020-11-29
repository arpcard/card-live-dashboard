from os.path import isfile, join
from os import listdir
from pathlib import Path
from io import BytesIO
import zipfile
import json

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
        flask_app.logger.info(f'Request to download all data from [{card_live_data_dir}]')
        memory_file = BytesIO()
        with zipfile.ZipFile(memory_file, 'w', compression=zipfile.ZIP_STORED) as zf:
            files = [f for f in listdir(card_live_data_dir) if isfile(join(card_live_data_dir, f))]
            for file in files:
                file_path = join(card_live_data_dir, file)
                with open(file_path) as f:
                    valid_file = False
                    try:
                        json_obj = json.load(f)
                        valid_file = True
                    except Exception:
                        pass
                    if valid_file and 'rgi_main' in json_obj:
                        zf.write(file_path, arcname=file)
                    else:
                        flask_app.logger.warning((f'File [{file_path}] is not a proper CARD:Live JSON file, '
                                                 'skipping file in download request.'))
        memory_file.seek(0)
        return flask.send_file(memory_file, attachment_filename='card-live-data.zip', as_attachment=True)
