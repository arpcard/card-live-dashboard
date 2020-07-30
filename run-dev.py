#!/usr/bin/env python
import logging
from pathlib import Path
import os.path as path

from card_live_dashboard.app import app
from card_live_dashboard.model.CardLiveDataLoader import CardLiveDataLoader
from card_live_dashboard.model.CardLiveData import CardLiveData
import card_live_dashboard.layouts as layouts

logger = logging.getLogger('run-dev')

if __name__ == '__main__':
    logging.basicConfig(level='DEBUG', format='%(asctime)s %(levelname)s %(name)s.%(funcName)s,%(lineno)s: %(message)s')
    logger.debug('Before run server')

    data_loader = CardLiveDataLoader(Path(path.dirname(__file__), 'data', 'card_live_small'))
    CardLiveData.create_instance(data_loader)
    data = CardLiveData.get_data_package()

    app.layout = layouts.default_layout(data)

    import card_live_dashboard.callbacks

    app.run_server(debug = False, port = 8050, host = '0.0.0.0')
    logger.debug('After run server')