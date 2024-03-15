""" Created by Beatrix Popa """

import numpy as np
import scipy.fftpack as fft
from my_app.models import Sounds
import soundfile as sf
from plotly.subplots import make_subplots
import plotly.graph_objects as go


class SoundData:
    """ Class for retrieving and structuring the data."""

    def create_plot(self, instrument_id, note):
        """ Creat the plotly dash plot for the given note and instrument """

        path = self.load_recordings_from_db(instrument_id, note)
        data, sampling_rate = sf.read(path)
        mono = self.make_single_channel(data)
        times = np.linspace(0, len(mono) / sampling_rate, num=len(mono))
        # calculating the fourier of the wave allows for the frequency breakdown
        fourier = fft.rfft(mono)
        freqf = fft.fftfreq(len(np.abs(fourier) ** 2), sampling_rate)

        # create and style the plotly dash plots
        fig = make_subplots(rows=2, cols=1, subplot_titles=(" ", " "))
        fig.add_trace(go.Scatter(x=times, y=mono), row=1, col=1)
        fig.add_trace(go.Scatter(x=freqf, y=abs(fourier), mode='lines'), row=2, col=1)
        fig.update_xaxes(title_text="Time (s)", range=[0, 3], row=1, col=1, gridcolor='#353436', zeroline=False)
        fig.update_yaxes(title_text="Magnitude", row=1, col=1, gridcolor='#353436')
        fig.update_xaxes(title_text="Frequency (Hz)", row=2, col=1, range=[0, 0.000005], gridcolor='#353436', zeroline=False)
        fig.update_yaxes(title_text="Magnitude", row=2, col=1, gridcolor='#353436')
        fig.update_layout(
            plot_bgcolor='#000000',
            paper_bgcolor='#0e0339',
            font_color='#b7b2b2')

        return fig

    def make_single_channel(self, data):
        """ Select a single channel from the available channels"""
        if len(data.shape) == 1:
            channel = np.transpose(data)
        if len(data.shape) == 2:
            channel = data[:, 0]
        return channel

    def load_recordings_from_db(self, instrument_id, note):
        """ Returns the path of the recording for the  given instrument playing the given note.
         At most one recording should exist for every given instrument and note."""
        recording = Sounds.query.filter(Sounds.instrument_id == instrument_id, Sounds.name.contains(note)).first()
        return recording.recording
