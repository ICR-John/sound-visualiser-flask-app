""" Created by Beatrix Popa """
# the two Dash apps are based on the Dash apps submitted for CW1 by our team 17

import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objects as go
from dash.dependencies import Input, Output
from my_app.models import Instruments, Sounds
from dash_app.soundsdata import SoundData

# prepare the data
sd = SoundData()
marks = {0: 'C4', 1: 'D4', 2: 'E4', 3: 'F4', 4: 'G4', 5: 'A4', 6: 'B4', 7: 'C5'}


def init_demo(flask_app):
    """ Create the demo plotly dash app """

    demo = dash.Dash(__name__, server=flask_app,
                     routes_pathname_prefix="/demo/")
    fig = go.Figure()
    fig.update_layout(
        plot_bgcolor='#000000',
        paper_bgcolor='#0e0339',
        font_color='#b7b2b2', )

    demo.layout = html.Div([
        html.Nav(className='navbar', children=[
            html.Div(className='navbar-nav', children=[
                html.A(className='nav-item container-fluid', href='/', children=[
                    html.Img(alt='wavy', className='navbar-brand', src=demo.get_asset_url('wavy_small.png'))])])]),
        html.Div(style={'backgroundColor': '#0e0339'}, children=[
            html.Br(),
            html.H2('Demo plot', className='text-center'),
            html.H4('Frequency breakdown for a flute', className='text-center'),
            html.Br(),
            html.P(
                'Enjoying this plot? If you would like to access many other instruments and hundreds of recordings, create an account now!'),
            html.A('Sign up', className='btn ', href='/signup'),
            dcc.Graph(id="demo_figure", figure=fig),
            dcc.Slider(id='note-slider', min=0, max=7, marks=marks),
        ])])

    init_demo_callbacks(demo)

    return demo


def init_demo_callbacks(demo):
    """ initialise the calbacks for the demo plot """

    @demo.callback(Output('demo_figure', 'figure'),
                   Input('note-slider', 'value'),
                   Input('note-slider', 'marks'))
    def update_demo_figure(value, marks):
        """ update the figure when the slider value is changed """
        if value is None:
            value = 0
        note = marks[str(value)]
        figure = sd.create_plot(1, note)  # instrument no.1 is the flute
        return figure


def init_dashboard(flask_app):
    """Create the main Plotly Dash dashboard."""

    # create the empty figure that will be updated by the initial callback
    fig = go.Figure()
    fig.update_layout(
        plot_bgcolor='#000000',
        paper_bgcolor='#0e0339',
        font_color='#b7b2b2', )

    dash_app = dash.Dash(__name__, server=flask_app,
                         routes_pathname_prefix="/dash_app/")
    options = prepare_instruments_for_dropdown()

    dash_app.layout = html.Div([
        html.Nav(className='navbar', children=[
            html.Div(className='navbar-nav', children=[
                html.A(className='nav-item container-fluid', href='/', children=[
                    html.Img(alt='wavy', className='navbar-brand', src=dash_app.get_asset_url('wavy_small.png'))])]),
            html.Div(className='navbar-nav', children=[
                html.A('Log out', className='nav-item nav-link btn', href='/logout')])]),
        html.Div(style={'backgroundColor': '#0e0339'}, children=[
            html.Br(),
            html.H2('Frequency breakdown for different notes', className='text-center'),
            html.Br(),
            html.H4('Choose the instrument below: '),
            dcc.Dropdown(id='dropdown_instrument',
                         options=options,
                         value=1,
                         style={'backgroundColor': 'black', 'color': 'black', 'border': 'black'}),
            html.Br(),
            html.P('Please be patient, it takes a second to load :)'),
            dcc.Graph(id="frequency_figure", figure=fig),
            dcc.Slider(id='note-slider', step=None),
        ])])

    init_callbacks(dash_app)

    return dash_app


def init_callbacks(dash_app):
    """ initialise the callbacks for the main apps """

    @dash_app.callback(Output('note-slider', 'marks'),
                       Output('note-slider', 'min'),
                       Output('note-slider', 'max'),
                       Input('dropdown_instrument', 'value'))
    def update_marks(value):
        """ update the markings on the slider when a new instrument is selected from the dropdown"""
        if value is None:
            value = 1
        marks = get_notes_from_db(value)
        return marks, 0, len(marks)

    @dash_app.callback(
        Output('frequency_figure', 'figure'),
        [Input('note-slider', 'value'),
         Input('note-slider', 'marks'),
         Input('dropdown_instrument', 'value')])
    def update_figure(value, marks, instrument):
        """ update the figure when the slider value changed """
        if value is None:
            value = 0
        note = marks[str(value)]
        figure = sd.create_plot(instrument, note)
        return figure



def get_notes_from_db(instrument_id):
    """ This function queries the database for all the notes that have recordings for the given instrument. """
    marks = {}
    index = 0
    all_sounds = Sounds.query.filter(Sounds.instrument_id == instrument_id).all()
    for recording in all_sounds:
        marks[index] = recording.note
        index += 1
    return marks


def prepare_instruments_for_dropdown():
    """ Prepare the dictionary for the dropdown menu with all instruments from the database"""
    all_instruments = Instruments.query.all()
    options = []
    for value in all_instruments:
        options.append({'label': value.name, 'value': value.instrument_id})
    return options
