#run first and make sure the files are in the colab first
from setuptools import setup, find_packages
import streamlit as st
from os import path
here = path.abspath(path.dirname(__file__))

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Education',
    'Intended Audience :: Customer Service',
    'Intended Audience :: Developers',
    'Intended Audience :: Information Technology',
    'Intended Audience :: Science/Research',
    'Intended Audience :: Telecommunications Industry',
    'Operating System :: OS Independent',
    'License :: OSI Approved :: Apache Software License',
    'Programming Language :: Python :: 3'
]

setup(
    name='searoute',
    version='1.4.2',
    description='A python package for generating the shortest sea route between two points on Earth.',
    #long_description=open('README.md').read() + '\n\n' +
    #open('CHANGELOG.txt').read(),
    long_description_content_type="text/markdown",
    url='',
    author='Gent Halili',
    author_email='genthalili@users.noreply.github.com',
    license='Apache License 2.0',
    classifiers=classifiers,
    keywords='searoute map sea route ocean ports',
    packages=find_packages(),
    install_requires=['geojson', 'networkx'],
    project_urls={
        "Documentation": "https://github.com/genthalili/searoute-py/blob/main/README.md",
        "Source": "https://github.com/genthalili/searoute-py",
    },
    include_package_data=True,
)
import searoute as sr
import pandas
import csv
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)# remove iloc warnings when getting distance
import sys
pandas.set_option('display.max_rows', None)
x=pandas.read_csv("ESG - Data sheet air freight shipping hubs.xlsx - Main - Air shipping.csv")#distance
x=x[:670]
y=pandas.read_csv("ESG - Data sheet sea freight.xlsx - Carbon footprints counting.csv")
ef=pandas.read_csv("ESG - Data sheet air freight shipping hubs.xlsx - Sheet1.csv")
import searoute as sr
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
def get_airport_coordinates(airport_code):
  geolocator = Nominatim(user_agent="airport_distance_calculator")
  try:
    location = geolocator.geocode(f"{airport_code} airport")
    if location:
      return (location.latitude, location.longitude)
    else:
      return None
  except Exception as e:
    return None
def get_airport_country(airport_code):
  geolocator = Nominatim(user_agent="airport_country_checker")
  try:
    location = geolocator.geocode(f"{airport_code} airport")
    if location:
      address = location.raw.get('display_name', '')
      return address.split(",")[-1].strip()
    else:
      return None
  except Exception as e:
    return None
def calculate_distance(airport_code1, airport_code2):
  coords1 = get_airport_coordinates(airport_code1)
  coords2 = get_airport_coordinates(airport_code2)


  if coords1 and coords2:
    distance = geodesic(coords1, coords2).kilometers
    print("Distance:",distance)
    return distance
  else:
    print("Unable to calculate distance due to missing coordinates.")
def check_same_country(airport_code1, airport_code2):
  country1 = get_airport_country(airport_code1)
  country2 = get_airport_country(airport_code2)


  if country1 and country2:
    return country1==country2
  else:
    return 0
choice=int(input("1 for sea and 0 for air"))
if choice:
  database=int(input("Enter mode:\n0: Database\n1: Coordinates\n"))
  if not database:
  #sea route if data in csv
    seaports0=y[y.columns[2]].values.tolist()
    seaports0=[str(i[8:]) for i in seaports0]
    seaports1=y[y.columns[4]].values.tolist()
    seaports1=[str(i[8:]) for i in seaports1]
    y["Codes_Starting"]=seaports0
    y["Codes_Ending"]=seaports1
    start=input("Enter start country ")
    end="Vietnam"#input("Enter country 2 ")# currently only vietnam because limited database
    #target=x[(x.Starting_Point==start and x.Ending_Point==end) or (x.Starting_Point==end and x.Ending_Point==start)]
    ef1=[0,0,0]
    target=y[y["Starting_Point"]==start]
    target=target[target["Ending_Point"]==end]
    if target.empty:
      print("Not Found, exiting, please try mode 1 for coordinates")
      sys.exit()
    print("Available Seaport codes:")
    print(target[["Codes_Starting","Codes_Ending"]])
    if len(target)==1:
      print("only one entry exists, using this entry")
      code1=target.iloc[0][9]
      code2=target.iloc[0][10]
    else:
      code1=input("Enter port code 1: choose 1 from Codes_Starting ")
      code2=input("Enter port code 2: choose 1 from Codes_Ending ")
    target=target[target["Codes_Starting"]==code1]
    target=target[target["Codes_Ending"]==code2]
    if target.empty:
      print("Not Found, exiting, please run and enter again")
      sys.exit()
    distance=target.iloc[0][8]
    print("Distance:",distance)
    try:
      teu=int(input("Enter TEU capacity: "))
    except:
      teu=-1
    try:
      percent=float(input("Enter % of capacity, do not include % sign: Default 70: "))
    except:
      percent=70
    if teu==-1:#unknown
      ef2=0.016
    elif teu<1000:
      ef2=0.0363
    elif teu<2000:
      ef2=0.0321
    elif teu<3000:
      ef2=0.0200
    elif teu<8000:
      ef2=0.0167
    else:
      ef2=0.0125
    try:
      ref_teu=int(input("Enter refrigerated teu capacity, default 800: "))
    except:
      ref_teu=800
    days_operated=min(int(input("Enter days operated out of 365: ")),365)
    weight=teu*24*percent/100 #using 24000kg per teu: https://oneworldcourier.com.au/what-is-a-teu-shipping-container/
    try:
      speed=float(input("Enter speed, default is 21 knots: "))#slow steaming
    except:
      speed=21.00
    print("CO2 Emission:",weight*distance*ef2*(speed/21)**2/1000,"kg")#fuel burned per km squares with speed
    ref_consum=ref_teu*1.9*1914/365*days_operated
    print("Refrigerator fuel consumption",ref_consum)
    dry_intensity=ef2*(target.iloc[0][7])*(speed/21)**2/0.875**2/distance/teu/(percent/100)*1000000
    print("Dry Container Emission Intensity:",dry_intensity)
    ref_intensity=dry_intensity+ef2*ref_consum/distance/(percent/100)/teu
    print("Refrigerated Container Emission Intensity",ref_intensity)
  else:
    lat1=float(input("Latitude 1 (-90 to 90): "))
    long1=float(input("Longitude 1 (-180 to 180): "))
    lat2=float(input("Latitude 2 (-90 to 90): "))
    long2=float(input("Longitude 2 (-180 to 180): "))
    origin=[long1,lat1]
    dest=[long2,lat2]
    route=sr.searoute(origin,dest)
    #print(route)
    distance=route.properties['length']
    print("Distance:",distance)
    teu=int(input("Enter TEU capacity: "))
    try:
      percent=float(input("Enter % of capacity, do not include % sign (Default 70): "))
    except:
      percent=70
    if teu<1000:
      ef2=0.0363
    elif teu<2000:
      ef2=0.0321
    elif teu<3000:
      ef2=0.0200
    elif teu<8000:
      ef2=0.0167
    else:
      ef2=0.0125
    try:
      ref_teu=int(input("Enter refrigerated teu capacity, default 800: "))
    except:
      ref_teu=800
    days_operated=min(int(input("Enter days operated out of 365: ")),365)
    # if more than 365 days, assume user means 365
    weight=teu*24*percent/100 #using 24000kg per teu: https://oneworldcourier.com.au/what-is-a-teu-shipping-container/
    try:
      speed=float(input("Enter speed, default is 21 knots: "))
    except:
      speed=21.00
    print("CO2 Emission:",weight*distance*ef2*(speed/21)**2,"kg")#fuel burned per km squares with speed
    ref_consum=ref_teu*1.9*1914/365*days_operated
    print("Refrigerator fuel consumption",ref_consum)
    dry_intensity=ef2/126.85*(speed/21)**2/teu/(percent/100)*1000000
    print("Dry Container Emission Intensity:",dry_intensity)
    ref_intensity=dry_intensity+ef2*ref_consum/distance/(percent/100)/teu
    print("Refrigerated Container Emission Intensity",ref_intensity)
else:
  code1=code2=""
  not_found=0
  airports0=x[x.columns[2]].values.tolist()
  airports0=[str(i[-4:-1]) for i in airports0]
  airports1=x[x.columns[4]].values.tolist()
  airports1=[str(i[-4:-1]) for i in airports1]
  x["Codes_Starting"]=airports0
  x["Codes_Ending"]=airports1
  start=input("Enter country 1 ")
  end=input("Enter country 2 ")#may be domestic flight
  #target=x[(x.Starting_Point==start and x.Ending_Point==end) or (x.Starting_Point==end and x.Ending_Point==start)]
  ef1=0
  target=x[(x["Starting_Point"]==start)|(x["Starting_Point"]==end)]
  if end=="United States" or end=="US" or start=="United States" or start=="US":
    target=target[(target["Ending_Point"]=="US")|(target["Ending_Point"]=="United States")|(target["Starting_Point"]=="US")|(target["Starting_Point"]=="United States")]
  else:
    target=target[(target["Ending_Point"]==end)|(target["Ending_Point"]==start)]
  if target.empty:
    not_found=1
  else:
    print("Available Airport codes:")
    print(target[["Codes_Starting","Codes_Ending"]])
    if len(target)==1:
      print("only one entry exists, using this entry")
      code1=target.iloc[0][6]
      code2=target.iloc[0][7]
      code1=input("Enter port code 1: choose 1 from Codes_Starting ")
      code2=input("Enter port code 2: choose 1 from Codes_Ending ")
    target=target[target["Codes_Starting"]==code1]
    target=target[target["Codes_Ending"]==code2]
    if target.empty:
      not_found=1
  print(not_found)
  if not not_found:
    distance=target.iloc[0][5]
    print("Distance:",distance)
    if start==end:
      ef1=ef.iloc[0][5]
    else:
      if int(distance)<3700:
        ef1=ef.iloc[1][5]
      else:ef1=ef.iloc[2][5]
  else:
    if code1=="" or code2=="":
      code1=input("Enter port code 1: ")
      code2=input("Enter port code 2: ")
    airport_code1 = code1.strip().upper()
    airport_code2 = code2.strip().upper()
    try:
      dst=calculate_distance(airport_code1, airport_code2)
      if check_same_country(airport_code1,airport_code2):
        ef1=ef.iloc[0][5]#domestic
      elif dst<3700:
        ef1=ef.iloc[1][5]#short haul
      else:ef1=ef.iloc[2][5]#long haul
    except:
      print("Timed out or error extracting data of one or both airports, or airport doesn't exist")
      #it seems that codes like MAA will time out the processor although MAA is Chennai International Airport in India
  try:
    weight=int(input("Enter weight in kg: Default 6804: "))
  except:
    weight=6804 #weight of p6p assumed if no or invalid input
  co2=weight*distance*ef1
  print("CO2 Emission:",co2/1000,"kg")
  print("This is equivalent to:")
  co2/=1000000
  print(co2*370.37,"kg of rice")
  print(co2*16.67,"kg of beef")
  print(co2*833.33,"liters of milk")
  print(co2*0.8,"hectares of cropland of fertilizer")
