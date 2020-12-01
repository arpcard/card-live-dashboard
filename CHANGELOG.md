# 0.5.0

* Added ability to download all data as a zip archive.
* Added option to print version from commands. 

# 0.4.0

* Adding GitHub Action to test project. Fixing some small issues in the process.
* Support only for Python 3.7+ (this was always the case, but now it's documented/tested).
* Adding additional space between y-axis labels and plots.
* Display all y-axis labels for certain plots.
* Added additional documentation to dashboard and updated title/favicon.
* Transitions to mobile view for larger displays.

# 0.3.0

* Renamed scripts from `cardlive-dash-X` to `card-live-dash-X`.
* Added configuration file `[cardlive-home]/config/cardlive.yaml` to specify a subpath to run the application.
* Added a gunicorn config file `[cardlive-home]/config/gunicorn.conf.py` to contain all config for the production server.
* Updated `card-live-dash-prod` script to allow start/status/stop commands.

# 0.2.0

* Mapping region **Antarctica** to **N/A** if the date is before *2020-07-20*. This is because before that date CARD:Live defaulted to **Antarctica** (instead of no selected region) and so there were many results showing up as Antarctica when it was likely intended these should be N/A.
* Changed organism selection. Now there is the option to select **RGI Kmer** or **LMAT** organism results and this will impact all the figures.
* Post-processing of LMAT organism results to make sure they do not go below the rank of species.
* Fixed bug in select by drug class causing multiple selections to miss some samples if drug classes were found on different contigs.
* Renamed *Besthit ARO* to *AMR gene*.
* Added plot for viewing drug class counts, AMR genes, AMR gene families, and Resistance Mechanism.
* Added `setup.py` install script.
* Added both percent and count plots for timeline.
* Added the ability to select a custom date range.

# 0.1.0

* First release of CARD:Live dashboard.
