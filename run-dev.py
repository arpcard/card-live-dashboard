#!/usr/bin/env python

import card_live_dashboard.app

if __name__ == '__main__':
    app = card_live_dashboard.app.build_app()
    app.run_server(debug = False,
                  port = 8050,
                  host = '0.0.0.0')