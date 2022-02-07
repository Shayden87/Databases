#!/usr/bin/env python
# coding: utf-8

# In[1]:


###################################################################################
# Name                  : ProjectTwoDashboard.ipynb
# Author                : Spencer Hayden
# Original Date         : 08/23/2020
# Revision Date         : 02/01/2022
# Version               : 2.0
# Description           : Jupyter notebook file that allows data from MongoDB to be
# viewed graphically through browser-based user interface. This particular notebook
# file displays animal rescue data in a 10 row scrollable table. It allows user to  
# filter results through radio buttons and update results on table. Upon selection/
# selections of a particular entry by row/rows, a pie chart and map widget is 
# displayed at bottom of the UI. The pie chart diplays percentages broken down by 
# breed of selected filter and/or selections. The map widget displays a pin on a map 
# on the location the selected animals were rescued. The backend functionality is 
# implemented by an included Python file animal_shelter 2 that provides functions 
# for creating, reading, updating, and deleting data entries from MongoDB database.
###################################################################################

import dash
import dash_leaflet as dl
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import dash_table as dt
import base64
import json
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from collections import OrderedDict
from bson.json_util import dumps
from dash.dependencies import Input, Output, State
from dash import callback_context
from pymongo import MongoClient

# Imports AnimalShelter Class from animal_shelter2 Python module
from animal_shelter2 import AnimalShelter

###########################
# Data Manipulation / Model
###########################

# Username and password once validated, are fed to AnimalShelter class Python module
username = "aacuser2"
password = "password"

while True: 
    a = str(input("Enter username:"))
    if (len(a) >= 15) or a != username:
        print("Username invalid")
    elif a == username:
        break

while True:
    b = str(input("Enter password:"))
    if (len(b) != 8) or b != password:
        print("Password invalid")
    elif b == password:
        break

username = a
password = b
            
shelter = AnimalShelter(username, password)
    
# Class read method must support return of cursor object and accept projection json input
df = pd.DataFrame.from_records(shelter.read({}))

#########################
# Dashboard Layout / View
#########################
app = JupyterDash('SimpleExample')

# Adds in Grazioso Salvare’s logo
image_filename = 'Grazioso Salvare Logo.png' 
encoded_image = base64.b64encode(open(image_filename, 'rb').read())

app.layout = html.Div([
    html.Div(id='hidden-div', style={'display':'none'}),
    # Enodes Grazioso Salvare’s logo with URL href
    html.A([
        html.Img(
            src='data:image/png;base64,{}'.format(encoded_image.decode()),
            style={
                    'height' : '20%',
                    'width' : '20%',
                    'float' : 'left',
                    'position' : 'relative',
                    'padding-top' : 0,
                    'padding-right' : 0
            })
    ], href='https://www.snhu.edu/'),
    html.Br(),
    html.Hr(),
    html.Center(html.B(html.H1('Spencer Hayden: CS340 Dashboard'))),
    html.Hr(),
    # Creates container for radio button filters to filter and reset table results
    html.Div(
        dcc.RadioItems(
            id='filters',
            # Creats labels and values for radio button filters
            options=[
            {'label': 'Water Rescue', 'value': '0'},
            {'label': 'Mountain/Wilderness Rescue', 'value': '1'},
            {'label': 'Disaster Rescue/Individual Tracking', 'value': '2'},
            {'label': 'Reset - returns unfiltered state', 'value': '3'}
            ],
            value='RESET',
            labelStyle={'display': 'inline-block'}
        )
    ),
    # Creates table to display MongoDB data
    dash_table.DataTable(
        id='datatable-interactivity',
        columns=[
            {'id': i, 'name': i} for i in df.columns
        ],
        data=df.to_dict('records'),
        # Makes table horizontally scrollable
        style_table={'overflowX': 'auto'},
        # Sets cell size
        style_cell={'height': 'auto', 'minWidth': '180px', 'width': '180px',
                    'maxWidth': 'auto', 'whiteSpace': 'normal'},
        # Aligns text to left on these particular table columns
        style_cell_conditional=([
            {
                'if':{'column_id': i},
                'textAlign': 'left'
            } for i in ['animal_type', 'name', 'breed', 'color', 
                        'outcome_subtype', 'outcome_type', 
                        'sex_upon_outcome']
        ]),
        editable=False,
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
        column_selectable=False,
        row_selectable="multi",
        row_deletable=False,
        selected_columns=[],
        selected_rows=[],
        page_action="native",
        page_current= 0,
        page_size= 10,

    ),
    html.Br(),
    html.Hr(),
    # This sets up the dashboard so that chart and geolocation chart are side-by-side
    html.Div(className='row',
         style={'display' : 'flex'},
             children=[
        html.Div(
            id='graph-id',
            className='col s12 m6',

            ),
        html.Div(
            id='map-id',
            className='col s12 m6',
            )
        ])
    
])

#############################################
# Interaction Between Components / Controller
#############################################

# Filters interactive data table with MongoDB queries through radio buttons created earlier.
@app.callback(
    [Output('datatable-interactivity','data'),
    Output('button-one', 'columns')],
    [Input('filters', 'value')]
)
def update_dashboard(filters):
    # Filters by water rescue
    if filters == '0':
        df = pd.DataFrame(list(shelter.read({'$or': [{'breed':'Labrador Retriever'},
                                                    {'breed':'Chesapeake Bay Retriever'},
                                                    {'breed':'Newfoundland'}],
                                                    'age_upon_outcome_in_weeks': 
                                                    {'$gte':26,'$lte':156},
                                                    'sex_upon_outcome':'Intact Female'})))
    # Filters by Mountain/Wilderness Rescue                         
    elif filters == '1':
        df = pd.DataFrame(list(shelter.read({'$or': [{'breed':'German Shepherd'},
                                                    {'breed':'Malamute'},
                                                    {'breed':'Old English Sheepdog'},
                                                    {'breed':'Siberian Husky'},
                                                    {'breed':'Rottweiler'}],
                                                    'age_upon_outcome_in_weeks': 
                                                    {'$gte':26,'$lte':156},
                                                    'sex_upon_outcome':'Intact Male'})))
    # Filters by Disaster Rescue/Individual Tracking        
    elif filters == '2':
        df = pd.DataFrame(list(shelter.read({'$or': [{'breed':'Doberman Pinscher'},
                                                    {'breed':'German Shepherd'},
                                                    {'breed':'Golden Retriever'},
                                                    {'breed':'Bloodhound'},
                                                    {'breed':'Rottweiler'}],
                                                    'age_upon_outcome_in_weeks': 
                                                    {'$gte':20,'$lte':300},
                                                    'sex_upon_outcome':'Intact Male'})))
    # Resets filters/unfiltered                                          
    elif filters == '3':
        df = pd.DataFrame.from_records(shelter.read({}))
    else:
        df = pd.DataFrame.from_records(shelter.read({}))
    # Displays table  
    return df.to_dict('records')

# Creates highlight for selected column
@app.callback(
    Output('datatable-interactivity', 'style_data_conditional'),
    [Input('datatable-interactivity', 'selected_columns')]
)
def update_styles(selected_columns):
    return [{
        'if': { 'column_id': i },
        'background_color': '#D2F3FF'
    } for i in selected_columns]

# Updates Pie Chart based on row selection
@app.callback(
    Output('graph-id', "children"),
    [Input('datatable-interactivity', "derived_viewport_data")]
)
def update_graphs(viewData):
    dff = pd.DataFrame.from_dict(viewData)
    
    names = dff['breed'].value_counts().keys().tolist()
    values = dff['breed'].value_counts().tolist()
    
    return [
        dcc.Graph(id='pie-chart',            
            figure = px.pie(
                data_frame=dff, 
                values = values, 
                names = names,
                color_discrete_sequence = px.colors.sequential.RdBu,
                width = 700,
                height = 400, 
            )
        )
    ]
    
# Updates Geolocation Map based on row selection
@app.callback(
    Output('map-id', "children"),
    [Input('datatable-interactivity', "derived_viewport_data"),
    Input('datatable-interactivity', 'selected_rows'),
    Input('datatable-interactivity', 'selected_columns')]
)
    
def update_map(viewData, selected_rows, selected_columns):
    
    dff = pd.DataFrame.from_dict(viewData)
    
    if selected_rows == []:
        selected_rows = [0]
    # Displays map with 1 pin per selected row (1 pin)
    if len(selected_rows) == 1:    
        return [
                dl.Map(style={'width':'1000px', 'height': '500px'}, center=[30.75,-97.48], zoom=10, children=[
                    dl.TileLayer(id="base-layer-id"),
            
                    #marker with tool tip and popup
                    dl.Marker(position=[(dff.iloc[selected_rows[0],13]), (dff.iloc[selected_rows[0],14])], children=[
                        dl.Tooltip(dff.iloc[selected_rows[0],4]),
                        dl.Popup([
                            html.H4("Animal Name"),
                            html.P(dff.iloc[selected_rows[0],9]),
                            html.H4("Sex"),
                            html.P(dff.iloc[selected_rows[0],12]),
                            html.H4("Breed"),
                            html.P(dff.iloc[selected_rows[0],4]),
                            html.H4("Age"),
                            html.P(dff.iloc[selected_rows[0],15])
                        ])
                    ])
                ])
            ]
    # Displays map with 1 pin per selected rows (2 pins)
    if len(selected_rows) == 2:
        return [
            dl.Map(style={'width':'1000px', 'height': '500px'}, center=[30.75,-97.48], zoom=10, children=[
                dl.TileLayer(id="base-layer-id"),
            
                #marker with tool tip and popup
                dl.Marker(position=[(dff.iloc[selected_rows[0],13]), (dff.iloc[selected_rows[0],14])], children=[
                    dl.Tooltip(dff.iloc[selected_rows[0],4]),
                    dl.Popup([
                        html.H4("Animal Name"),
                        html.P(dff.iloc[selected_rows[0],9]),
                        html.H4("Sex"),
                        html.P(dff.iloc[selected_rows[0],12]),
                        html.H4("Breed"),
                        html.P(dff.iloc[selected_rows[0],4]),
                        html.H4("Age"),
                        html.P(dff.iloc[selected_rows[0],15])
                    ])
                ]),
                dl.Marker(position=[(dff.iloc[selected_rows[1],13]), (dff.iloc[selected_rows[1],14])], children=[
                    dl.Tooltip(dff.iloc[selected_rows[1],4]),
                    dl.Popup([
                        html.H4("Animal Name"),
                        html.P(dff.iloc[selected_rows[1],9]),
                        html.H4("Sex"),
                        html.P(dff.iloc[selected_rows[1],12]),
                        html.H4("Breed"),
                        html.P(dff.iloc[selected_rows[1],4]),
                        html.H4("Age"),
                        html.P(dff.iloc[selected_rows[1],15])
                    ])
                ])
            ])
        ]
    # Displays map with 1 pin per selected rows (3 pins)
    if len(selected_rows) == 3:
        return [
            dl.Map(style={'width':'1000px', 'height': '500px'}, center=[30.75,-97.48], zoom=10, children=[
                dl.TileLayer(id="base-layer-id"),
            
                #marker with tool tip and popup
                dl.Marker(position=[(dff.iloc[selected_rows[0],13]), (dff.iloc[selected_rows[0],14])], children=[
                    dl.Tooltip(dff.iloc[selected_rows[0],4]),
                    dl.Popup([
                        html.H4("Animal Name"),
                        html.P(dff.iloc[selected_rows[0],9]),
                        html.H4("Sex"),
                        html.P(dff.iloc[selected_rows[0],12]),
                        html.H4("Breed"),
                        html.P(dff.iloc[selected_rows[0],4]),
                        html.H4("Age"),
                        html.P(dff.iloc[selected_rows[0],15])
                    ])
                ]),
                dl.Marker(position=[(dff.iloc[selected_rows[1],13]), (dff.iloc[selected_rows[1],14])], children=[
                    dl.Tooltip(dff.iloc[selected_rows[1],4]),
                    dl.Popup([
                        html.H4("Animal Name"),
                        html.P(dff.iloc[selected_rows[1],9]),
                        html.H4("Sex"),
                        html.P(dff.iloc[selected_rows[1],12]),
                        html.H4("Breed"),
                        html.P(dff.iloc[selected_rows[1],4]),
                        html.H4("Age"),
                        html.P(dff.iloc[selected_rows[1],15])
                    ])
                ]),
                d1.Marker(position=[(dff.iloc[selected_rows[2],13]), (dff.iloc[selected_rows[2],14])], children=[
                    d1.Tooltip(dff.iloc[selected_rows[2],4]),
                    d1.Popup([
                        html.H4("Animal Name"),
                        html.P(dff.iloc[selected_rows[2],9]),
                        html.H4("Sex"),
                        html.P(dff.iloc[selected_rows[2],12]),
                        html.H4("Breed"),
                        html.P(dff.iloc[selected_rows[2],4]),
                        html.H4("Age"),
                        html.P(dff.iloc[selected_rows[2],15])
                    ])
                ])
            ])
        ]
        
        
    
app


# In[ ]:




