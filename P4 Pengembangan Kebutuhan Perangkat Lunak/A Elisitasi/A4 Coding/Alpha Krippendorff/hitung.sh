#!/usr/bin/bash
pip install pandas numpy openpyxl

python hitung_alpha_krippendorff.py coder1.xlsx coder2.xlsx --pilot
python hitung_alpha_krippendorff.py coder1.xlsx coder2.xlsx --boot 5000 --out hasil.xlsx
