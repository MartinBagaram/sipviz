import dash 
import dash_core_components as dcc
import dash_html_components as html
import geopandas as gpd
import json

FILE = "./shp/good_fake.shp"
gdf =  gpd.read_file(FILE)

def get_lon_lat(gdf):
    lon = []
    lat = []
    for _, row in gdf.iterrows():
        lon.append(row.geometry.centroid.x)
        lat.append(row.geometry.centroid.y)
    return lon, lat
gdf = gdf.to_crs({'init':'epsg:4326'})
lon, lat = get_lon_lat(gdf)

with open('./shp/good_fake.json') as geofile:
    geoson_layer = json.load(geofile)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


def get_trace():
    all_trace = []
    for index, row in gdf.iterrows():
        x,y = row.geometry.exterior.coords.xy
        trace = dict(
            type='scatter',
            showlegend=False,
            legendgroup='shapes',
            x=x,
            y=y,
            fill='toself',
            fillcolor='#c7c3c6',
            line=dict(color='black', width=0.90),
            marker=dict(size=0.00001),
            text=row.id
          
        )
        all_trace.append(trace)
    return all_trace
all_trace = get_trace()

app.css.append_css({
    'external_url': 'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css'
})
app.title = 'SIPVIZ'

app.layout =  dcc.Graph(
    id = 'mapbox',
    figure = dict(
        data =  [
        dict(
        type = 'scattermapbox',
        lat=lat,
        lon=lon,
        text = [str(i) for i in range(1, 301)],
        hoverinfo = 'text',
        marker = dict(size=5, color='white', opacity=0),)],
        layout = dict(
            autosize=True,
            hovermode='closest',
            margin=dict(l=0, r=0, t=0, b=0)
            ,
            mapbox=dict(
                accesstoken='pk.eyJ1Ijoic2lyc2FtYXJpIiwiYSI6ImNqcGcxamlzaDBoNDMzcW83MG8xeTltdHYifQ.BvZfMdd8oDh7GzaPejajhg',
                bearing=0,
                center=dict(lat=0.00096507, lon=-115.48729153102),
                style='light',
                pitch=0,
                zoom=18,
                layers=[
                    dict(
                        type='fill',
                        sourcetype='geoson',
                        source=geoson_layer,
                        color='gray',
                        below = 'state-label-sm',
                        opacity=0.8,
                    )
                ]
            )
        )
    ),
    style = {"height": '100vh'}
)
if __name__ == '__main__':
    app.run_server(debug=True)