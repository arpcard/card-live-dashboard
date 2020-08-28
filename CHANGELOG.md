# 0.2.0

* Mapping region **Antarctica** to **N/A** if the date is before *2020-07-20*. This is because before that date CARD:Live defaulted to **Antarctica** (instead of no selected region) and so there were many results showing up as Antarctica when it was likely intended these should be N/A.
* Changed organism selection. Now there is the option to select **RGI Kmer** or **LMAT** organism results and this will impact all the figures.
* Post-processing of LMAT organism results to make sure they do not go below the rank of species.
* Fixed bug in select by drug class causing multiple selections to miss some samples if drug classes were found on different contigs.
* Renamed *Besthit ARO* to *AMR gene*.
* Added plot for viewing drug class counts and AMR genes.
* Added `setup.py` install script.
* Added both percent and count plots for timeline.
* Added *AMR Gene Family* and *Resistance Mechanism* as selection criteria and as figures.
* Added the ability to select a custom date range.

# 0.1.0

* First release of CARD:Live dashboard.
