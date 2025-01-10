#run first and make sure the files are in the colab first
import pandas
import csv
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)# remove iloc warnings when getting distance
import sys
pandas.set_option('display.max_rows', None)
x=pandas.read_csv("/content/ESG - Data sheet air freight shipping hubs.xlsx - Main - Air shipping.csv")#distance
x=x[:670]
y=pandas.read_csv("/content/ESG - Data sheet sea freight.xlsx - Carbon footprints counting.csv")
ef=pandas.read_csv("/content/ESG - Data sheet air freight shipping hubs.xlsx - Sheet1.csv")
pip install searoute
