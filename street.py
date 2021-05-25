import requests
import streamlit as st
from PIL import Image
from numpy import arctan2, sin, cos, degrees

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
class street_views():
    '''
    Google Street View Parameters

    ---- required parameters ----
    location: (or pano(id)), address/ latlog
    size: {width}x{height}
    key: (or client), Google Clound API

    ---- optional parameters ----
    signature: (hash)
    heading: 0 - 360,  (both values indicating North, with 90 indicating East, and 180 South).
    fov: (default is 90) determines the horizontal field of view of the image. Max 120, smaller -> higher zoom.
    radius: default 50,  sets a radius, specified in meters, in which to search for a panorama.
    source: default / outdoor.  Default value is default.
    '''

    def __init__(self,
                 key,
                 size='640x640',
                 fov=90,
                 heading=90,
                 pitch=0,
                 signature=None,
                 radius=50,
                 source='default'):

        default_location = "Cornell Tech"

        self.params = {
            'location': default_location,
            'size': size,
            'key': key,
            'heading': heading,
            'fov': fov,
            'pitch': pitch,
            'radius': radius,
            'source': source,
        }

        self.pano_API_url = 'https://maps.googleapis.com/maps/api/streetview?'
        self.metadata_API_url = 'https://maps.googleapis.com/maps/api/streetview/metadata?'

    def get_pano(self, **kwargs):
        pano_url = self.get_pano_url(**kwargs)
        response = requests.get(pano_url, stream=True)
        return Image.open(response.raw)

    def get_metadata(self, **kwargs):
        metadata_url = self.get_metadata_url(**kwargs)
        response = requests.get(metadata_url, stream=True)
        return response.json()

    def get_pano_url(self, **kwargs):
        pano_params = self.get_parameters(**kwargs)
        return requests.get(self.pano_API_url, params=pano_params).url

    def get_metadata_url(self, **kwargs):
        pano_params = self.get_parameters(**kwargs)
        return requests.get(self.metadata_API_url, params=pano_params).url

    def get_parameters(self, **kwargs):
        '''return a new parameter dictionary with default values and updated arguments. '''
        pano_params = self.params.copy()
        return {**pano_params, **kwargs}

    # update default parameters.
    def update_parameters(self, **kwargs):
        '''update default parameters. '''
        self.params = self.get_parameters(**kwargs)
        return self.params

    def get_encoded_signature(self):
        # implementation
        return self.signature

    def get_heading(self, pano_lat, pano_lng, target_lat, target_lng):
        dLng = target_lng - pano_lng
        X = cos(target_lat) * sin(dLng)
        Y = cos(pano_lat) * sin(target_lat) - sin(pano_lat) * cos(target_lat) * cos(dLng)
        bearing = arctan2(X, Y)

        return ((degrees(bearing) + 360) % 360)

    def __call__(self, target_lat=40.7557592, target_lng=-73.9542045, address='', **kwargs):
        is_address = isinstance(target_lat, str)

        if is_address:
            target_location = target_lat
        else:
            target_location = '{},{}'.format(target_lat, target_lng)

        metadata = self.get_metadata(location=target_location, **kwargs)
        pano_lat = metadata['location']['lat']
        pano_lng = metadata['location']['lng']
        pano_latlng = '{},{}'.format(pano_lat, pano_lng)

        if ('heading' not in kwargs) and (not is_address):
            target_heading = self.get_heading(pano_lat, pano_lng, target_lat, target_lng)
            kwargs['heading'] = target_heading

        kwargs['location'] = pano_latlng
        pano = self.get_pano(**kwargs)
        return pano, metadata

    # 1. get_megadata
    # 2. get_heading: calculate heading: relative direction.
    # 3. get_params: return updated params



st.title('Street View Image')

# Initialization
KEY = st.text_input('Google Street View API KEY')
streetview = street_views(KEY)

numLat = st.sidebar.number_input('Lat', value=42.43849650076074)
numLong = st.sidebar.number_input('Long', value=-76.50318614115257)

# st.text_input('FOV')
heading = st.sidebar.slider('Heading', min_value=0, max_value=360, value=186)
fov = st.sidebar.slider('FOV', min_value=0, max_value=150, value=20)

if st.checkbox('Live update') or st.button('Request'):
    streetview = street_views(KEY, fov=80, heading=30, radius=100, source='default')
    # img, meta = streetview(42.44, -76.50, heading=186, fov=20)
    img, meta = streetview(numLat, numLong, heading=heading, fov=fov)

    st.image(img)

