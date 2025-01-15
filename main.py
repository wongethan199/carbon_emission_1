import streamlit as st
import searoute as sr
import pandas
import csv
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)# remove iloc warnings when getting distance
pandas.set_option('display.max_rows', None)
x=pandas.read_csv("https://raw.githubusercontent.com/wongethan199/carbon_emission_1/main/ESG%20-%20Data%20sheet%20air%20freight%20shipping%20hubs.xlsx%20-%20Main%20-%20Air%20shipping.csv")#distance
y=pandas.read_csv("https://raw.githubusercontent.com/wongethan199/carbon_emission_1/refs/heads/main/ESG%20-%20Data%20sheet%20sea%20freight.xlsx%20-%20Carbon%20footprints%20counting.csv")
ef=pandas.read_csv("https://raw.githubusercontent.com/wongethan199/carbon_emission_1/refs/heads/main/ESG%20-%20Data%20sheet%20air%20freight%20shipping%20hubs.xlsx%20-%20Sheet1.csv")
w=pandas.read_csv("https://raw.githubusercontent.com/wongethan199/carbon_emission_1/refs/heads/main/aircraft%20weight.csv")
import searoute as sr
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
def get_airport_coordinates(airport_code):
  geolocator=Nominatim(user_agent="airport_distance_calculator")
  try:
    location=geolocator.geocode(f"{airport_code} airport")
    if location:
      return(location.latitude,location.longitude)
    else:
      return None
  except:
    return None
def get_airport_country(airport_code):
  geolocator=Nominatim(user_agent="airport_country_checker")
  try:
    location=geolocator.geocode(f"{airport_code} airport")
    if location:
      address=location.raw.get('display_name','')
      return address.split(",")[-1].strip()
    else:
      return None
  except:
    return None
def calculate_distance(airport_code1, airport_code2):
  coords1=get_airport_coordinates(airport_code1)
  coords2=get_airport_coordinates(airport_code2)
  if coords1 and coords2:
    distance=geodesic(coords1, coords2).kilometers
    st.write("Distance:",round(distance),'km')
    return distance
def check_same_country(airport_code1, airport_code2):
  country1=get_airport_country(airport_code1)
  country2=get_airport_country(airport_code2)
  return (country1 and country2) and country1==country2
st.header("Carbon Emission Calculator")
choice=st.text_input("Enter 0 for air(Default) and 1 for sea: ")
if choice=='1':
  st.write("Current mode: Sea")
  database=st.text_input("Enter mode: 0: Database (Default, only supports Vietnam as end) 1: Coordinates")  
  if database=='0' or not database:
  #sea route if data in csv
    seaports0=y[y.columns[2]].values.tolist()
    seaports0=[str(i[8:]) for i in seaports0]
    seaports1=y[y.columns[4]].values.tolist()
    seaports1=[str(i[8:]) for i in seaports1]
    y["Codes_Starting"]=seaports0
    y["Codes_Ending"]=seaports1
    start=st.text_input("Enter start country")
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
        code1=st.text_input("Enter port code 1:")
        code2=st.text_input("Enter port code 2:")
      if code1 and code2:
        target=target[target["Codes_Starting"].str.lower()==code1.lower().strip()]
        target=target[target["Codes_Ending"].str.lower()==code2.lower().strip()]
        if target.empty:
          st.write("Not Found")
        else:
          distance=target.iloc[0][8]
          st.write("Distance:",round(distance),'km')
          try:
            teu=int(st.text_input("Enter TEU capacity:"))
          except:
            teu=24000
          try:
            percent=float(st.text_input("Enter % of teu capacity: Default 70: "))
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
            ref_teu=int(st.text_input("Enter refrigerated teu capacity, default 800:"))
          except:
            ref_teu=800
          ref_teu=min(ref_teu,teu)
          weight=teu*24*percent/100 #using 24000kg per teu: https://oneworldcourier.com.au/what-is-a-teu-shipping-container/
          st.markdown(":red[Warning: Only fill one of the below 2]")
          speed=st.text_input("Enter speed in knots")
          days=st.text_input("enter number of days you expect your shipment to arrive")
          if speed and days:
            st.write("You entered both speed and days, it is impossible to calculate it")
          elif speed:
            speed=float(speed)
            days=distance/(speed*1.852)/24
            st.write('Days',days)
            ref_consum=ref_teu*0.75*days*24
            st.write("Refrigerator fuel consumption",round(ref_consum*0.9,2),'kg')
            co2=weight*distance*ef2*(speed/21)**2/1000+ref_consum*3.15
            st.write("CO2 Emission:",round(co2,1),"kg")
            co2/=1000
            st.write("This is equivalent to:",round(co2*370.37,1),"kg of rice,",round(co2*16.67,2),"kg of beef,",round(co2*833.33,1),"liters of milk, or",round(co2*0.8,4),"hectares of cropland of fertilizer")
            dry_intensity=ef2/126.85*(speed/21)**2/teu/(percent/100)*1000000
            st.write("Dry Container Emission Intensity:",dry_intensity)
            ref_intensity=dry_intensity+ef2*ref_consum/distance/(percent/100)/teu
            st.write("Refrigerated Container Emission Intensity",ref_intensity)
          elif days:
            days=float(days)
            speed=distance/(days*24)/1.852
            st.write("Speed",speed,"knots")
            ref_consum=ref_teu*0.75*days*24#ref_teu*1.9*1914/365*days_operated
            st.write("Refrigerator fuel consumption",round(ref_consum*0.9,2),'kg')
            co2=weight*distance*ef2*(speed/21)**2/1000+ref_consum*3.15
            st.write("CO2 Emission:",round(co2,1),"kg")
            co2/=1000
            st.write("This is equivalent to:",round(co2*370.37,1),"kg of rice,",round(co2*16.67,2),"kg of beef,",round(co2*833.33,1),"liters of milk, or",round(co2*0.8,4),"hectares of cropland of fertilizer")
            dry_intensity=ef2/126.85*(speed/21)**2/teu/(percent/100)*1000000
            st.write("Dry Container Emission Intensity:",dry_intensity)
            ref_intensity=dry_intensity+ef2*ref_consum/distance/(percent/100)/teu
            st.write("Refrigerated Container Emission Intensity",ref_intensity)     
  else:
    lat1=st.text_input("Latitude 1 (-90 to 90): ")
    long1=st.text_input("Longitude 1 (-180 to 180):")
    lat2=st.text_input("Latitude 2 (-90 to 90):")
    long2=st.text_input("Longitude 2 (-180 to 180): ")
    lst=[long1,lat1,long2,lat2]
    if all(lst):
      lst=[float(i)for i in lst]
      orig=lst[:2]
      dest=lst[2:]
      route=sr.searoute(orig,dest)
      distance=route.properties['length']
      if distance==0:
        st.write("Locations are too close to calculate CO2 emission and emission intensity")
      else:
        st.write("Distance:",round(distance),'km')
        try:
          teu=int(st.text_input("Enter TEU capacity:"))
        except:
          teu=24000
        try:
          percent=float(st.text_input("Enter % of teu capacity: Default 70:"))
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
          ref_teu=int(st.text_input("Enter refrigerated teu capacity, default 800:"))
        except:
          ref_teu=800
        ref_teu=min(ref_teu,teu)
        weight=teu*24*percent/100 #using 24000kg per teu: https://oneworldcourier.com.au/what-is-a-teu-shipping-container/
        st.markdown(":red[Warning: Only fill one of the below 2]")
        speed=st.text_input("Enter speed in knots")
        days=st.text_input("enter number of days you expect your shipment to arrive")
        if speed and days:
          st.write("You entered both speed and days, it is impossible to calculate it")
        elif speed:
          speed=float(speed)
          days=distance/(speed*1.852)/24
          st.write('Days',days)
          ref_consum=ref_teu*0.75*days*24#ref_teu*1.9*1914/365*days_operated
          st.write("Refrigerator fuel consumption",round(ref_consum*0.9,2),'kg')
          co2=weight*distance*ef2*(speed/21)**2/1000+ref_consum*3.15
          st.write("CO2 Emission:",round(co2,1),"kg")
          st.write("This is equivalent to:")
          co2/=1000
          st.write(round(co2*370.37,1),"kg of rice")
          st.write(round(co2*16.67,2),"kg of beef")
          st.write(round(co2*833.33,1),"liters of milk")
          st.write(round(co2*0.8,4),"hectares of cropland of fertilizer")
          dry_intensity=ef2/126.85*(speed/21)**2/teu/(percent/100)*1000000
          st.write("Dry Container Emission Intensity:",dry_intensity)
          ref_intensity=dry_intensity+ef2*ref_consum/distance/(percent/100)/teu
          st.write("Refrigerated Container Emission Intensity",ref_intensity)
        elif days:
          days=float(days)
          speed=distance/(days*24)/1.852
          st.write("Speed",speed,"knots")
          ref_consum=ref_teu*0.75*days*24#ref_teu*1.9*1914/365*days_operated
          st.write("Refrigerator fuel consumption",round(ref_consum*0.9,2),'kg')
          co2=weight*distance*ef2*(speed/21)**2/1000+ref_consum*3.15
          st.write("CO2 Emission:",round(co2,1),"kg")
          co2/=1000
          st.write("This is equivalent to:",round(co2*370.37,1),"kg of rice,",round(co2*16.67,2),"kg of beef,",round(co2*833.33,1),"liters of milk, or",round(co2*0.8,4),"hectares of cropland of fertilizer")
          dry_intensity=ef2/126.85*(speed/21)**2/teu/(percent/100)*1000000
          st.write("Dry Container Emission Intensity:",dry_intensity)
          ref_intensity=dry_intensity+ef2*ref_consum/distance/(percent/100)/teu
          st.write("Refrigerated Container Emission Intensity",ref_intensity)
        elif days:
          days=float(days)
          speed=distance/(days*24)/1.852
          st.write("Speed",speed)
          ref_consum=ref_teu*0.75*days*24#ref_teu*1.9*1914/365*days_operated
          st.write("Refrigerator fuel consumption",round(ref_consum*0.9,2),'kg')
          co2=weight*distance*ef2*(speed/21)**2/1000+ref_consum/1000*3.15
          st.write("CO2 Emission:",round(co2,1),"kg")
          co2/=1000
          st.write("This is equivalent to:",round(co2*370.37,1),"kg of rice,",round(co2*16.67,2),"kg of beef,",round(co2*833.33,1),"liters of milk, or",round(co2*0.8,4),"hectares of cropland of fertilizer")
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
  start=st.text_input("Enter country 1")
  end=st.text_input("Enter country 2")
  ef1=0
  if start and end:
    start=start.lower().strip()
    end=end.lower().strip()
    target=x[(x["Starting_Point"].str.lower()==start)|(x["Starting_Point"].str.lower()==end)]
    if end=="united states" or end=="us" or start=="united states" or start=="us":
      target=target[(target["Ending_Point"]=="US")|(target["Ending_Point"]=="United States")|(target["Starting_Point"]=="US")|(target["Starting_Point"]=="United States")]
    else:
      target=target[(target["Ending_Point"].str.lower()==end)|(target["Ending_Point"].str.lower()==start)]
    if start!=end:
      target=target[target["Ending_Point"].str.lower()!=target["Starting_Point"].str.lower()]
    if target.empty:
      not_found=1
      st.write("Not Found, will use geopy")
    else:
      st.write("Available Airport codes:")
      st.write(target.drop_duplicates(subset=['Distance'])[["Codes_Starting","Codes_Ending"]])
      if len(target.drop_duplicates(subset=['Distance'])[["Codes_Starting","Codes_Ending"]])==1:
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
    if 0==not_found:
      distance=target.iloc[0][5]
      st.write("Distance:",distance,'km')
      if start==end:
        ef1=ef.iloc[0][5]
      else:
        if distance<3700:
          ef1=ef.iloc[1][5]
        else:ef1=ef.iloc[2][5]
    else:
      if code1=="" or code2=="":
        code1=st.text_input("Enter port code 1:")
        code2=st.text_input("Enter port code 2:")
      airport_code1=code1.strip().upper()
      airport_code2=code2.strip().upper()
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
    aircraft=st.text_input("Enter the aircraft, please enter the company name e.g. Airbus A340-500, Antonov An-225, Boeing 747-400")
    if aircraft:
      aircraft1=w[w["Type"].str.lower()==aircraft.lower().strip()]
    if aircraft1.empty:
      st.write("No aircraft found")
    else:
      percent=st.text_input("enter % of maximum takeoff weight (Minimum 40)")
      if percent:
        percent=max(min(float(percent),100),40)
        weight=aircraft1.iloc[0][1]*percent/100
        st.write("the weight of the aircraft is",round(weight,1),"kg")
        co2=weight*distance*ef1
        st.write("CO2 Emission:",round(co2/1000,1),"kg")
        co2/=1000000
        st.write("This is equivalent to:",round(co2*370.37,1),"kg of rice,",round(co2*16.67,2),"kg of beef,",round(co2*833.33,1),"liters of milk, or",round(co2*0.8,4),"hectares of cropland of fertilizer")
