import pyaudio
import wave
import struct
import numpy as np
import math


class Guitar:
    Chunk = 4096
    Format = pyaudio.paInt16
    Channels = 2
    RATE = 44100
    p = pyaudio.PyAudio()
    stream = p.open(
        format=Format,
        channels=Channels,
        rate=RATE,
        input=True,
        frames_per_buffer=Chunk
    )
    frequencies = {
        82.41: "E2",
        164.81: "E2",
        110: "A4",
        146.8: "D3",
        196: "G3",
        392: "G3",
        246.9: "B3",
        329.63: "E4"
    }

    def blackman_window(self):
        window = np.blackman(self.Chunk * 2)
        return window

    def hamming_window(self):
        window = np.hamming(self.Chunk * 2)
        return window

    def kaiser_window(self):
        window = np.kaiser(self.Chunk * 2, 14)
        return window

    def find_volume(self, data):
        """Function to find the volume in decibel using input data"""
        count = len(data) / 2
        format = "%dh" % (count)
        shorts = struct.unpack(format, data)
        sum_squares = 0.0
        for sample in shorts:
            n = sample * (1.0 / 32768)
            sum_squares += n * n
        rms_data = math.sqrt(sum_squares / count)
        return 20 * math.log10(rms_data)

    def find_frequency(self):
        """Function to find the peak frequency of audio."""
        # obtain the data in bytes from the stream
        data = self.stream.read(self.Chunk)
        window = self.hamming_window()

        # get data in int form
        data_int = np.array(wave.struct.unpack("%dh" % (len(data) / 2), data)) * window

        # get the rms to calculate the volume in decibel
        decibel = self.find_volume(data)

        # Take the fft and square each value
        fftData = abs(np.fft.fft(data_int)) ** 2

        # find the maximum
        which = fftData[1:].argmax() + 1

        # use quadratic interpolation around the max
        if which != len(fftData) - 1:
            y0, y1, y2 = np.log(fftData[which - 1:which + 2:])
            x1 = (y2 - y0) * .5 / (2 * y1 - y2 - y0)

            # find the frequency and output it
            freq = (which + x1) * self.RATE / self.Chunk
            return freq, decibel

