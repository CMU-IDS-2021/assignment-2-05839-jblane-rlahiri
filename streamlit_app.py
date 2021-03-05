import streamlit as st
import pandas as pd
import altair as alt
from datetime import date



# Deliverables
#  An interactive data science or machine learning application using Streamlit.
#  The URL at the top of this readme needs to point to your application online. It should also list the names of the team members.
#  A write-up that describes the goals of your application, justifies design decisions, and gives an overview of your development process. Use the writeup.md file in this repository. You may add more sections to the document than the template has right now.


st.title("Let's analyze some Penguin Data 🐧📊.") #how did he get this emoji on here?!

@st.cache  # add caching so we load the data only once
def load_data():
    # Load the penguin data from https://github.com/allisonhorst/palmerpenguins.
    penguins_url = "https://raw.githubusercontent.com/allisonhorst/palmerpenguins/v0.1.0/inst/extdata/penguins.csv"
    return pd.read_csv(penguins_url)

df = load_data()

st.write("Let's look at raw data in the Pandas Data Frame.")

st.write(df)

st.write("Hmm 🤔, is there some correlation between body mass and flipper length? Let's make a scatterplot with [Altair](https://altair-viz.github.io/) to find.")

chart = alt.Chart(df).mark_point().encode(
    x=alt.X("body_mass_g", scale=alt.Scale(zero=False)),
    y=alt.Y("flipper_length_mm", scale=alt.Scale(zero=False)),
    color=alt.Y("species")
).properties(
    width=600, height=400
).interactive()

st.write(chart)


# code for a map

# import altair as alt
# from vega_datasets import data

# counties = alt.topo_feature(data.us_10m.url, 'counties')
# source = data.unemployment.url

# alt.Chart(counties).mark_geoshape().encode(
#     color='rate:Q'
# ).transform_lookup(
#     lookup='id',
#     from_=alt.LookupData(source, 'id', ['rate'])
# ).project(
#     type='albersUsa'
# ).properties(
#     width=500,
#     height=300
# )
