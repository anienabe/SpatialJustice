# loading libraries
# GeoPandas: for GeoJSONs and GeoDataFrames
import geopandas as gpd

# Pandas: für tables, DataFrames
import pandas as pd

# Matplotlib: Visualization and plots 
import matplotlib.pyplot as plt



# Loading data: GeoJSON with administrative boundaries
boundaries = gpd.read_file("data/Statist_UnterbezirkePolygon.geojson", encoding="latin-1") # UTF-8 was not working

# Loading data: GeoJSON with point data (here maybe loop for all point data soon)
assisted_living = gpd.read_file("data/betreutes-wohnen_do_2026.geojson", encoding="latin-1") 


# plot both datasets at the same time to check data situation
fig, ax = plt.subplots()
boundaries.plot(ax=ax, edgecolor='black',color='powderblue')
assisted_living.plot(ax=ax, color='red')

plt.show()


# finding matches of points and polygons (how many points are in each polygon?)
# copy of points
pts = assisted_living.copy()

# Spatial Join by coordinates (is point coordinate geometrically inside coordinates of polygon?)
joined = gpd.sjoin(pts, boundaries, how='left', predicate='within')

# count the points
point_count = joined.groupby('index_right').size().reset_index(name='amount_points')

# merge with boundaries
boundaries_result = boundaries.copy()
boundaries_result['amount_points'] = boundaries_result.index.map(
    point_count.set_index('index_right')['amount_points']
).fillna(0).astype(int)

# list, sorted by administrative boundaries number, ascending (so 001 is first)
print(boundaries_result[['bezeichnun', 'unbeznr','amount_points']].sort_values('unbeznr', ascending=True))

# export as csv (sorted, ascended)
result_table = boundaries_result[['bezeichnun', 'unbeznr', 'amount_points']].sort_values('unbeznr', ascending=True)
result_table.to_csv('preprocessing/output/assisted_living_.csv', index=False)

# Plot to verify the results visually
boundaries_result['coloring'] = boundaries_result['amount_points'] > 0
ax = boundaries_result.plot(edgecolor='black', facecolor='powderblue')
pts.plot(ax=ax, color='red', markersize=5)
boundaries_result[boundaries_result['coloring']].plot(ax=ax, facecolor='coral', edgecolor='black')
plt.show()