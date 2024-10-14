import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import cartopy.crs as ccrs
import cartopy.feature as cfeature

def point_overview(lat1: float, lon1: float, lat2: float, lon2: float):
    '''
    Plots points on world map.
    
    Returns
    -------
    matplotlib figure
    '''
    central_lat = (lat1 + lat2)/2 + 20
    central_lon = (lon1 + lon2)/2
    
    # define map projection
    map_proj = ccrs.Orthographic(central_latitude=central_lat, central_longitude=central_lon)
    
    # set higher resolution for lines (the default values are awful)
    map_proj._threshold /= 100.0
    
    ax = plt.axes(projection=map_proj)
    
    # plot entire globe
    ax.set_global()
    
    # add oceans & land
    ax.add_feature(cfeature.OCEAN)
    ax.add_feature(cfeature.LAND)
    
    # add labels
    plt.text(lon1 - 2, lat1 - 10, s='Point A', backgroundcolor='white',
             horizontalalignment='right', color='red', transform=ccrs.Geodetic())
    
    plt.text(lon2 + 2, lat2 - 10, s='Point B', backgroundcolor='white',
             horizontalalignment='left', color='red', transform=ccrs.Geodetic())
    
    # North Pole lines for spherical triangle
    line1 = mlines.Line2D(xdata=[lon1, 0], ydata=[lat1, 90], linestyle='--', transform=ccrs.Geodetic())
    ax.add_line(line1)
    
    line2 = mlines.Line2D(xdata=[lon2, 0], ydata=[lat2, 90], linestyle='--', transform=ccrs.Geodetic())
    ax.add_line(line2)
    
    # baseline of spherical triangle (between main points)
    baseline = mlines.Line2D(xdata=[lon1, lon2], ydata=[lat1, lat2], color='pink',
                             marker='o', transform=ccrs.Geodetic())
    ax.add_line(baseline)
    
    # ellipsoidal chord is a straight line
    chord = mlines.Line2D(xdata=[lon1, lon2], ydata=[lat1, lat2], color='red',
                          marker='o', transform=ccrs.PlateCarree())
    ax.add_line(chord)
    
    plt.show()
    
