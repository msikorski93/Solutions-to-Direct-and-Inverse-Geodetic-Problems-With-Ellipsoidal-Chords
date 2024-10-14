# Solutions-to-Direct-and-Inverse-Geodetic-Problems-With-Ellipsoidal-Chords


![ alt text ](https://img.shields.io/badge/license-MIT-green?style=&logo=)
![ alt text ](https://img.shields.io/badge/-Python-3776AB?logo=Python&logoColor=white)
![ alt text ](https://img.shields.io/badge/-Jupyter-F37626?logo=Jupyter&logoColor=white)

An approach of solving the most fundamental geodetic tasks with usage of ellipsoidal chords (slant distances) proposed by Molodensky.


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
