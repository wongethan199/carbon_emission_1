# create a streamlit account and make a blank app then paste the code
# before running the program make sure that you have run
# pip install searoute
# and
# pip install geopy
# on the terminal

import streamlit as st
import searoute as sr
import pandas
import csv
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)# remove iloc warnings when getting distance

pandas.set_option('display.max_rows', None)
x=pandas.read_csv("https://raw.githubusercontent.com/wongethan199/carbon_emission_1/main/ESG%20-%20Data%20sheet%20air%20freight%20shipping%20hubs.xlsx%20-%20Main%20-%20Air%20shipping.csv")#distance
x=x[:670]
y=pandas.read_csv("https://raw.githubusercontent.com/wongethan199/carbon_emission_1/refs/heads/main/ESG%20-%20Data%20sheet%20sea%20freight.xlsx%20-%20Carbon%20footprints%20counting.csv")
ef=pandas.read_csv("https://raw.githubusercontent.com/wongethan199/carbon_emission_1/refs/heads/main/ESG%20-%20Data%20sheet%20air%20freight%20shipping%20hubs.xlsx%20-%20Sheet1.csv")
w=pandas.read_csv("https://raw.githubusercontent.com/wongethan199/carbon_emission_1/refs/heads/main/aircraft%20weight.csv")
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
    st.write("Distance:",round(distance),'km')
    return distance
  else:
    st.write("Unable to calculate distance due to missing coordinates.")
def check_same_country(airport_code1, airport_code2):
  country1 = get_airport_country(airport_code1)
  country2 = get_airport_country(airport_code2)


  if country1 and country2:
    return country1==country2
  else:
    return 0
st.header("Carbon Emission Calculator")
choice=st.text_input("Enter 0 for air(Default) and 1 for sea: ")
if choice=='1':
  st.write("Current mode: Sea")
  database=st.text_input("Enter mode:\n0: Database (Default, only supports Vietnam as end)\n1: Coordinates\n")
  
  if database=='0' or not database:
  #sea route if data in csv
    seaports0=y[y.columns[2]].values.tolist()
    seaports0=[str(i[8:]) for i in seaports0]
    seaports1=y[y.columns[4]].values.tolist()
    seaports1=[str(i[8:]) for i in seaports1]
    y["Codes_Starting"]=seaports0
    y["Codes_Ending"]=seaports1
    start=st.text_input("Enter start country ")
    ef1=0
    target=y[y["Starting_Point"].str.lower()==start.lower().strip()]
    if target.empty:
      if start:
        st.write("Not Found, please try mode 1 for coordinates")
    else:
      st.write("Available Seaport codes:")
      st.write(target[["Codes_Starting","Codes_Ending"]])
      if len(target)==1:
        st.write("only one entry exists, using this entry")
        code1=target.iloc[0][9]
        code2=target.iloc[0][10]
      else:
        code1=st.text_input("Enter port code 1: choose 1 from Codes_Starting ")
        code2=st.text_input("Enter port code 2: choose 1 from Codes_Ending ")
      if code1 and code2:
        target=target[target["Codes_Starting"].str.lower()==code1.lower().strip()]
        target=target[target["Codes_Ending"].str.lower()==code2.lower().strip()]
        if target.empty:
          st.write("Not Found")
        else:
          distance=target.iloc[0][8]
          st.write("Distance:",round(distance),'km')
          try:
            teu=int(st.text_input("Enter TEU capacity: "))
          except:
            teu=24000
          try:
            percent=float(st.text_input("Enter % of capacity, do not include % sign: Default 70: "))
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
            ref_teu=int(st.text_input("Enter refrigerated teu capacity, default 800: "))
          except:
            ref_teu=800
          days_operated=st.text_input("Enter days operated out of 365: ")
          if days_operated:
            days_operated=int(days_operated)
            days_operated=min(days_operated,365)
            weight=teu*24*percent/100 #using 24000kg per teu: https://oneworldcourier.com.au/what-is-a-teu-shipping-container/
            try:
              speed=float(st.text_input("Enter speed, default is 21 knots: "))#slow steaming
            except:
              speed=21.00
            co2=weight*distance*ef2*(speed/21)**2/1000
            st.write("CO2 Emission:",round(co2,1),"kg")
            st.write("This is equivalent to:")
            co2/=1000000
            st.write(round(co2*370.37,1),"kg of rice")
            st.write(round(co2*16.67,2),"kg of beef")
            st.write(round(co2*833.33,1),"liters of milk")
            st.write(round(co2*0.8,3),"hectares of cropland of fertilizer")
            ref_consum=ref_teu*1.9*1914/365*days_operated
            st.write("Refrigerator fuel consumption",ref_consum)
            dry_intensity=ef2*(target.iloc[0][7])*(speed/21)**2/0.875**2/distance/teu/(percent/100)*1000000
            st.write("Dry Container Emission Intensity:",dry_intensity)
            ref_intensity=dry_intensity+ef2*ref_consum/distance/(percent/100)/teu
            st.write("Refrigerated Container Emission Intensity",ref_intensity)
  else:
    lat1=st.text_input("Latitude 1 (-90 to 90): ")
    long1=st.text_input("Longitude 1 (-180 to 180): ")
    lat2=st.text_input("Latitude 2 (-90 to 90): ")
    long2=st.text_input("Longitude 2 (-180 to 180): ")
    lst=[long1,lat1,long2,lat2]
    if all(lst):
      lst=[float(i)for i in lst]
      origin=lst[:2]
      dest=lst[2:]
      route=sr.searoute(origin,dest)
      #st.write(route)
      distance=route.properties['length']
      st.write("Distance:",round(distance),'km')
      try:
        teu=int(st.text_input("Enter TEU capacity: "))
      except:
        teu=24000
      try:
        percent=float(st.text_input("Enter % of capacity, do not include % sign (Default 70): "))
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
        ref_teu=int(st.text_input("Enter refrigerated teu capacity, default 800: "))
      except:
        ref_teu=800
      days_operated=min(int(st.text_input("Enter days operated out of 365: ")),365)
      # if more than 365 days, assume user means 365
      weight=teu*24*percent/100 #using 24000kg per teu: https://oneworldcourier.com.au/what-is-a-teu-shipping-container/
      try:
        speed=float(st.text_input("Enter speed, default is 21 knots: "))
      except:
        speed=21.0
      co2=weight*distance*ef2*(speed/21)**2/1000
      st.write("CO2 Emission:",round(co2,1),"kg")
      st.write("This is equivalent to:")
      co2/=1000000
      st.write(round(co2*370.37,1),"kg of rice")
      st.write(round(co2*16.67,2),"kg of beef")
      st.write(round(co2*833.33,1),"liters of milk")
      st.write(round(co2*0.8,3),"hectares of cropland of fertilizer")
      ref_consum=ref_teu*1.9*1914/365*days_operated
      st.write("Refrigerator fuel consumption",ref_consum)
      dry_intensity=ef2/126.85*(speed/21)**2/teu/(percent/100)*1000000
      st.write("Dry Container Emission Intensity:",dry_intensity)
      ref_intensity=dry_intensity+ef2*ref_consum/distance/(percent/100)/teu
      st.write("Refrigerated Container Emission Intensity",ref_intensity)
else:
  st.write("Current mode: Air")
  target=pandas.DataFrame()
  code1=code2=""
  not_found=0
  airports0=x[x.columns[2]].values.tolist()
  airports0=[str(i[-4:-1]) for i in airports0]
  airports1=x[x.columns[4]].values.tolist()
  airports1=[str(i[-4:-1]) for i in airports1]
  x["Codes_Starting"]=airports0
  x["Codes_Ending"]=airports1
  start=st.text_input("Enter country 1").lower().strip()
  end=st.text_input("Enter country 2").lower().strip()
  ef1=0
  if start and end:
    target=x[(x["Starting_Point"].str.lower()==start)|(x["Starting_Point"].str.lower()==end)]
    if end=="united states" or end=="us" or start=="united states" or start=="us":
      target=target[(target["Ending_Point"]=="US")|(target["Ending_Point"]=="United States")|(target["Starting_Point"]=="US")|(target["Starting_Point"]=="United States")]
    else:
      target=target[(target["Ending_Point"].str.lower()==end)|(target["Ending_Point"].str.lower()==start)]
    if start!=end:
      target=target[target["Ending_Point"].str.lower()!=target["Starting_Point"].str.lower()]
    if target.empty:
      not_found=1
      st.write("Not Found, will use geopy")# the database will be faster if the data is found, and prevents errors like timeout
    else:
      st.write("Available Airport codes:")
      st.write(target[["Codes_Starting","Codes_Ending"]])
      if len(target)==1:
        st.write("only one entry exists, using this entry")
        code1=target.iloc[0][6]
        code2=target.iloc[0][7]
      else:
        code1=st.text_input("Enter port code 1: ")
        code2=st.text_input("Enter port code 2: ")
      if code2 and code1:
        target=target[target["Codes_Starting"]==code1.upper().strip()]
        target=target[target["Codes_Ending"]==code2.upper().strip()]
        if target.empty:
          not_found=1
  if not not_found:
    distance=target.iloc[0][5]
    st.write("Distance:",distance,'km')
    if start==end:
      ef1=ef.iloc[0][5]
    else:
      if int(distance)<3700:
        ef1=ef.iloc[1][5]
      else:ef1=ef.iloc[2][5]
  else:
    if code1=="" or code2=="":
      code1=st.text_input("Enter port code 1: ")
      code2=st.text_input("Enter port code 2: ")
    airport_code1 = code1.strip().upper()
    airport_code2 = code2.strip().upper()
    try:
      distance=calculate_distance(airport_code1, airport_code2)
      if check_same_country(airport_code1,airport_code2):
        ef1=ef.iloc[0][5]#domestic
      elif distance<3700:
        ef1=ef.iloc[1][5]#short haul
      else:ef1=ef.iloc[2][5]#long haul
    except:
      st.write("Timed out or error extracting data of one or both airports, or airport doesn't exist")
  aircraft1=pandas.DataFrame()
  aircraft=st.text_input("Enter the aircraft, please enter the company name e.g. Airbus A340-500, Antonov An-225, Boeing 747-400 ")
  if aircraft:
    aircraft1=w[w["Type"]==aircraft]
  if aircraft1.empty:
    st.write("No aircraft found")
  else:
    percent=st.text_input("enter % of takeoff weight ")
    if percent:
      percent=min(float(percent),100)
      weight=aircraft1.iloc[0][1]*percent/100
      st.write("the weight of the aircraft is",round(weight,1),"kg")
      co2=weight*distance*ef1
      st.write("CO2 Emission:",round(co2/1000,1),"kg")
      st.write("This is equivalent to:")
      co2/=1000000
      st.write(round(co2*370.37,1),"kg of rice")
      st.write(round(co2*16.67,2),"kg of beef")
      st.write(round(co2*833.33,1),"liters of milk")
      st.write(round(co2*0.8,3),"hectares of cropland of fertilizer")
