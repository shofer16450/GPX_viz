import gpxpy
import numpy as np
import matplotlib.pyplot as plt
import mplleaflet
import pandas as pd
import seawater as sw


# Import data
gpx = gpxpy.parse(open('/home/sh16450/Downloads/Getting_attacked_by_British_drivers.gpx'))

print("{} track(s)".format(len(gpx.tracks)))
track = gpx.tracks[0]
print("{} segment(s)".format(len(track.segments)))
segment = track.segments[0]
print("{} point(s)".format(len(segment.points)))

data = []
segment_length = segment.length_3d()
for point_idx, point in enumerate(segment.points):
    data.append([point.longitude, point.latitude,
                 point.elevation, point.time, segment.get_speed(point_idx)])

columns = ['Longitude', 'Latitude', 'Altitude', 'Time', 'Speed']
df = pd.DataFrame(data, columns=columns)
df.head()

# To get unsmoothed total height of climbs
df['Altitude'].diff()[df['Altitude'].diff() > 0.0].sum()

# SMOOTHING
df_new = pd.rolling_mean(df[['Longitude', 'Latitude', 'Altitude', 'Speed']], 5, min_periods=1, center=True)
df_new['Time'] = df['Time']
# smoothed total of climbs
df_new['Altitude'].diff()[df_new['Altitude'].diff() > 0.0].sum()

# get angles
_, angles = sw.dist(df_new['Latitude'], df_new['Longitude'])
angles = np.r_[0, np.deg2rad(angles)]
# Normalize the speed to use as the length of the arrows
r = df_new['Speed'] / df_new['Speed'].max()
kw = dict(window_len=31, window='hanning')
df_new['u'] = r * np.cos(angles)
df_new['v'] = r * np.sin(angles)

# Visualize the data
fig, ax = plt.subplots(figsize=(16,9))
df = df.dropna()
ax.plot(df_new['Longitude'], df_new['Latitude'],
        color='darkorange', linewidth=6, alpha=0.5)
sub = 10
# ax.quiver(df_new['Longitude'][::sub], df_new['Latitude'][::sub], df_new['u'][::sub],
          # df_new['v'][::sub], color='deepskyblue', alpha=0.8)
mplleaflet.show(fig=fig, tiles='esri_aerial')


# Find time around a specific location
def time_at_place(df_new, east=-3.408, west=-3.423, north=50.6164, south=50.612):

    times_at_place = df_new['Time'].loc[(df_new['Latitude'] <= north) & (df_new['Latitude'] >= south) &
                                        (df_new['Longitude'] <= east) & (df_new['Longitude'] >= west)]
    return times_at_place
