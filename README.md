# Solutions-to-Direct-and-Inverse-Geodetic-Problems-With-Ellipsoidal-Chords

![ alt text ](https://img.shields.io/badge/license-MIT-green?style=&logo=)
![ alt text ](https://img.shields.io/badge/-Python-3776AB?logo=Python&logoColor=white)
![ alt text ](https://img.shields.io/badge/-Jupyter-F37626?logo=Jupyter&logoColor=white)

Scientific and research papers list countless approaches of solving the two fundamental geodetic problems, mostly named after the person who introduced it. Some top widely known and classic methods include: Clarke, Bessel-Helmert, Gauss, Vincenty, Sjöberg, Bowring, Kivioja, Puissant, etc. are just a few. Almost all of them have some limitations and are not comepletly versatile. New solutions are still developed to this day. This proves how significant and basic this task is for applications such as: geodesy, navigation, astro-geodesy, and astronomy.

A less known but highly reliable method to overcome this problem with slant distances (chord method) was proposed by M.S. Molodensky. This algorithm has following advantages:
* calculates geodetic coordinates not only for $\phi$ and $\lambda$, but also $h$ in which other approaches struggle;
* no distance limits between points - other methods are unreliable beyond a certain distance;
* very accurate, fast, and robust;
* no differential, integral, or numerical equations;
* easy to understand and entails solving an ellipsoidal triangle.

This class created in Python has no additional requirements and is ready to run (except the plotting function which requires to pre-install Cartopy). The included notebook shows few cases of the class usage on GRS80 ellipsoid - any rotational ellipsoid can be defined by implementing its semi axes $a$ and $b$.

**Code examples:**
```
from geodetic_problems import InverseProblem

# decimal latitudes in range [-90, 90]
# decimal longitudes in range (-180, 180)
# point 1: Paris, France
# point 2: Shillong, India

InverseProblem(lat1=48.836, lon1=2.335, height1=124.553,
                lat2=25.674, lon2=91.913, height2=1007.2).display_measures()
```

```
from geodetic_problems import DirectProblem

# azimuth & zenith distance in decimal degrees
# chord length in meters
# direct task from Paris to Shillong

DirectProblem(lat1=48.836, lon1=2.335, height1=124.553,
              azimuth=72.64905288510523,
              zenith=125.3179963885463,
              chord=7386512.867946799).display_measures()
```

<p align='center'>
<img src='https://github.com/user-attachments/assets/65b0015b-0244-4ac2-ae99-b7763f090f42' height='380'/>
</p>
