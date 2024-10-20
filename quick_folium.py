import pandas as pd
import geopandas as gpd
import folium 
from folium import plugins
from folium.plugins import HeatMap
from folium.features import GeoJsonTooltip, GeoJsonPopup

## Function 1 map_location
def map_location(gdf):
    """ Creates centroid for the study area from a geo data frame to use as Folium map location 
    
    Parameters:
    - a geodataframe: a geographic polygon layer.
    """
    
    combined_bbox = gdf.geometry.union_all().envelope
    centroid = combined_bbox.centroid
    return [centroid.y, centroid.x]

## Function 2 map_boundary
def map_boundary(geo_data, fg_name, map_obj, lw):
    """ Adds a map boundary outline layer to Folium map 
    
    Parameters:
    - geo_data: a geodataframe containing polygons
    - fg_name: a feature group name (str)
    - map_obj: a folium map object (str)
    - lw: a line width (int)
    """
    
    feature_group = folium.FeatureGroup(name=fg_name)
    map_obj.add_child(feature_group)
    choropleth = folium.Choropleth(
        geo_data=geo_data,
        fill_opacity=0,
        line_weight=lw,
        fill_color=None
    ).add_to(feature_group)

## Function 3 map_poly_label
def map_poly_label(map_obj, geo_data, fg_name='Feature Group',
                   lc='black', lw=1.5,
                   tooltip_fields=None, tooltip_aliases=None):
    """ Creates a filled polygon layer with popup labels 
    
    Parameters:
    - map_obj: a folium map obj (str)
    - geo_data: a geodataframe containing polygons
    - fg_name: a feature group name (str)
    - lc: line colour (str)
    - lw: linewidth (int)
    - tooltip_fields: geodataframe column header field names (str)
    - tooltip_aliases: tooltip fields aliases (str)
    """
    
    # 1. Create a feature group
    feature_group = folium.FeatureGroup(name=fg_name)
    map_obj.add_child(feature_group)
    
    # 2. Add layer with transparent fill and no lines
    clust = folium.Choropleth(
        geo_data=geo_data,
        fill_opacity=0,
        line_opacity=0,
        fill_color=None
    ).add_to(feature_group)
    
    # 3. Style function for the lines
    clust_style = lambda x: {
        'color': lc,
        'weight': lw
    }
    
    # 4. Add style to the choropleth
    clust.geojson.add_child(
        folium.features.GeoJson(
            data=clust.geojson.data,
            style_function=clust_style
        )
    )
    
    # 5. Add transparent layer with tooltips
    folium.GeoJson(
        geo_data,
        style_function=lambda x: {'color': 'transparent', 'fillColor': 'transparent'},
        tooltip=folium.GeoJsonTooltip(
            fields=tooltip_fields if tooltip_fields else [],
            aliases=tooltip_aliases if tooltip_aliases else [],
            localize=True
        )
    ).add_to(feature_group)

## Function 5 map_point_label
def map_point_label(map_obj, geo_data, name='Robbery Offences in Clusters', 
                      r=6, fc='blue', fo=1, ec='blue', lw=1, 
                      fields=['month', 'location', 'lad'], 
                      show=False):   
    """ Creates a point layer with popup labels 
    
    Parameters:
    - map_obj: a folium map obj (str)
    - geo_data: a geodataframe containing polygons
    - name: new layer name (str)
    - r: radius of the circle point (int)
    - fc: fill_color (str)
    - fo: fill_opacity (dec)
    - ec: edge_color (str)
    - lw: line_width (int)
    - fields: geodataframe column header field names (str)
    - show: show the layer when loaded (bool)
    """
    
    geojson_layer = folium.GeoJson(
        geo_data,
        name=name,
        marker=folium.Circle(radius=r, fill_color=fc, fill_opacity=fo, color=ec, weight=lw),
        tooltip=folium.GeoJsonTooltip(fields=fields),
        popup=folium.GeoJsonPopup(fields=fields),
        show=show
    )

    geojson_layer.add_to(map_obj)
    return geojson_layer

## Function 6 heatmap_from_points
def heatmap_from_points(map_obj, geo_data, fg_name='Heatmap', r=15, b=10):
    """ Creates a heatmap from a point layer 
    
    Parameters:
    - map_obj: a folium map obj (str)
    - geo_data: a geodataframe containing polygons
    - fg_name: a feature group name (str)
    - r: radius of heatmap from points (int)
    - b: blur of heat from points (int)
    """
    
    # 1. Create a feature group 
    fg = folium.FeatureGroup(name=fg_name, show=False)
    map_obj.add_child(fg)

    # 2. Extract coords from geo_data
    heat_data = [[point.y, point.x] for point in geo_data.geometry]

    # 3. Add heatmap to feature group
    HeatMap(
        heat_data,
        radius=r,
        blur=b,
        gradient={0.3: 'white', 0.6:'yellow', 0.8:'orange', 0.9:'red', 1:'magenta'},
        overlay=True
    ).add_to(fg)

    return fg 

## Function 7 map_boundary_tooltip
def map_boundary_tooltip(
    map_obj,
    geo_data,
    fg_name='Boundary_with_tooltip',
    show=False,
    tooltip_fields=None,
    popup_fields=None,
    fo=0,
    fc=None,
    lw=2,
    lc='black',
    name='Boundary'
):
    """Adds a boundary layer with tooltips and popups to a Folium map.
    
    Parameters:
    - map_obj: a folium map obj (str)
    - geo_data: a geodataframe containing polygons
    - fg_name: a feature group name (str)
    - show: show the layer when loaded (bool)
    - tooltip_fields: geodataframe column header field names (str)
    - popup_fields: geodataframe column header field names (str)
    - fo: fill_opacity (dec)
    - fc: fill_color (str)
    - lw: line_width (int)
    - lc: line_color (str)
    - name: new layer name (str)
    """
    
    # 1. Create a feature group
    fg = folium.FeatureGroup(name=fg_name, show=show)
    map_obj.add_child(fg)
    
    # 2. Add the choropleth layer
    choropleth = folium.Choropleth(
        geo_data=geo_data,
        fill_opacity=fo,
        fill_color=fc,
        line_weight=lw,
        line_color=lc,
        name=name
    ).add_to(fg)
    
    # 3. Add tooltip if fields are provided
    if tooltip_fields:
        tooltip = GeoJsonTooltip(fields=tooltip_fields)
        choropleth.geojson.add_child(tooltip)
    
    # 4. Add popup if fields are provided
    if popup_fields:
        popup = GeoJsonPopup(fields=popup_fields)
        choropleth.geojson.add_child(popup)
        
## Function 8 map_graduated_circles
def map_graduated_circles(
    map_obj,
    gdf_points,
    radius_scale=10000,
    color='#17cbef',
    show=False,
    fill=True,
    fill_color='#17cbef',
    opacity=0.6,
    stroke=True,
    weight=1.0,
    fg_name='Graduated_Circles'
):
    """ Adds graduated circles to a Folium map based on the number of points at each location 
    
    Parameters:
    - map_obj: a folium map obj (str)
    - gdf_points: a geodataframe containing points
    - radius_scale: value for scaling points based on sum (int)
    - color: color of points (str)
    - show: show the layer when loaded (bool)
    - fill: circles fill (bool)
    - fill_color: fill colour (str)
    - opacity: opacity of circle (int)
    - stroke: stroke (bool)
    - weight: circle marker line weight (int)
    - fg_name: a feature group name (str)
    """
    
    # 1. Extract latitude and longitude from geometries
    gdf_points = gdf_points.copy()
    gdf_points['latitude'] = gdf_points.geometry.y
    gdf_points['longitude'] = gdf_points.geometry.x
    
    # 2. Group by exact coordinates and count the number of points per location
    grouped = gdf_points.groupby(['latitude', 'longitude']).size().reset_index(name='count')
    
    # 3. Create a feature group for the circles
    fg = folium.FeatureGroup(name=fg_name, show=show)
    map_obj.add_child(fg)
    
    # 4. Add circles to the feature group
    for idx, row in grouped.iterrows():
        location = [row['latitude'], row['longitude']]
        count = row['count']
        radius = count * radius_scale  # scale the radius based on count
        
        folium.Circle(
            location=location,
            radius=radius,
            color=color,
            fill=fill,
            fill_color=fill_color,
            opacity=opacity,
            stroke=stroke,
            weight=weight
        ).add_to(fg)