import math

class DirectProblem(object):
    '''
    General class to perform the direct geodetic problem with ellipsoidal chords.
    Direct (first or forward) task: computing position given azimuth and distance from a known location.
    Takes input geodetic coordinates (ϕ, λ, h). 
    
    Parameters
    ----------
    lat1: float
        Geodetic latitude in decimal degrees (°) at point A in range [-90, 90].
        
    lon1: float
        Geodetic longitude in decimal degrees (°) at point A in range [0, 360). If negative,
        converts to proper range. Examples: -75°E --> 285°, -195°W --> 165°
        
    height1: float
        Geodetic height in meters (m) at point A.
        
    chord: float
        Ellipsoidal chord in meters (m), distance from point A to point B.
        
    azimuth: float
        Forward (direct) azimuth in decimal degrees (°) from point A to point B.
    
    zenith: float
        Chords zenith distance in decimal degrees (°).
        
    a: float, optional
        Semi-major axis (equatorial radius) of GRS80 in meters (m). Defaults to 6378137.0.
        
    b: float, optional
        Semi-minor axis (polar radius) of GRS80 in meters (m). Defaults to 6356752.3141.
        
    dec_degs: bool, optional
        Whether to express angular fractions as decimal degrees or DMS.
        Defaults to True.
    '''
    def __init__(self, lat1: float, lon1: float, height1: float,
                 chord: float, azimuth: float, zenith: float,
                 a: float = 6378137.0, b: float = 6356752.3141, dec_degs: bool = True):
        
        self.lat1 = lat1
        self.lon1 = lon1
        self.height1 = height1
        self.chord = chord
        self.azimuth = azimuth
        self.zenith = zenith
        self.a = a
        self.b = b
        self.dec_degs = dec_degs
        
        # latitude check
        if not (-90 <= self.lat1 <= 90):
            raise ValueError('Latitude must be in range [-90, 90]')
            
        # longitude checks
        if self.lon1 > 360:
            raise ValueError('Longitude must be in range (-180, 180)')
        
        # normalize longitude to the range (-180, 180)
        if self.lon1 > 180:
            self.lon1 -= 360
            
        # convert degrees to radians
        self.lat1, self.lon1, self.azimuth, self.zenith \
        = map(math.radians, [self.lat1, self.lon1, self.azimuth, self.zenith])
        
        # first eccentricity squared
        self.e2 = (self.a**2 - self.b**2) / self.a**2
        
        # normal radius of curvature in prime vertical
        self.N1 = self.a / math.sqrt(1 - self.e2 * math.sin(self.lat1)**2)
        
        # chord's direction cosines
        self.l = math.cos(self.lat1) * math.cos(self.lon1) * math.cos(self.zenith) \
        - math.sin(self.lat1) * math.cos(self.lon1) * math.sin(self.zenith) * math.cos(self.azimuth) \
        - math.sin(self.lon1) * math.sin(self.zenith) * math.sin(self.azimuth)
        
        self.m = math.cos(self.lat1) * math.sin(self.lon1) * math.cos(self.zenith) \
        - math.sin(self.lat1) * math.sin(self.lon1) * math.sin(self.zenith) * math.cos(self.azimuth) \
        + math.cos(self.lon1) * math.sin(self.zenith) * math.sin(self.azimuth)
        
        self.n = math.sin(self.lat1) * math.cos(self.zenith) \
        + math.cos(self.lat1) * math.sin(self.zenith) * math.cos(self.azimuth)
        
    def latitude(self):
        '''
        Computes geodetic latitude in decimal degrees (°) and radius of curvature in prime
        vertical in meters (m) at point B.
        
        Returns
        -------
        Value of reduced ellipsoid chord in meters (m).
        '''
        # initial approximate: latitude
        numerator = (self.N1 + self.height1) * math.sin(self.lat1) + self.chord * self.n

        denominator = math.sqrt(
            ((self.N1 + self.height1) * math.cos(self.lat1) * math.cos(self.lon1) + self.chord * self.l)**2 \
            + ((self.N1 + self.height1) * math.cos(self.lat1) * math.sin(self.lon1) + self.chord * self.m)**2
        )
        lat2 = math.atan(numerator / denominator)
        
        # initial approximate: radius of curvature in prime vertical
        N2 = self.a / math.sqrt(1 - self.e2 * math.sin(lat2)**2)
        
        # repeat calculations 15 times
        for _ in range(0, 15):
            numerator = (self.N1 + self.height1) * math.sin(self.lat1) + self.chord * self.n \
            + self.e2 * (N2 * math.sin(lat2) - self.N1 * math.sin(self.lat1))
            
            denominator = math.sqrt(
                ((self.N1 + self.height1) * math.cos(self.lat1) * math.cos(self.lon1) + self.chord * self.l)**2 \
                + ((self.N1 + self.height1) * math.cos(self.lat1) * math.sin(self.lon1) + self.chord * self.m)**2
            )
            lat2 = math.atan(numerator / denominator)
            
            N2 = self.a / math.sqrt(1 - self.e2 * math.sin(lat2)**2)
            
        return math.degrees(lat2), N2
    
    def longitude(self):
        '''
        Computes geodetic longitude in decimal degrees (°) at point B.
        
        Returns
        -------
        Value of longitude in decimal degrees (°).
        '''
        X = (self.N1 + self.height1) * math.cos(self.lat1) * math.sin(self.lon1) + self.chord * self.m
        Y = (self.N1 + self.height1) * math.cos(self.lat1) * math.cos(self.lon1) + self.chord * self.l
        
        lon2 = math.degrees(math.atan2(X, Y))
        
        # normalize longitude to (-180, 180)
        if lon2 > 180:
            lon2 -= 360
        elif lon2 < -180:
            lon2 += 360
        
        return lon2
    
    def height(self):
        '''
        Computes geodetic height in meters (m) at point B.
        
        Returns
        -------
        Value of height in meters (m).
        '''
        # convert degrees to radians 
        lat2, lon2 = map(math.radians, [self.latitude()[0], self.longitude()])
        
        # normal radius of curvature at point B
        N2 = self.latitude()[1]
        
        # sum of radius of curvature in prime vertical and height at point B
        N2_H2 = ((self.N1 + self.height1) * math.cos(self.lat1) * math.sin(self.lon1) + self.chord * self.m) \
            / ((math.cos(lat2)) * math.sin(lon2))
        
        return N2_H2 - N2
    
    def reduced_distance(self):
        '''
        Computes reduced ellipsoid chord (heights are not taken into account).
        
        Returns
        -------
        Value of reduced ellipsoid chord in meters (m).
        '''
        # convert degrees to radians 
        lat2 = math.radians(self.latitude()[0])
        
        # radius of curvature in prime vertical at point B
        N2 = self.latitude()[1]
        
        # height at point B
        height2 = self.height()
        
        k = (self.height1 / self.N1) + (height2 / N2) + ((self.height1 * height2) / (self.N1 * N2))
        
        mi = (self.a**4 - self.b**4) / self.a**4
        
        tau = 2 * (N2 - self.N1) * (height2 - self.height1) \
        + k * mi * (N2 * math.sin(lat2) - self.N1 * math.sin(self.lat1))**2 \
        - 2 * self.e2 * (N2 * math.sin(lat2) - self.N1 * math.sin(self.lat1)) \
        * (height2 * math.sin(lat2) - self.height1 * math.sin(self.lat1))
        
        p = (1 / (1 + k)) * (k + ((height2 - self.height1)**2 / self.chord**2) + (tau / self.chord**2))
        
        return self.chord - self.chord * (p / (1 + math.sqrt(1 - p)))
    
    def reverse_zenith_distance(self):
        '''
        Computes angular distance from the zenith above point B to point A: △ZBA.
        
        Returns
        -------
        Value of reverse zenith distance in decimal degrees (°).
        '''
        # convert degrees to radians 
        lat2, lon2 = map(math.radians, [self.latitude()[0], self.longitude()])
        
        # radius of curvature in prime vertical at point B
        N2 = self.latitude()[1]
        
        # height at point B
        height2 = self.height()
        
        # cosine of the central angle between two points
        cos_fi = math.sin(self.lat1) * math.sin(lat2) \
        + math.cos(self.lat1) * math.cos(lat2) * math.cos(lon2 - self.lon1)
        
        # reverse zenith distance
        cos_zen2 = math.acos(
            ((self.N1 + self.height1) * cos_fi - (N2 + height2) \
             + self.e2 * (N2 * math.sin(lat2) \
             - self.N1 * math.sin(self.lat1)) * math.sin(lat2)) / self.chord
        )
        
        return math.degrees(cos_zen2)
    
    def convert_to_xyz(self):
        '''
        Converts geodetic coordinates (ϕ, λ, h) to Cartesian coordinates (X, Y, Z).
        
        Returns
        -------
        Cartesian coordinates in meters (m).
        '''
        # convert degrees to radians 
        lat2, lon2 = map(math.radians, [self.latitude()[0], self.longitude()])
        
        # radius of curvature in prime vertical at point B
        N2 = self.latitude()[1]
        
        # height at point B
        height2 = self.height()
        
        # get Cartesian coordinates
        X2 = (N2 + height2) * math.cos(lat2) * math.cos(lon2)
        Y2 = (N2 + height2) * math.cos(lat2) * math.sin(lon2)
        Z2 = (N2 * (1 - self.e2) + height2) * math.sin(lat2)
        
        return {'X': X2, 'Y': Y2, 'Z': Z2}
    
    def decimal_to_dms(self, decimal_degrees):
        '''
        Converts decimal degrees into DMS. Example: 30.5° --> 30°30'00".
        
        Returns
        -------
        Angular values expressed in DMS notation.
        '''
        # get degrees (integer part)
        degrees = int(decimal_degrees)
        
        # get the fractional part of the degrees and convert it to minutes
        minutes_float = (abs(decimal_degrees) - abs(degrees)) * 60
        minutes = int(minutes_float)
        
        # get the fractional part of the minutes and convert it to seconds
        seconds = (minutes_float - minutes) * 60
    
        return f'{degrees}°{minutes}\'{seconds:.8f}"'
        
    def display_measures(self):
        '''
        Displays all computed quantities.
        
        Returns
        -------
        quantities: dict
        '''
        if self.dec_degs:
            return {
                'Normal radius of curvature': f'{self.latitude()[1]} m',
                'Latitude': f'{self.latitude()[0]}°',
                'Longitude': f'{self.longitude()}°',
                'Height': f'{self.height()} m',
                'Reduced chord': f'{self.reduced_distance()} m',
                'Reverse zenith distance': f'{self.reverse_zenith_distance()}°',
                'XYZ 2': f'{self.convert_to_xyz()} m',
            }
        else:
            return {
                'Normal radius of curvature': f'{self.latitude()[1]} m',
                'Latitude': self.decimal_to_dms(self.latitude()[0]),
                'Longitude': self.decimal_to_dms(self.longitude()),
                'Height': f'{self.height()} m',
                'Reduced chord': f'{self.reduced_distance()} m',
                'Reverse zenith distance': self.decimal_to_dms(self.reverse_zenith_distance()),
                'XYZ 2': f'{self.convert_to_xyz()} m',
            }
        

class InverseProblem(object):
    '''
    General class to perform the inverse geodetic problem with ellipsoidal chords.
    Inverse (second or reverse) task: computing azimuth and distance between known positions.
    Takes input geodetic coordinates (ϕ, λ, h). 
    
    Parameters
    ----------
    lat1: float
        Geodetic latitude in decimal degrees (°) at point A in range [-90, 90].
        Positive for north hemisphere and negative for south hemisphere.
        
    lon1: float
        Geodetic longitude in decimal degrees (°) at point A in range (-180, 180).
        Negative for west hemisphere and positive for east hemisphere.
        
    height1: float
        Geodetic height in meters (m) at point A.
        
    lat2: float
        Geodetic latitude in decimal degrees (°) at point B in range [-90, 90].
        Positive for north hemisphere and negative for south hemisphere.
        
    lon2: float
        Geodetic longitude in decimal degrees (°) at point A in range (-180, 180).
        Negative for west hemisphere and positive for east hemisphere.
        
    height2: float
        Geodetic height in meters (m) at point B.
        
    a: float, optional
        Semi-major axis (equatorial radius) of GRS80 in meters (m). Defaults to 6378137.0.
        
    b: float, optional
        Semi-minor axis (polar radius) of GRS80 in meters (m). Defaults to 6356752.3141.
        
    dec_degs: bool, optional
        Whether to express angular fractions as decimal degrees or DMS.
        Defaults to True.
    '''
    def __init__(self, lat1: float, lon1: float, height1: float,
                 lat2: float, lon2: float, height2: float,
                 a: float = 6378137., b: float = 6356752.3141, dec_degs: bool = True):
        
        self.lat1 = lat1
        self.lon1 = lon1
        self.height1 = height1
        self.lat2 = lat2
        self.lon2 = lon2
        self.height2 = height2
        self.a = a
        self.b = b
        self.dec_degs = dec_degs
        
        # latitude checks
        if not (-90 <= self.lat1 <= 90):
            raise ValueError('Latitude must be in range [-90, 90]')
        if not (-90 <= self.lat2 <= 90):
            raise ValueError('Latitude must be in range [-90, 90]')
            
        # longitude checks
        if self.lon1 > 360 or self.lon2 > 360:
            raise ValueError('Longitude must be in range [0, 360)')
        
        # normalize longitudes to the range (-180, 180)
        if self.lon1 > 180:
            self.lon1 -= 360
        if self.lon2 > 180:
            self.lon2 -= 360
            
        # convert degrees to radians
        self.lat1, self.lon1, self.lat2, self.lon2 \
        = map(math.radians, [self.lat1, self.lon1, self.lat2, self.lon2])
        
        # first eccentricity squared
        self.e2 = (self.a**2 - self.b**2) / self.a**2
        
        # normal radius of curvature in prime vertical
        self.N1 = self.a / math.sqrt(1 - self.e2 * math.sin(self.lat1)**2)
        self.N2 = self.a / math.sqrt(1 - self.e2 * math.sin(self.lat2)**2)
        
    def convert_to_xyz(self):
        '''
        Converts geodetic coordinates (ϕ, λ, h) to Cartesian coordinates (X, Y, Z).
        
        Returns
        -------
        Cartesian coordinates in meters (m).
        '''
        X1 = (self.N1 + self.height1) * math.cos(self.lat1) * math.cos(self.lon1)
        Y1 = (self.N1 + self.height1) * math.cos(self.lat1) * math.sin(self.lon1)
        Z1 = (self.N1 * (1 - self.e2) + self.height1) * math.sin(self.lat1)
        
        X2 = (self.N2 + self.height2) * math.cos(self.lat2) * math.cos(self.lon2)
        Y2 = (self.N2 + self.height2) * math.cos(self.lat2) * math.sin(self.lon2)
        Z2 = (self.N2 * (1 - self.e2) + self.height2) * math.sin(self.lat2)
        
        return {'X': X1, 'Y': Y1, 'Z': Z1}, {'X': X2, 'Y': Y2, 'Z': Z2}
    
    def chord_distance(self):
        '''
        Computes ellipsoid chord (slant distance from A to B, not arc).
        
        Returns
        -------
        Value of ellipsoid chord in meters (m).
        '''
        mi = (self.a**4 - self.b**4) / self.a**4
        
        # cosine of the central angle between two points
        cos_fi = math.sin(self.lat1) * math.sin(self.lat2) \
        + math.cos(self.lat1) * math.cos(self.lat2) * math.cos(self.lon2 - self.lon1)
 
        # chord length
        chord = (self.N2 + self.height2)**2 + (self.N1 + self.height1)**2 \
            - 2 * (self.N2 + self.height2) * (self.N1 + self.height1) * cos_fi \
            - mi * (self.N2 * math.sin(self.lat2) - self.N1 * math.sin(self.lat1))**2 \
            - 2 * self.e2 * (self.N2 * math.sin(self.lat2) - self.N1 * math.sin(self.lat1))\
            * (self.height2 * math.sin(self.lat2) - self.height1 * math.sin(self.lat1))
        
        return math.sqrt(chord)
    
    def cartesian_distance(self):
        '''
        Computes ellipsoid chord using Cartesian coordinates. Should return the same
        value as chord_distance() method.
        
        Returns
        -------
        Value of distance (ellipsoid chord) in meters (m).
        
        '''
        # get Cartesian coordinates
        X1 = (self.N1 + self.height1) * math.cos(self.lat1) * math.cos(self.lon1)
        Y1 = (self.N1 + self.height1) * math.cos(self.lat1) * math.sin(self.lon1)
        Z1 = (self.N1 * (1 - self.e2) + self.height1) * math.sin(self.lat1)
        
        X2 = (self.N2 + self.height2) * math.cos(self.lat2) * math.cos(self.lon2)
        Y2 = (self.N2 + self.height2) * math.cos(self.lat2) * math.sin(self.lon2)
        Z2 = (self.N2 * (1 - self.e2) + self.height2) * math.sin(self.lat2)
        
        # Euclidean distance
        chord = (X2 - X1)**2 + (Y2 - Y1)**2 + (Z2 - Z1)**2
        
        return math.sqrt(chord)
    
    def reduced_distance(self):
        '''
        Computes reduced ellipsoid chord (heights are not taken into account).
        
        Returns
        -------
        Value of reduced ellipsoid chord in meters (m).
        '''
        mi = (self.a**4 - self.b**4) / self.a**4
        
        # sine of the central angle between two points
        sin_2fi = math.sin((self.lat2 - self.lat1)/2)**2 \
        + math.cos(self.lat1) * math.cos(self.lat2) * math.sin((self.lon2 - self.lon1)/2)**2
        
        # chord length (without heights)
        reduced_chord = 4 * self.N1 * self.N2 * sin_2fi + (self.N2 - self.N1)**2 \
        - mi * (self.N2 * math.sin(self.lat2) - self.N1 * math.sin(self.lat1))**2
        
        return math.sqrt(reduced_chord)
    
    def forward_azimuth(self):
        '''
        Computes foward (direct) azimuth from point A to point B.
        
        Returns
        -------
        Value of foward azimuth in decimal degrees (°).
        '''
        # calculate 1st term
        ctga1 = (math.sin(self.lat2) * math.cos(self.lat1) - 
                  math.cos(self.lat2) * math.sin(self.lat1) * 
                  math.cos(self.lon2 - self.lon1)) / (math.cos(self.lat2) * 
                  math.sin(self.lon2 - self.lon1))
    
        # calculate 2nd term
        ctgA1 = ctga1 - self.e2 * ((self.N2 * math.sin(self.lat2) \
                    - self.N1 * math.sin(self.lat1)) * 
                    math.cos(self.lat1)) / ((self.N2 + self.height2) * 
                    math.cos(self.lat2) * math.sin(self.lon2 - self.lon1))
    
        # calculate azimuth using atan2 to avoid quadrant issues
        azimuth = math.degrees(math.atan2(1, ctgA1))
    
        # normalize the azimuth to [0, 360)
        if azimuth > 180:
            azimuth -= 360
        
        return azimuth

    def reverse_azimuth(self):
        '''
        Computes reverse (backward) azimuth from point A to point B.
        
        Returns
        -------
        Value of reverse azimuth in decimal degrees (°).
        '''
        # calculate 1st term
        ctga2 = -(math.sin(self.lat1) * math.cos(self.lat2) - 
                   math.cos(self.lat1) * math.sin(self.lat2) * 
                   math.cos(self.lon2 - self.lon1)) / (math.cos(self.lat1) * 
                   math.sin(self.lon2 - self.lon1))
    
        # calculate 2nd term
        ctgA2 = ctga2 - self.e2 * ((self.N2 * math.sin(self.lat2) \
                    - self.N1 * math.sin(self.lat1)) * 
                    math.cos(self.lat2)) / ((self.N1 + self.height1) * 
                    math.cos(self.lat1) * math.sin(self.lon2 - self.lon1))
    
        # calculate azimuth using atan2 to avoid quadrant issues
        azimuth = math.degrees(math.atan2(1, ctgA2))
    
        # normalize the azimuth to [0, 360)
        if azimuth > 180:
            azimuth -= 360
    
        # reverse azimuth is typically the forward azimuth ± 180°
        azimuth = (azimuth + 180) % 360
        
        return azimuth
    
    def forward_zenith_distance(self):
        '''
        Computes angular distance from the zenith above point A to point B: △ZAB.
        
        Returns
        -------
        Value of forward zenith distance in decimal degrees (°).
        '''
        # cosine of the central angle between two points
        cos_fi = math.sin(self.lat1) * math.sin(self.lat2) \
        + math.cos(self.lat1) * math.cos(self.lat2) * math.cos(self.lon2 - self.lon1)
       
        # forward zenith distance
        cos_zen1 = math.acos(
            ((self.N2 + self.height2) * cos_fi - (self.N1 + self.height1) \
             - self.e2 * (self.N2 * math.sin(self.lat2) \
             - self.N1 * math.sin(self.lat1)) * math.sin(self.lat1)) / self.chord_distance()
        )
        
        return math.degrees(cos_zen1)

    def reverse_zenith_distance(self):
        '''
        Computes angular distance from the zenith above point B to point A: △ZBA.
        
        Returns
        -------
        Value of reverse zenith distance in decimal degrees (°).
        '''
        # cosine of the central angle between two points
        cos_fi = math.sin(self.lat1) * math.sin(self.lat2) \
        + math.cos(self.lat1) * math.cos(self.lat2) * math.cos(self.lon2 - self.lon1)
        
        # reverse zenith distance
        cos_zen2 = math.acos(
            ((self.N1 + self.height1) * cos_fi - (self.N2 + self.height2) \
             + self.e2 * (self.N2 * math.sin(self.lat2) \
             - self.N1 * math.sin(self.lat1)) * math.sin(self.lat2)) / self.chord_distance()
        )
        
        return math.degrees(cos_zen2)
    
    def decimal_to_dms(self, decimal_degrees):
        '''
        Converts decimal degrees into DMS. Example: 30.5° --> 30°30'00".
        
        Returns
        -------
        Angular values expressed in DMS notation.
        '''
        # get degrees (integer part)
        degrees = int(decimal_degrees)
        
        # get the fractional part of the degrees and convert it to minutes
        minutes_float = (abs(decimal_degrees) - abs(degrees)) * 60
        minutes = int(minutes_float)
        
        # get the fractional part of the minutes and convert it to seconds
        seconds = (minutes_float - minutes) * 60
    
        return f'{degrees}°{minutes}\'{seconds:.8f}"'

    def display_measures(self):
        '''
        Displays all computed quantities.
        
        Returns
        -------
        quantities: dict
        '''
        if self.dec_degs:
            return {
                'XYZ 1': f'{self.convert_to_xyz()[0]} m',
                'XYZ 2': f'{self.convert_to_xyz()[1]} m',
                'Chord (distance)': f'{self.chord_distance()} m',
                'Cartesian distance': f'{self.cartesian_distance()} m',
                'Reduced chord': f'{self.reduced_distance()} m',
                'Forward azimuth': f'{self.forward_azimuth()}°',
                'Reverse azimuth': f'{self.reverse_azimuth()}°',
                'Forward zenith distance': f'{self.forward_zenith_distance()}°',
                'Reverse zenith distance': f'{self.reverse_zenith_distance()}°',
            }
        else:
            return {
                'XYZ 1': f'{self.convert_to_xyz()[0]} m',
                'XYZ 2': f'{self.convert_to_xyz()[1]} m',
                'Chord (distance)': f'{self.chord_distance()} m',
                'Cartesian distance': f'{self.cartesian_distance()} m',
                'Reduced chord': f'{self.reduced_distance()} m',
                'Forward azimuth': self.decimal_to_dms(self.forward_azimuth()),
                'Reverse azimuth': self.decimal_to_dms(self.reverse_azimuth()),
                'Forward zenith distance': self.decimal_to_dms(self.forward_zenith_distance()),
                'Reverse zenith distance': self.decimal_to_dms(self.reverse_zenith_distance()),
            }
