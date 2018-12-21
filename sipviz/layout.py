import os, json
import dash 
import geopandas as gpd 
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

from sipviz.data_preparation import ResultsData
from sipviz.globals import DEFAULT_COLOR_SCALE, MAPBOX_TOKEN

FOLDER = os.getcwd() # os.path.join(FOLDER, os.pardir())
FOLDER_DATA = os.path.join(FOLDER, "sample_data/")
sample_data = "sample_data/"
# Load the data and get the max of scenarios and max of iterations
dInstance = ResultsData(sample_data)
data = dInstance.process_solutions_to_dictionary() #process_solutions_to_dictionary()
max_iterations = max(data.keys())
max_scenarios = max(data[0].keys())
steps = int(max_iterations / (len(data.keys()) - 1))
max_periods = max(data[0][1]) # iteration, scenario

solution_final, volume_final = dInstance.get_final_result_data()


colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}


layout = html.Div(
    style={'backgroundColor': colors['background'], 'width':'99vw', 'height':'99vh'}, 
    children=[
            html.Div([
                html.Div([
                    html.H2(
                        children='Welcome to SIPVIZ',
                        style={
                            'textAlign': 'center',
                            'color': colors['text']
                        }
                    ), 
                    html.H3('A Web App for Visualizing Model 1 Results from Progressive Hedging Variables Fixing (PHVF).', 
                    style={
                        'textAlign': 'center',
                        'color': colors['text']
                    })
                ], className = 'col-lg-12 col-md-12')
                
            ], className = 'row'),
            html.Div([
                html.Div([
                    html.Div(
                        id = "main_map",
                        style = {"padding": '0px'}, 
                        children = [
                            dcc.Graph(
                                id = 'mapbox',
                            
                            )
                        ]
                    ),
                    html.Div(
                        style = {'margin-left':'10px', 'margin-right': '10px'},
                        children = [
                            dcc.RangeSlider(
                                marks={i: '{}'.format(i) for i in range(1, max_scenarios+1, 10)},
                                min=1,
                                max=max_scenarios,
                                value=[1, int(max_scenarios/2)]
                            ),
                            html.P('Select the range of scenarios results you want to download and press "Downlaod"', style={'margin-top':'40px', 'color':'#fff'}, 
                                    className = 'col-md-10'),
                            html.A(
                                html.Button('Download', id='dwld_solution', style={'margin-top':'30px', 'color':'#fff'}, className = 'btn btn-primary col-md-2' ),
                                id = 'download_solutions',
                                download = 'solutions.csv',
                                href = '',
                                target = '_blank'
                            )
                            ,
                        ]
                    )
                ], className = 'col-lg-6'),
                
                html.Div([
                    html.Div(
                        style={'margin-left':'0vw', 'margin-right':'1vw'}, 
                        children=[
                            html.Label('Iterations', style={'color':'#fff'}),
                            dcc.Slider(
                                id='slider_iterations',
                                min=0,
                                max=max_iterations,
                                step = steps,
                                marks={i: '{}'.format(i) for i in range(0, max_iterations+1, steps)},
                                value=0,
                            ),
                            html.Label('Scenarios', style={'margin-top':'20px', 'color':'#fff'}),
                            dcc.Slider(
                                id='slider_scenarios',
                                min=1,
                                max=max_scenarios,
                                step=1,
                                marks={i: '{}'.format(i) for i in range(1, max_scenarios+1, 10)},
                                value=5,
                            ),
                            html.Label('Periods', style={'margin-top':'20px', 'color':'#fff'}),
                            dcc.Slider(
                                id='slider_periods',
                                min=0,
                                max=max_periods,
                                step=1,
                                marks={i: '{}'.format(i) for i in range(0, max_periods+1)},
                                value=1,
                            )], className = 'col-lg-12 col-md-12'),
                        html.Div([
                            dcc.Checklist(
                                id = 'sce_peri_checkbox',
                                style={'margin-top':'20px', 'color':'#fff'},
                                options=[
                                    {'label': 'Full Scenario', 'value': 'full_scenario'},
                                    {'label': 'All Periods', 'value': 'all_periods'}
                                ],
                                values=[],
                                labelStyle={'display': 'inline-block', 'padding': '10px'},
                                inputStyle={'padding': '10px'}
                            ),
                        ], className= 'col-lg-6 col-md-6'),
                        html.P(id='selected-scenario', className= 'col-lg-6 col-md-6', style={'margin-top':'10px', 'position':'relative'}),
                        html.Div([
                            dcc.Graph(
                                id='volume-bars',
                                style = {'width':'45vw', 'height':'50vh'}
                            )
                        ], className = 'col-lg-12 col-md-12')
                        #])
            ], className = 'col-lg-6 col-md-6')
                
            ], className = 'row')
])