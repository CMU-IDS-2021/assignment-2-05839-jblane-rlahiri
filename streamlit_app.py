import streamlit as st
import pandas as pd
import altair as alt
from datetime import date
import covidcast
import pandasql

# Deliverables
#  An interactive data science or machine learning application using Streamlit.
#  The URL at the top of this readme needs to point to your application online. It should also list the names of the team members.
#  A write-up that describes the goals of your application, justifies design decisions, and gives an overview of your development process. Use the writeup.md file in this repository. You may add more sections to the document than the template has right now.


#st.title("Let's analyze some Penguin Data 🐧📊.") #how did he get this emoji on here?!
st.title("Public Behaviour Analysis in Covid-19 from 1st October 2020 to 1st March 2021 for PA 📊")

# Seems like there's some real delay in fetching 6 months of data so to build the skeletal model considered 2 months, even pre-downloading CSV isn't working well, We'll figure out someway to include 6 months later.

@st.cache
def fetch(dat):
    if(dat==1):
    # safegraph: The fraction of devices that spent between 3 and 6 hours at a location other than their home during the daytime
        data1 = covidcast.signal("safegraph", "part_time_work_prop", date(2020, 10, 1), date(2020, 12, 1), "county")
    #safegraph: The fraction of mobile devices that spent more than 6 hours at a location other than their home during the daytime
    elif(dat==2):
        data1 = covidcast.signal("safegraph", "full_time_work_prop", date(2020, 10, 1), date(2020, 12, 1), "county")
    #safegraph: The number of daily visits made by those with SafeGraph’s apps to bar-related POIs in a certain region, per 100,000 population
    elif(dat==3):
        data1 = covidcast.signal("safegraph", "bars_visit_prop", date(2020, 10, 1), date(2020, 12, 1), "county")
    #safegraph: The number of daily visits made by those with SafeGraph’s apps to restaurant-related POIs in a certain region, per 100,000 population
    elif(dat==4):
        data1 = covidcast.signal("safegraph", "restaurants_visit_prop",date(2020, 10, 1), date(2020, 12, 1), "county")

    #fb-survey: Estimated percentage of people reporting illness in their local community, including their household, with no survey weighting
    elif(dat==5):    
        data1 = covidcast.signal("fb-survey", "smoothed_hh_cmnty_cli", date(2020, 10, 1), date(2020, 12, 1), "county")
    
    #fb-survey: Estimated percentage of respondents who reported feeling very or somewhat worried that “you or someone in your immediate family might become seriously ill from COVID-19”
    elif(dat==6):
        data1 = covidcast.signal("fb-survey", "smoothed_worried_become_ill", date(2020, 10, 1), date(2020, 12, 1), "county")
    
    #fb-survey: Estimated percentage of people with COVID-like illness, with no survey weighting
    elif(dat==7):
        data1 = covidcast.signal("fb-survey", "smoothed_cli",date(2020, 10, 1), date(2020, 12, 1), "county")
    
    else:
        data1= covidcast.signal("doctor-visits", "smoothed_cli",date(2020, 10, 1), date(2020, 12, 1), "county")
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

    
input_drop=alt.binding_select(options=(list(county_details.values())),name="Select County by FIPS code")
picked=alt.selection_single(encodings=["color"],bind=input_drop) 
scatter=alt.Chart(data_barvis_PA).mark_line().encode(
    x=alt.X("monthdate(time_value):O"),

    y=alt.Y("value:Q",axis=alt.Axis(title='Average number of daily bar visits')),
    tooltip=['geo_value','monthdate(time_value)','value'],

    color=alt.condition(picked,'geo_value',alt.value('lightgray')),
    
    ).add_selection(picked).properties(width=800,height=400)
st.write(scatter)

#--Doctor's visits
doctorVisitsdf = pd.read_csv("doctorVisits.csv")
#PAcountiesdf = (doctorVisitsdf['geo_value'] >= 42000) & (doctorVisitsdf['geo_value' < 43000])
PAcounties = alt.FieldRangePredicate(field='geo_value',range=[42000,43000])
#input_dropdown = alt.binding_select(options=PAcounties,name="Select County")
brush = alt.selection_interval()

chart = alt.Chart(doctorVisitsdf).mark_line().encode(
    x=alt.X('monthdate(time_value):O',axis=alt.Axis(title="Date")),
    y=alt.Y('value:Q',axis=alt.Axis(title="Indicator Value")),
    color=alt.condition(brush, 'geo_value:N', alt.value('lightgray'))
).properties(
    width=500,height=400,title="Reporting Illness in Community over Time"
).transform_filter(
    PAcounties
).add_selection(
    brush
)
    
# st.write(chart)

#https://altair-viz.github.io/gallery/layered_chart_with_dual_axis.html
#alt.layer(chart1,chart2).resolve_scale(
#   y='independent'
#)

