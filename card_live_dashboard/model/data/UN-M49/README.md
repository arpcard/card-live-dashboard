# UN Country codes

This directory contains the UN Standard country/area codes for statistical use (M49). This was downloaded from <https://unstats.un.org/unsd/methodology/m49/overview/> on July 15, 2020.

I downloaded the Excel (instead of CSV) version of the file to preserve region names with commas in them. I converted to CSV using:

```python
import pandas as pd

df = pd.read_excel('UNSD — Methodology.xlsx', dtype = object)
df.to_csv('UNSD-Methodology.csv', encoding='utf-8', index=False)
```
