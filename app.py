import os, json
import dash 
import geopandas as gpd
import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from sipviz.layout import layout, data,  solution_final, volume_final
from sipviz.globals import DEFAULT_COLOR_SCALE, MAPBOX_TOKEN
#from sipviz.layout import layout


# Temp hack
data_progress = data
colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

FILE = "./shp/pack_proj.shp"
gdf =  gpd.read_file(FILE)
def get_lon_lat(gdf):
    lon = []
    lat = []
    for _, row in gdf.iterrows():
        lon.append(row.geometry.centroid.x)
        lat.append(row.geometry.centroid.y)
    return lon, lat
# gdf = gdf.to_crs({'init':'epsg:4326'})
lon, lat = get_lon_lat(gdf)

with open('./shp/pack_proj.json') as geofile:
    geoson_layer = json.load(geofile)
layer_binned = [{
        'type': 'FeatureCollection',
        'crs': {'type': 'name',
        'properties': {'name': 'urn:ogc:def:crs:OGC:1.3:CRS84'}},
        'features': [geoson_layer['features'][i]]
            } for i in range(len(geoson_layer['features']))]
stand_info = pd.read_csv('./shp/stand_info.csv')

##############################################
annotations = [dict(
		showarrow = False,
		text = '<b>Periods</b>',
        #bgcolor = '#EFEFEE',
		x = 0.98,
		y = 0.915,
)]
for i in range(len(DEFAULT_COLOR_SCALE)):
    annotations.append(
        dict(
            arrowcolor = DEFAULT_COLOR_SCALE[i],
            text = ('{}'.format(i)),
            height = 21,
            x = 0.98,
            y = 0.85-(i/20),
            ax = -55,
            ay = 0,
            arrowwidth = 15,
            arrowhead = 0,
        )
    )


text_info =[]
for _, row in stand_info.iterrows():
     text_info.append(
            '<b>Unit Name :</b> {}<br>'\
            '<b>Species:</b> {}<br>'\
            '<b>Area (acc):</b> {:0.2f}<br>'\
            '<b>Age:</b> {}<br>'\
            '<b>Site index:</b> {}'.format(row.UNIT_NAME, row.SPECIES, row.ACRES, row.AGE_2007, row.SITE_INDEX))


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server




app.css.append_css({
    'external_url': 'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css'
})
app.title = 'SIPVIZ'

app.layout = layout

@app.callback(
    Output('selected-scenario', 'children'),
    [Input('slider_scenarios', 'value')] )
def show_selected_scenario(selected_scenario):
    return ' Seclected Scenario: {}'.format(selected_scenario)


@app.callback(
    Output('volume-bars', 'figure'),
    [Input('slider_scenarios', 'value')]
)
def plot_volmes_harvested(scenario):
    scen_volume = volume_final[scenario]
    return {
            'data': [
                dict(
                    x = [i for i in range(1, len(scen_volume)+1)],
                    y = scen_volume,
                    type =  'bar'
                )
            ],
            'layout': dict(
                title = 'Volume harvested per period for scenario {}'.format(scenario),
                autosize = False,
                plot_bgcolor = colors['background'],
                paper_bgcolor =  colors['background'],
                font = {
                    'color': colors['text']
                },
                margin=dict(
                        b=40,
                        t=50,
                        pad=4
                    ),
                xaxis=dict(
                    title='Periods',
                    titlefont=dict(
                        family='Courier New, monospace',
                        size=18,
                        #color='#7f7f7f'
                        )
                    ),
                yaxis=dict(
                    title='Volumes',
                    titlefont=dict(
                        family='Courier New, monospace',
                        size=18,
                        #color='#7f7f7f',
                        automargin=True
                        )
                    )
                )
        }


data_map_callback =  [
            dict(
            type = 'scattermapbox',
            lat=lat,
            lon=lon,
            text = text_info,
            hoverinfo = 'text',
            marker = dict(size=5, color='white', opacity=0),)
            ]

@app.callback(
    Output('mapbox', 'figure'),
    [
        Input('slider_iterations', 'value'),
        Input('slider_scenarios', 'value'),
        Input('slider_periods', 'value'),
        Input('sce_peri_checkbox', 'values')
    ],
    # [
    #     State('mapbox', 'figure')
    # ]
)
def update_map_colors(iterations, scenarios, periods, final_full):
    if 'full_scenario' in final_full:
        data_display = solution_final[scenarios]
        if 'all_periods' in final_full:
            palette = [DEFAULT_COLOR_SCALE[data_display[i]] for i in range(len(data_display))]
        else:
            palette = [DEFAULT_COLOR_SCALE[data_display[i]] if data_display[i] == periods else '#cccccc' for i in range(len(data_display))]
    elif 'all_periods' in final_full:
        data_display = data_progress[iterations][scenarios]
        palette = [DEFAULT_COLOR_SCALE[data_display[i]]  for i in range(len(data_display))]
    else:
        data_display = data_progress[iterations][scenarios]
        palette = [DEFAULT_COLOR_SCALE[data_display[i]] if data_display[i] == periods else '#cccccc' for i in range(len(data_display))]
    
    layout = dict(
            autosize=True,
            hovermode='closest',
            margin=dict(l=0, r=0, t=0, b=0),
            plot_bgcolor = colors['background'],
            paper_bgcolor = colors['background'],
            annotations = annotations,
            mapbox=dict(
                accesstoken=MAPBOX_TOKEN,
                bearing=0,
                center=dict(lat=46.838, lon=-122.29),
                    style='light',
                    pitch=0,
                    zoom=12,
                    layers=[]
            )
        )
    for i in range(len(geoson_layer['features'])):
        geolayer = dict(
            type='fill',
            sourcetype='geoson',
            source=layer_binned[i],
            color= palette[i],
            below = 'state-label-sm',
            opacity=0.8,
        )
        layout['mapbox']['layers'].append(geolayer)

    updated_figure = dict(data = data_map_callback, layout = layout)
    return updated_figure
    


if __name__ == '__main__':
    app.run_server(debug=True)
