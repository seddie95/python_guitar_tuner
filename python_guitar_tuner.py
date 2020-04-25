import pyaudio
import wave
import struct
import numpy as np
import math
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# variables for sampling Audio
Chunk = 4096
Format = pyaudio.paInt16
Channels = 2
RATE = 44100


# Kaiser window to smooth values
window = np.kaiser(Chunk*2,14)

#instantiate pyaudio
p = pyaudio.PyAudio()

# Open the stream and set parameters	
stream = p.open(
	format=Format,
	channels=Channels,
	rate=RATE,
	input=True,
	frames_per_buffer=Chunk
	)	

#function to obtain rms of data
def rms(data):
    count = len(data)/2
    format = "%dh"%(count)
    shorts = struct.unpack( format, data )
    sum_squares = 0.0
    for sample in shorts:
        n = sample * (1.0/32768)
        sum_squares += n*n
    return math.sqrt( sum_squares / count )

# Guitar frequencies  
frequencies = {
	82.41:"E2",
	164.81:"E2", 
	110:"A4", 
	146.8:"D3", 
	196:"G3",
	392:"G3",
	246.9:"B3",
	329.63:"E4"
}


# set initial graph
fig, ax = plt.subplots()
#set the bounds of the graph
ax.set_ylim([0, 5])  
ax.set_xlim([-5, 5])

#set origin and length of line
x, y = (0,0)
length = 5

# Find the end point
endy = length * math.sin(math.radians(90))
endx = length * math.cos(math.radians(90))

# End point Line denoting correct note
cory = 10 * math.sin(math.radians(90))
corx = 10 * math.cos(math.radians(90))

#correct line
ax.plot([x, 0], [y, 5], color= 'grey', ls='--', lw= 3 )

# updated line
line, = ax.plot([x, endx], [y, endy],color='red', lw=4)



	
# continuously take in audio with the microphone
def animate_frequency(i):
	# obtain the data in bytes from the stream 
	data= stream.read(Chunk)
	

	#get data in int form
	data_int = np.array(wave.struct.unpack("%dh"%(len(data)/2),\
                                         data))*window
	
	# get the rms to caclulate the volume in decibel
	rms_data = rms(data)
	decibel = (20 * math.log10(rms_data))
	

	# Take the fft and square each value
	fftData=abs(np.fft.fft(data_int))**2

	# find the maximum
	which = fftData[1:].argmax() + 1
	
		
    # use quadratic interpolation around the max
	if which != len(fftData)-1:
		y0,y1,y2 = np.log(fftData[which-1:which+2:])
		x1 = (y2 - y0) * .5 / (2 * y1 - y2 - y0)
		
		# find the frequency and output it
		freq = (which+x1)*RATE/Chunk
		
		#Find the nearewst pitch to the frequency
		nearest = min(frequencies, key=lambda x:abs(x-freq))
		pitch= frequencies[nearest]
		
		# get difference between  nearest and actual frequency
		diff = round((freq - nearest )*-1,2)
		
		# Display frequencies less than A4 and louder than -50 Decibels 
		if decibel> -50 and freq <440:
			
			# Ipdate line position using frequency
			pos= diff*1.8 +90
			
			# find the uupdated end of the line coordinates
			endx = length * math.cos(math.radians(pos))
			endy = length * math.sin(math.radians(pos))
			
			# Update the lines end coordinates 
			line.set_xdata([x, endx])
			line.set_ydata([y, endy])
			plt.title(f"Chord: {pitch},{diff}")
			
			# Change line colour depenidng on proximity to desired note
			if abs(diff) < 1:
				line.set_color('green') 
			
			elif abs(diff) < 3 and abs(diff) > 1 :
				line.set_color('yellow') 
				
			else:
				line.set_color('red')

			return line, 
			
if __name__ == "__main__":			
	animation = FuncAnimation(fig, func=animate_frequency,
			frames=np.arange(0, 10, 0.1), interval=100,)
	plt.show()
