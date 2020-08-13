# 0.2.0

* Mapping region **Antarctica** to **N/A** if the date is before *2020-07-20*. This is because before that date CARD:Live defaulted to **Antarctica** (instead of no selected region) and so there were many results showing up as Antarctica when it was likely intended these should be N/A.
* Added an organism select dropdown for both LMAT and RGI Kmer results.
* Fixed bug in select by drug class causing multiple selections to miss some samples if drug classes were found on different contigs.
* Added plot for viewing drug class counts.
* Added plot for Best Hit ARO (AMR gene).

# 0.1.0

* First release of CARD:Live dashboard.
