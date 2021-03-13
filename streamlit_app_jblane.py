import streamlit as st
import pandas as pd
import altair as alt
from datetime import date
import covidcast
import pandasql
from geopy.geocoders import Nominatim


st.title("Public Behaviour Analysis in Covid-19 in PA (November 1, 2020 to December 31, 2020)📊")
# streamlit run streamlit_app_jblane.py


#PREP----Pull data from COVID just to get the csv files----
@st.cache
def fetch(dat):

    #safegraph: The number of daily visits made by those with SafeGraph’s apps to bar-related POIs in a certain region, per 100,000 population
    if(dat==3):
        data1 = covidcast.signal("safegraph", "bars_visit_prop", date(2020, 10, 1), date(2020, 12, 31), "county")
    #safegraph: The number of daily visits made by those with SafeGraph’s apps to restaurant-related POIs in a certain region, per 100,000 population
    elif(dat==4):
        data1 = covidcast.signal("safegraph", "restaurants_visit_prop",date(2020, 10, 1), date(2020, 12, 31), "county")

    #fb-survey: Estimated percentage of people reporting illness in their local community, including their household, with no survey weighting
    elif(dat==5):    
        data1 = covidcast.signal("fb-survey", "smoothed_hh_cmnty_cli", date(2020, 10, 1), date(2020, 12, 31), "county")
    
    else:#(dat == 6)
    #fb-survey: Estimated percentage of respondents who reported feeling very or somewhat worried that “you or someone in your immediate family might become seriously ill from COVID-19”
        data1 = covidcast.signal("fb-survey", "smoothed_worried_become_ill", date(2020, 10, 1), date(2020, 12, 31), "county")
    return data1

# #PREP #--Pull data-----Used in csv file process

barData = fetch(3)
restaurantData = fetch(4)
commWorry = fetch(5)
selfWorry = fetch(6)

# #PREP--Convert to csv----Used in csv file process

# barData.to_csv("barData.csv")
# restaurantData.to_csv("restaurantData.csv")
# commWorry.to_csv("commWorry.csv")
# selfWorry.to_csv("selfWorry.csv")

#--create df from csv files, keep desired columns, combine counties with FIPS-- This is different from pulling it off the covidcast server
@st.cache
def createCsvDf(valueCSVfile): #given filename for metric csv file
    fipsData = pd.read_csv("Fips_countyname.csv") #list of county names and fips to dataframe (cite: https://github.com/kjhealy/fips-codes)
    finalDf = pd.read_csv(valueCSVfile) #metric csv file to dataframe
    finalDf = finalDf[['geo_value','time_value','value']] #keep desired columns
    finalDf = pd.merge(finalDf,fipsData, on = "geo_value",how="left") #add county names to fips, left join tables
    finalDf.drop(finalDf[finalDf['state'] != 'PA'].index, inplace = True) #keep PA counties
    return finalDf

#---define variables

barDatadf = createCsvDf("barData.csv")
restaurantDatadf = createCsvDf("restaurantData.csv")
commWorrydf = createCsvDf("commWorry.csv")
selfWorrydf = createCsvDf("selfWorry.csv")
countyList = set(list(barDatadf['name'])+list(restaurantDatadf['name'])+list(commWorrydf['name'])+list(selfWorrydf['name']))
# countyList = countyList.sort()


#Make clean csv's with fips, county names, and just PA
barDatadf.to_csv("barData2.csv")
restaurantDatadf.to_csv("restaurantData2.csv")
commWorrydf.to_csv("commWorry2.csv")
selfWorrydf.to_csv("selfWorry2.csv")


# #---create map-----
# def plot_on_PA(bar_dataPA):
#     from vega_datasets import data
#     counties = alt.topo_feature(data.us_10m.url, 'counties')
#     bar_dataPA=pandasql.sqldf("select * from bar_dataPA where geo_value like '42%'")
#     county_data=pandasql.sqldf("select distinct geo_value from bar_dataPA")
#     county_details=dict()

#     l=county_data["geo_value"].tolist()

#     for i in range(county_data.shape[0]):
#         county_details.update({str(covidcast.fips_to_name(county_data.iloc[i]))[2:len(str(covidcast.fips_to_name(county_data.iloc[i])))-2]:l[i]})

#     data6hrs = pandasql.sqldf("select * from bar_dataPA where geo_value like '42%'")

#     map_pennsylvania =(
#     alt.Chart(data = counties,
#               )
#     .mark_geoshape(
#         stroke='black',
#         strokeWidth=1,
#         fill='lightyellow'
#     )
#     .transform_calculate(state_id = "(datum.id / 1000)|0")
#     .transform_filter((alt.datum.state_id)==42)
#     .transform_lookup(
#         lookup='data6hrs',
#         from_=alt.LookupData(data6hrs,'geo_value',['value']),
        
         
#         ).properties(width=500,height=400)
#     )

#     geolocator = Nominatim(user_agent="streamlit_app.py")

#     lat=[]
#     lon=[]
#     coun=[]
#     @st.cache
#     def sw():
#         lsd={}
#         for i in county_details.keys():
#             sss=i+", PA"
#             y=geolocator.geocode(sss)
#             r=[y.latitude,y.longitude]
#             lat.append(y.latitude)
#             #st.write(y.latitude)
#             lon.append(y.longitude)
#             coun.append(county_details[i])
#             lsd.update({county_details[i]:r})
#         return lat,lon,coun

#     [lat,lon,coun]=sw()
#     det={'County':coun,'Latitude':lat,'Longitude':lon}

#     gb=pd.DataFrame(det)

#     bar_dataPA['time_value']=bar_dataPA['time_value'].str.slice(0, 10) 
#     kal=pandasql.sqldf("select bar_dataPA.geo_value,bar_dataPA.time_value,bar_dataPA.value,gb.Latitude,gb.Longitude from bar_dataPA,gb where gb.County=bar_dataPA.geo_value")

#     dg=pandasql.sqldf("select distinct time_value from kal")

#     input_drop=alt.binding_select(options=dg['time_value'].tolist(),name="Select Date")
#     picked=alt.selection_single(encodings=["color"],bind=input_drop) 

#     points = alt.Chart(kal).mark_circle().encode(
#         longitude='Longitude:Q',
#         latitude='Latitude:Q',
#         size='value:Q',
#         color=alt.condition(picked,'time_value',alt.value('lightgray'), legend=None),
#         opacity=alt.condition(picked,alt.value(0.5),alt.value(0)),


#         tooltip=['geo_value','value']
#     ).add_selection(picked).transform_filter(picked).properties(width=500,height=400)

#     st.write(map_pennsylvania+points)

# st.write("Shown below is the Distribution of Restaurant Visits on the Map of Pennsylvania, Please select a Date to view the distribution on a particular Date")
# #plot_on_PA(bar_dataPA)

# my_button = st.radio("Please Select an Option to see the Distribution on the Pennsylvania Map", ('Show the distribution of Bar visits','Show the distribution of Restaurant visits', 'Show the distribution of people staying 3-6 hours away from home','Show the distribution of people staying greater than 6 hours away from home')) 
# if my_button=='Show the distribution of Bar visits':
#     plot_on_PA(barData)
# elif my_button=='Show the distribution of Restaurant visits':
#     plot_on_PA(restaurantData)
# elif my_button=='Show the distribution of people staying 3-6 hours away from home':
#     plot_on_PA(commWorry)
# else:
#     plot_on_PA(selfWorry)






#---Select County Dropdown--
county_dropdown = alt.binding_select(options=list(set(countyList)))
selectedCounty = alt.selection_single(fields=['name'],bind=county_dropdown, name='PA County:')

#---brush select area to focus on
brush = alt.selection(type = 'interval',encodings=['x'])

#---slider select for date


#---commWorry chart
commWorryChart = alt.Chart(commWorrydf).mark_area(color='red').encode(
    alt.X("monthdate(time_value):T",axis=alt.Axis(title='Date')),
    alt.Y("value:Q",axis=alt.Axis(title='Percentage of people')),
    tooltip=[alt.Tooltip('geo_value',title = 'FIPS'),alt.Tooltip('monthdate(time_value)',title = 'date'), alt.Tooltip('value',title='Value')],
    # color=alt.condition(brush, 'Cylinders:O', alt.value('lightgray')),
    #opacity=alt.condition(selectedCounty,alt.value(1),alt.value(0.05))
    
    # ).add_selection(
    #     selectedCounty,
    #     brush
    ).transform_filter(
        selectedCounty
    ).properties(width=600,height=200,title="Percent of People who know someone with COVID-like symptoms")

# st.write(commWorryChart)

#--selfWorry chart

selfWorryChart = alt.Chart(selfWorrydf).mark_area(color='purple').encode(
    alt.X("monthdate(time_value):T",axis=alt.Axis(title='Date')),
    alt.Y("value:Q",axis=alt.Axis(title='Percentage of people')),
    tooltip=[alt.Tooltip('geo_value',title = 'FIPS'),alt.Tooltip('monthdate(time_value)',title = 'date'), alt.Tooltip('value',title='Value')],
    # color=alt.condition(brush, 'Cylinders:O', alt.value('lightgray')),
    #opacity=alt.condition(selectedCounty,alt.value(1),alt.value(0.05))
    
    # ).add_selection(
    #     selectedCounty,
    #     brush
     ).transform_filter(
         selectedCounty
     ).properties(width=600,height=200,title="Percent of People who are afraid they or someone they know will become seriously ill from COVID-19 ")

# st.write(selfWorryChart)

#--barData chart
barDataChart = alt.Chart(barDatadf).mark_line(color = 'green').encode(
    alt.X("monthdate(time_value):T",axis=alt.Axis(title='Date'),scale=alt.Scale(domain=brush)),
    alt.Y("value:Q",axis=alt.Axis(title='Percentage of people')),
    tooltip=[alt.Tooltip('geo_value',title = 'FIPS'),alt.Tooltip('monthdate(time_value)',title = 'date'), alt.Tooltip('value',title='Value')],
    # color=alt.condition(brush, 'Cylinders:O', alt.value('lightgray')),
    #opacity=alt.condition(selectedCounty,alt.value(1),alt.value(0.05))
    
    # ).add_selection(
    #     selectedCounty, 
    #     brush
    ).transform_filter(
        selectedCounty
    ).properties(width=600,height=200,title="Number of people visiting bars")

# st.write(barDataChart)

#--restaurant data chart
restaurantDataChart = alt.Chart(restaurantDatadf).mark_line( color = 'blue').encode(
    alt.X("monthdate(time_value):T",axis=alt.Axis(title='Date'),scale=alt.Scale(domain=brush)),
    alt.Y("value:Q",axis=alt.Axis(title='Percentage of people')),
    tooltip=[alt.Tooltip('geo_value',title = 'FIPS'),alt.Tooltip('monthdate(time_value)',title = 'date'), alt.Tooltip('value',title='Value')],
    # color=alt.condition(brush, 'Cylinders:O', alt.value('lightgray')),
    #opacity=alt.condition(selectedCounty,alt.value(1),alt.value(0.05))
    
    # ).add_selection(
    #     selectedCounty,
    #     brush
    ).transform_filter(
        selectedCounty
    ).properties(width=600,height=200,title="Number of people visiting restaurants")

# st.write(restaurantDataChart)


# #--version 1 combine
# emotionalBase = alt.layer(commWorryChart,selfWorryChart).encode(
#     # color=alt.condition(brush, 'Cylinders:O', alt.value('lightgray')),
#     ).add_selection(
#         selectedCounty,
#         brush
#     ).properties(width=500,height=500,title="Percent of People are worried about COVID-19 or know someone with symptoms"
#     # ).transform_calculate(
#     # worryLegend = 
#     )
# # st.write(emotional)

# behavioralBase = alt.layer(barDataChart,restaurantDataChart).encode(
#     alt.X("monthdate(time_value):O",axis=alt.Axis(title='Date'),scale=alt.Scale(domain=brush))
#     ).add_selection(
#         selectedCounty,
#         brush
#     ).properties(width=500,height=500,title="Number of People Going to Bars and Restaurants")
# # st.write(behavioral)

# vCombine = alt.vconcat(emotionalBase,behavioralBase) #vertical concat two combined charts
# st.write(vCombine)

#---version 2 combine
#st.write(commWorryChart|selfWorryChart|barDataChart|restaurantDataChart) #horizontal concat

#---version 3 combine
#st.write(commWorryChart+selfWorryChart) #layer

#---version 4 combine #vertical concat all 4
vconcatChart=alt.vconcat(commWorryChart,selfWorryChart,barDataChart,restaurantDataChart).add_selection(
        selectedCounty,
        brush
        )
st.write(vconcatChart)

    
   #---Show Raw Data data table

#BarData
if st.checkbox("Show me the raw data for bar visits"):
    st.write(barDatadf)    
#RestaurantData
if st.checkbox("Show me the raw data restaurant visits"):
    st.write(restaurantDatadf)
#CommunityWorry Data
if st.checkbox("Show me the raw data worry about illness in community"):
    st.write(commWorrydf)
#SelfWorry Data
if st.checkbox("Show me the raw data becoming ill"):
    st.write(selfWorrydf)
# if st.checkbox("Show me the list of counties"):
#     st.write(countyList)
 





#----------------------------------------------------
# data=fetch(3)
# data_barvis_PA = pandasql.sqldf("select * from data where geo_value like '42%'")
# if st.checkbox("Display raw data"):
#     st.write(data_barvis_PA)
    
# county_data=pandasql.sqldf("select distinct geo_value from data_barvis_PA")
# county_details=dict()
# print(county_data.shape[0])
# l=county_data["geo_value"].tolist()
# print(str(covidcast.fips_to_name(county_data.iloc[1])))
# for i in range(county_data.shape[0]):
#     county_details.update({str(covidcast.fips_to_name(county_data.iloc[i]))[2:len(str(covidcast.fips_to_name(county_data.iloc[i])))-2]:l[i]})

    
# input_drop=alt.binding_select(options=(list(county_details.values())),name="Select County by FIPS code")
# picked=alt.selection_single(encodings=["color"],bind=input_drop) 
# scatter=alt.Chart(data_barvis_PA).mark_line().encode(
#     x=alt.X("monthdate(time_value):O"),

#     y=alt.Y("value:Q",axis=alt.Axis(title='Average number of daily bar visits')),
#     tooltip=['geo_value','monthdate(time_value)','value'],

#     color=alt.condition(picked,'geo_value',alt.value('lightgray')),
    
#     ).add_selection(picked).properties(width=800,height=400)
# st.write(scatter)



##---Early indicators section----
# communityIll = fetch(5)
# worryIll = fetch(6)
# selfIll = fetch(7)
# doctorVisits = fetch(8)

# communityIlldf = pd.read_csv("communityIll.csv")
# worryIlldf = pd.read_csv("worryIll.csv")
# selfIlldf = pd.read_csv("selfIll.csv")
# doctorVisitsdf = pd.read_csv("doctorVisits.csv")
#allIndic = pd.read_csv("allIndic.csv")
# worryIll.to_csv("worryIll.csv")
# selfIll.to_csv("selfIll.csv")
# doctorVisits.to_csv("doctorVisits.csv")
# st.write(communityIll)
# st.write(worryIll)
#write to .csv
#communityIlldf = pd.DataFrame(communityIll)
#communityIlldf.to_csv("communityIll.csv")
#communityIlldf = pd.read_csv("communityIll.csv")
#st.write(communityIlldf)


#---all data
#input_dropdown = alt.binding_select(options=[])
# brush = alt.selection_interval()

# chart1 = alt.Chart(doctorVisitsdf).mark_line().encode(
#     x=alt.X('monthdate(time_value):O',axis=alt.Axis(title="Date")),
#     y=alt.Y('value:Q',axis=alt.Axis(title="Indicator Value")),
#     color=alt.condition(brush, 'geo_value:N', alt.value('lightgray'))
# ).properties(width=500,height=400,title="Reporting Illness in Community over Time"
# ).transform_filter(
#     alt.FieldRangePredicate(field='geo_value',range=[42000,43000])
# ).add_selection(
#     brush
# )

# final = alt.layer(chart1, chart2, chart3, chart4)    
# st.write(chart)

#--Doctor's visits
# #PAcountiesdf = (doctorVisitsdf['geo_value'] >= 42000) & (doctorVisitsdf['geo_value' < 43000])
# PAcounties = alt.FieldRangePredicate(field='geo_value',range=[42000,43000])
# #input_dropdown = alt.binding_select(options=PAcounties,name="Select County")
# brush = alt.selection_interval()

# chart = alt.Chart(doctorVisitsdf).mark_line().encode(
#     x=alt.X('monthdate(time_value):O',axis=alt.Axis(title="Date")),
#     y=alt.Y('value:Q',axis=alt.Axis(title="Indicator Value")),
#     color=alt.condition(brush, 'geo_value:N', alt.value('lightgray'))
# ).properties(
#     width=500,height=400,title="Reporting Illness in Community over Time"
# ).transform_filter(
#     PAcounties
# ).add_selection(
#     brush
# )
    
# st.write(chart)

# #domain = ['Resale', 'No Resale']
# #range_ = ['green', 'red']
# CI=alt.Chart(allIndic).mark_line().encode(
#     x='monthdate(time_value):O',
#     y='indicator_value:Q',
#     color='indicator'
# ).properties(width=500,height=400,title="Reporting Illness in Community over Time")
# st.write(CI)


##---Early indicators section----
# communityIll = fetch(5)
# st.write(communityIll)

#worryIll = fetch(6)
#selfIll = fetch(7)
#doctorVisits = fetch(8)


# domain = ['Resale', 'No Resale']
# range_ = ['green', 'red']
# CI=alt.Chart(communityIll).mark_point().encode(
#     x='Area',
#     y='Price',
#     color=alt.Color('Resale_Value', scale=alt.Scale(domain=domain, range=range_)),
#     tooltip=[alt.Tooltip('Area'),
#             alt.Tooltip('Price'),
#             alt.Tooltip('Resale_Value')]
# ).properties(width=500,height=400,title="Area vs Price against Resale")



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

