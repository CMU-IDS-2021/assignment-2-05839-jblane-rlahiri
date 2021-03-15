import streamlit as st
import pandas as pd
import altair as alt
from datetime import date
import covidcast
import pandasql
from geopy.geocoders import Nominatim

st.title("🦠 Covid-19 Public Behaviour Analysis in PA ")
st.text("(November 1, 2020 to December 31, 2020)")
#--https://share.streamlit.io/cmu-ids-2021/assignment-2-05839-jblane-rlahiri

st.markdown("_**Welcome!**_ COVID-19 has become large part of our every day lives. People walk around in public areas covered in masks trying to maintain a six feet distance away from each other. School attendance is limited in many areas of the country, and some people have not seen grandparents in many months. This past February (2021), the number of U.S. deaths related to COVID-19 exceeded half a million people. There is no wonder that citizens worry about whether or not they or people in their community may contract the virus. With the increasing death toll, though, how worried are people about becoming sick or spreading the sickness to others? Are they worried enough to quarantine themselves, only leaving the home for essential items?" )

st.markdown(" The purpose of this visualization is to take a look at the emotional state of counties within Pennsylvania and compare the information to whether or not this affects overall tendencies to conduct non-essential activities such as going to bars and restaurants.")
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

# barData = fetch(3)
# restaurantData = fetch(4)
# commWorry = fetch(5)
# selfWorry = fetch(6)

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
countyList = list(set(list(barDatadf['name'])+list(restaurantDatadf['name'])+list(commWorrydf['name'])+list(selfWorrydf['name'])))
countyList.sort()




#-------------------------------------------
#--Create PA map
#-------------------------------------------

#TODO - Fix size issue for restaurant visits
#TODO - Changethe bottom two buttons for the emotional datasets
#TODO - See if you can use the csv files instead of fetch


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
        
         
        ).properties(width=700,height=400)
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
    ).add_selection(picked).transform_filter(picked).properties(width=700,height=400)

    st.write(map_pennsylvania+points)
    
    
st.title("PA Map of All Metrics by Date")
st.markdown("**Select a Metric (button) and Date (dropdown)**")
st.markdown("Note: Not all counties have data for each metric for every time period")

#plot_on_PA(bar_dataPA)

my_button = st.radio("COVID-19 Metrics", ('Show the distribution of Bar visits','Show the distribution of Restaurant visits', 'Show the distribution of those reporting illness in the community','Show the distribution of people worried about becoming ill')) 

if my_button == 'Show the distribution of those reporting illness in the community':
    html_commworry="""
    <div class='tableauPlaceholder' id='viz1615794286191' style='position: relative'><noscript><a href='#'><img alt=' ' src='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;6G&#47;6G6YMCGKG&#47;1_rss.png' style='border: none' /></a></noscript><object class='tableauViz'  style='display:none;'><param name='host_url' value='https%3A%2F%2Fpublic.tableau.com%2F' /> <param name='embed_code_version' value='3' /> <param name='path' value='shared&#47;6G6YMCGKG' /> <param name='toolbar' value='yes' /><param name='static_image' value='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;6G&#47;6G6YMCGKG&#47;1.png' /> <param name='animate_transition' value='yes' /><param name='display_static_image' value='yes' /><param name='display_spinner' value='yes' /><param name='display_overlay' value='yes' /><param name='display_count' value='yes' /><param name='language' value='en' /><param name='filter' value='publish=yes' /></object></div>                <script type='text/javascript'>                    var divElement = document.getElementById('viz1615794286191');                    var vizElement = divElement.getElementsByTagName('object')[0];                    if ( divElement.offsetWidth > 800 ) { vizElement.style.width='600px';vizElement.style.height='627px';} else if ( divElement.offsetWidth > 500 ) { vizElement.style.width='600px';vizElement.style.height='627px';} else { vizElement.style.width='100%';vizElement.style.height='727px';}                     var scriptElement = document.createElement('script');                    scriptElement.src = 'https://public.tableau.com/javascripts/api/viz_v1.js';                    vizElement.parentNode.insertBefore(scriptElement, vizElement);                </script>
    """
    st.components.v1.html(html_commworry,width = 600, height= 600)
elif my_button=='Show the distribution of people worried about becoming ill':
    plot_on_PA(fetch(6))
elif my_button=='Show the distribution of Bar visits':
    html_tableau_bar_visits="""
    <div class='tableauPlaceholder' id='viz1615792167055' style='position: relative'><noscript><a href='#'><img alt=' ' src='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;Ba&#47;BarVisitsData&#47;Dashboard1&#47;1_rss.png' style='border: none' /></a></noscript><object class='tableauViz'  style='display:none;'><param name='host_url' value='https%3A%2F%2Fpublic.tableau.com%2F' /> <param name='embed_code_version' value='3' /> <param name='path' value='views&#47;BarVisitsData&#47;Dashboard1?:language=en&amp;:embed=y&amp;:display_count=y&amp;publish=yes' /> <param name='toolbar' value='yes' /><param name='static_image' value='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;Ba&#47;BarVisitsData&#47;Dashboard1&#47;1.png' /> <param name='animate_transition' value='yes' /><param name='display_static_image' value='yes' /><param name='display_spinner' value='yes' /><param name='display_overlay' value='yes' /><param name='display_count' value='yes' /><param name='language' value='en' /><param name='filter' value='publish=yes' /></object></div>                <script type='text/javascript'>                    var divElement = document.getElementById('viz1615792167055');                    var vizElement = divElement.getElementsByTagName('object')[0];                    if ( divElement.offsetWidth > 800 ) { vizElement.style.width='1000px';vizElement.style.height='827px';} else if ( divElement.offsetWidth > 500 ) { vizElement.style.width='1000px';vizElement.style.height='827px';} else { vizElement.style.width='100%';vizElement.style.height='727px';}                     var scriptElement = document.createElement('script');                    scriptElement.src = 'https://public.tableau.com/javascripts/api/viz_v1.js';                    vizElement.parentNode.insertBefore(scriptElement, vizElement);                </script>
    """
    st.components.v1.html(html_tableau_bar_visits,width = 600, height= 600)
else: # my_button=='Show the distribution of Restaurant visits':
    plot_on_PA(fetch(4))

#--------------------------------------------------
#--Time versus Value charts (Line)
#--------------------------------------------------
st.title("Compare the individual metrics over time")
st.markdown("**1) Select a PA County from the dropdown (below charts)**")
st.markdown("**2) Highlight any of the first two graph (emotional charts) to compare with last two (behavior)**")
st.markdown("Note: Not all counties have data for each metric for every time period (Try large counties such as Alleghany, Philadelphia, York, etc.)")

#---Select County Dropdown--
county_dropdown = alt.binding_select(options=list(countyList))
selectedCounty = alt.selection_single(fields=['name'],bind=county_dropdown, name='PA County:')

#---brush select area to focus on
brush = alt.selection(type = 'interval',encodings=['x'])


#---commWorry chart
commWorryChart = alt.Chart(commWorrydf).mark_area(color='red').encode(
    alt.X("monthdate(time_value):T",axis=alt.Axis(title='Date')),
    alt.Y("value:Q",axis=alt.Axis(title='Percentage of people')),
    tooltip=[alt.Tooltip('geo_value',title = 'FIPS'),alt.Tooltip('monthdate(time_value)',title = 'date'), alt.Tooltip('value',title='Value')],

    ).transform_filter(
        selectedCounty
    ).properties(width=600,height=200,title="Percent of People who know someone with COVID-like symptoms")


#--selfWorry chart

selfWorryChart = alt.Chart(selfWorrydf).mark_area(color='purple').encode(
    alt.X("monthdate(time_value):T",axis=alt.Axis(title='Date')),
    alt.Y("value:Q",axis=alt.Axis(title='Percentage of people')),
    tooltip=[alt.Tooltip('geo_value',title = 'FIPS'),alt.Tooltip('monthdate(time_value)',title = 'date'), alt.Tooltip('value',title='Value')],

     ).transform_filter(
         selectedCounty
     ).properties(width=600,height=200,title="Percent of People who are afraid they or someone they know will become seriously ill from COVID-19 ")



#--barData chart
barDataChart = alt.Chart(barDatadf).mark_line(color = 'green').encode(
    alt.X("monthdate(time_value):T",axis=alt.Axis(title='Date'),scale=alt.Scale(domain=brush)),
    alt.Y("value:Q",axis=alt.Axis(title='Percentage of people')),
    tooltip=[alt.Tooltip('geo_value',title = 'FIPS'),alt.Tooltip('monthdate(time_value)',title = 'date'), alt.Tooltip('value',title='Value')],

    ).transform_filter(
        selectedCounty
    ).properties(width=600,height=200,title="Number of people visiting bars")


#--restaurant data chart
restaurantDataChart = alt.Chart(restaurantDatadf).mark_line( color = 'blue').encode(
    alt.X("monthdate(time_value):T",axis=alt.Axis(title='Date'),scale=alt.Scale(domain=brush)),
    alt.Y("value:Q",axis=alt.Axis(title='Percentage of people')),
    tooltip=[alt.Tooltip('geo_value',title = 'FIPS'),alt.Tooltip('monthdate(time_value)',title = 'date'), alt.Tooltip('value',title='Value')],

    ).transform_filter(
        selectedCounty
    ).properties(width=600,height=200,title="Number of people visiting restaurants")



#---version 4 combine #vertical concat all 4
vconcatChart=alt.vconcat(commWorryChart,selfWorryChart,barDataChart,restaurantDataChart).add_selection(
        selectedCounty,
        brush
        )
st.write(vconcatChart)

    
#---Show Raw Data data table
st.title("View Raw Data Tables")
st.markdown("**Select a checkbox**")

#CommunityWorry Data
if st.checkbox("Show me the raw data for those reporting illness in the community"):
    st.write(commWorrydf)
    
#SelfWorry Data
if st.checkbox("Show me the raw data worried about becoming ill"):
    st.write(selfWorrydf)
    
#BarData
if st.checkbox("Show me the raw data for bar visits"):
    st.write(barDatadf)    
#RestaurantData
if st.checkbox("Show me the raw data for restaurant visits"):
    st.write(restaurantDatadf)


# if st.checkbox("Show me the list of counties"):
#     st.write(countyList)
 


