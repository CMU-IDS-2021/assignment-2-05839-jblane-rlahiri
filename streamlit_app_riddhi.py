import streamlit as st
import pandas as pd
import altair as alt
from datetime import date
import covidcast
import pandasql
from geopy.geocoders import Nominatim
# Deliverables
#  An interactive data science or machine learning application using Streamlit.
#  The URL at the top of this readme needs to point to your application online. It should also list the names of the team members.
#  A write-up that describes the goals of your application, justifies design decisions, and gives an overview of your development process. Use the writeup.md file in this repository. You may add more sections to the document than the template has right now.


#st.title("Let's analyze some Penguin Data 🐧📊.") #how did he get this emoji on here?!
st.title("Public Behaviour Analysis in Covid-19 from 1st October 2020 to 31st December 2020 for PA 📊")

@st.cache
def fetch(dat):
    if(dat==1):
    # safegraph: The fraction of devices that spent between 3 and 6 hours at a location other than their home during the daytime
        data1 = covidcast.signal("safegraph", "part_time_work_prop", date(2020, 10, 1), date(2020, 12, 31), "county")
    #safegraph: The fraction of mobile devices that spent more than 6 hours at a location other than their home during the daytime
    elif(dat==2):
        data1 = covidcast.signal("safegraph", "full_time_work_prop", date(2020, 10, 1), date(2020, 12, 31), "county")
    #safegraph: The number of daily visits made by those with SafeGraph’s apps to bar-related POIs in a certain region, per 100,000 population
    elif(dat==3):
        data1 = covidcast.signal("safegraph", "bars_visit_prop", date(2020, 10, 1), date(2020, 12, 31), "county")
    #safegraph: The number of daily visits made by those with SafeGraph’s apps to restaurant-related POIs in a certain region, per 100,000 population
    elif(dat==4):
        data1 = covidcast.signal("safegraph", "restaurants_visit_prop",date(2020, 10, 1), date(2020, 12, 31), "county")

    #fb-survey: Estimated percentage of people reporting illness in their local community, including their household, with no survey weighting
    elif(dat==5):    
        data1 = covidcast.signal("fb-survey", "smoothed_hh_cmnty_cli", date(2020, 10, 1), date(2020, 12, 31), "county")
    
    #fb-survey: Estimated percentage of respondents who reported feeling very or somewhat worried that “you or someone in your immediate family might become seriously ill from COVID-19”
    elif(dat==6):
        data1 = covidcast.signal("fb-survey", "smoothed_worried_become_ill", date(2020, 10, 1), date(2020, 12, 31), "county")
    
    #fb-survey: Estimated percentage of people with COVID-like illness, with no survey weighting
    elif(dat==7):
        data1 = covidcast.signal("fb-survey", "smoothed_cli",date(2020, 10, 1), date(2020, 12, 31), "county")
    
    else:
        data1= covidcast.signal("doctor-visits", "smoothed_cli",date(2020, 10, 1), date(2020, 12, 31), "county")
    return data1

  
data=fetch(3)
data_barvis_PA = pandasql.sqldf("select * from data where geo_value like '42%'")
if st.checkbox("Display raw data"):
    st.write(data_barvis_PA)
    
county_data=pandasql.sqldf("select distinct geo_value from data_barvis_PA")
county_details=dict()
print(county_data.shape[0])
l=county_data["geo_value"].tolist()
print(str(covidcast.fips_to_name(county_data.iloc[1])))
for i in range(county_data.shape[0]):
    county_details.update({str(covidcast.fips_to_name(county_data.iloc[i]))[2:len(str(covidcast.fips_to_name(county_data.iloc[i])))-2]:l[i]})

    
input_drop=alt.binding_select(options=(list(county_details.values())),name="Select County to Highlight data for Bar visits")
picked=alt.selection_single(encodings=["color"],bind=input_drop) 
scatter=alt.Chart(data_barvis_PA).mark_line().encode(
    x=alt.X("monthdate(time_value):O"),

    y=alt.Y("value:Q",axis=alt.Axis(title='Average number of daily bar visits')),
    tooltip=['geo_value','monthdate(time_value)','value'],

    color=alt.condition(picked,'geo_value',alt.value('lightgray')),
    opacity=alt.condition(picked,alt.value(1),alt.value(0.05))
    ).add_selection(picked).properties(width=800,height=400).interactive()



data=fetch(4)

data3_6hr = pandasql.sqldf("select * from data where geo_value like '42%'")

county_data=pandasql.sqldf("select distinct geo_value from data3_6hr")
county_details=dict()
print(county_data.shape[0])
l=county_data["geo_value"].tolist()
print(str(covidcast.fips_to_name(county_data.iloc[1])))
for i in range(county_data.shape[0]):
    county_details.update({str(covidcast.fips_to_name(county_data.iloc[i]))[2:len(str(covidcast.fips_to_name(county_data.iloc[i])))-2]:l[i]})
  
input_drop=alt.binding_select(options=(list(county_details.values())),name="Select County to Highlight data for Restaurant visits")
picked=alt.selection_single(encodings=["color"],bind=input_drop) 


bar_dataPA=data3_6hr = pandasql.sqldf("select * from data where geo_value like '42%'")

scatter1=alt.Chart(bar_dataPA).mark_line(point=True).encode(
    x=alt.X("monthdate(time_value):O"),
    
    y=alt.Y("value:Q",axis=alt.Axis(title='Average number of daily bar visits')),
    tooltip=['geo_value','monthdate(time_value)','value'],
    
    color=alt.condition(picked,'geo_value',alt.value('lightgray')),
    opacity=alt.condition(picked,alt.value(1),alt.value(0.05))
    
    ).add_selection(picked).properties(width=800,height=400,title="Percentage of people spending 3-6 hours outside").interactive()

st.write(scatter1+scatter)


# Call the function with the dataset to get a plot on Pennsylvania
def plot_on_PA(bar_dataPA):
    from vega_datasets import data
    counties = alt.topo_feature(data.us_10m.url, 'counties')
    bar_dataPA=pandasql.sqldf("select * from bar_dataPA where geo_value like '42%'")
    county_data=pandasql.sqldf("select distinct geo_value from bar_dataPA")
    county_details=dict()

    l=county_data["geo_value"].tolist()

    for i in range(county_data.shape[0]):
        county_details.update({str(covidcast.fips_to_name(county_data.iloc[i]))[2:len(str(covidcast.fips_to_name(county_data.iloc[i])))-2]:l[i]})

    data6hrs = pandasql.sqldf("select * from bar_dataPA where geo_value like '42%'")

    map_pennsylvania =(
    alt.Chart(data = counties,
              )
    .mark_geoshape(
        stroke='black',
        strokeWidth=1,
        fill='lightyellow'
    )
    .transform_calculate(state_id = "(datum.id / 1000)|0")
    .transform_filter((alt.datum.state_id)==42)
    .transform_lookup(
        lookup='data6hrs',
        from_=alt.LookupData(data6hrs,'geo_value',['value']),
        
         
        ).properties(width=500,height=400)
    )

    geolocator = Nominatim(user_agent="streamlit_app.py")

    lat=[]
    lon=[]
    coun=[]
    @st.cache
    def sw():
        lsd={}
        for i in county_details.keys():
            sss=i+", PA"
            y=geolocator.geocode(sss)
            r=[y.latitude,y.longitude]
            lat.append(y.latitude)
            #st.write(y.latitude)
            lon.append(y.longitude)
            coun.append(county_details[i])
            lsd.update({county_details[i]:r})
        return lat,lon,coun

    [lat,lon,coun]=sw()
    det={'County':coun,'Latitude':lat,'Longitude':lon}

    gb=pd.DataFrame(det)

    bar_dataPA['time_value']=bar_dataPA['time_value'].str.slice(0, 10) 
    kal=pandasql.sqldf("select bar_dataPA.geo_value,bar_dataPA.time_value,bar_dataPA.value,gb.Latitude,gb.Longitude from bar_dataPA,gb where gb.County=bar_dataPA.geo_value")

    dg=pandasql.sqldf("select distinct time_value from kal")

    input_drop=alt.binding_select(options=dg['time_value'].tolist(),name="Select Date")
    picked=alt.selection_single(encodings=["color"],bind=input_drop) 

    points = alt.Chart(kal).mark_circle().encode(
        longitude='Longitude:Q',
        latitude='Latitude:Q',
        size='value:Q',
        color=alt.condition(picked,'time_value',alt.value('lightgray'), legend=None),
        opacity=alt.condition(picked,alt.value(0.5),alt.value(0)),


        tooltip=['geo_value','value']
    ).add_selection(picked).transform_filter(picked).properties(width=500,height=400)

    st.write(map_pennsylvania+points)

st.write("Shown below is the Distribution of Restaurant Visits on the Map of Pennsylvania, Please select a Date to view the distribution on a particular Date")
#plot_on_PA(bar_dataPA)

my_button = st.radio("Please Select an Option to see the Distribution on the Pennsylvania Map", ('Show the distribution of Bar visits','Show the distribution of Restaurant visits', 'Show the distribution of people staying 3-6 hours away from home','Show the distribution of people staying greater than 6 hours away from home')) 
if my_button=='Show the distribution of Bar visits':
    plot_on_PA(fetch(3))
elif my_button=='Show the distribution of Restaurant visits':
    plot_on_PA(fetch(4))
elif my_button=='Show the distribution of people staying 3-6 hours away from home':
    plot_on_PA(fetch(1))
else:
     plot_on_PA(fetch(2))







# #--Doctor's visits
# doctorVisitsdf = pd.read_csv("doctorVisits.csv")
# #PAcountiesdf = (doctorVisitsdf['geo_value'] >= 42000) & (doctorVisitsdf['geo_value' < 43000])
# PAcounties = alt.FieldRangePredicate(field='geo_value',range=[42000,43000])
# #input_dropdown = alt.binding_select(options=PAcounties,name="Select County")
# brush = alt.selection_interval()

# chart = alt.Chart(doctorVisitsdf).mark_line().encode(
#     x=alt.X('monthdate(time_value):O',axis=alt.Axis(title="Date")),
#     y=alt.Y('value:Q',axis=alt.Axis(title="Indicator Value")),
#     color=alt.condition(brush, 'geo_value:N', alt.value('lightgray')),
   
# ).properties(
#     width=500,height=400,title="Reporting Illness in Community over Time"
# ).transform_filter(
#     PAcounties
# ).add_selection(
#     brush
# )
    
# st.write(chart)

#https://altair-viz.github.io/gallery/layered_chart_with_dual_axis.html
#alt.layer(chart1,chart2).resolve_scale(
#   y='independent'
#)

