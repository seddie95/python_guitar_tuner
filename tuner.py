from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from matplotlib.animation import FuncAnimation
import numpy as np
import math
import matplotlib.pyplot as plt
from matplotlib.patches import Arc
from guitar import Guitar

# Set up the graph information
fig, ax = plt.subplots()

# set the color of the graph
fig.patch.set_facecolor('black')

# set the bounds of the graph
ax.set_ylim([2, 6])
ax.set_xlim([-5, 5])
ax.set_facecolor('black')

# Hide the ticks and labels
ax.set_yticklabels([])
ax.set_xticklabels([])
ax.xaxis.set_ticks_position('none')
ax.yaxis.set_ticks_position('none')

# set origin and length of line
x, y = (0, 0)
length = 4

# Find the end point
endy = length * math.sin(math.radians(90))
endx = length * math.cos(math.radians(90))

# correct line
ax.plot([x, 0], [y, 5], color='grey', ls='--', lw=3)

# updated line
line, = ax.plot([x, 0], [y, 5], color='red', lw=4)

# Set initial title
plt.title(f"Chord: ", color='green', fontsize=20)

# Add Arc
arc = Arc((0, 0), 10.5, 10.5, theta1=30, theta2=150, color='b', lw=3)
ax.add_artist(arc)

# Add labels for arc
plt.text(-5.5, 2.5, "-50Hz", color='g', fontsize=18, rotation=70)
plt.text(4.5, 2.5, "+50Hz", color='g', fontsize=18, rotation=-70)

# draw circle for 0Hz
circle = plt.Circle((0, 5.5), 0.1,  color='r')
ax.add_artist(circle)



def update_line(i, instrument):
    """ Function To update the end location
    of the line using the frequency data """
    # call the find frequency method
    freq_data = instrument.find_frequency()
    freq = freq_data[0]
    decibel = freq_data[1]

    # Find the nearest pitch to the frequency
    nearest = min(instrument.frequencies, key=lambda num: abs(num - freq))
    pitch = instrument.frequencies[nearest]

    # get difference between  nearest and actual frequency
    diff = round((freq - nearest) * -1, 2)

    # Display frequencies less than A4 and louder than -50 Decibels
    if decibel > -50 and freq < 440:

        # update line position using frequency
        # Show  +- 50Hz  from 30° to 150° ,(90°-30°)/50
        pos = diff * 1.2 + 90

        # find the updated end of the line coordinates
        x2 = 5 * math.cos(math.radians(pos))
        y2 = 5 * math.sin(math.radians(pos))

        # Update the lines end coordinates
        line.set_xdata([0, x2])
        line.set_ydata([0, y2])

        # Set the title text and design
        plt.title(f"Chord: {pitch},{diff}", color='green', fontsize=20)


        # Change line colour depending on proximity to desired note
        if abs(diff) < 1:
            line.set_color('green')

        elif 3 > abs(diff) > 1:
            line.set_color('yellow')

        else:
            line.set_color('red')

        return line,


if __name__ == "__main__":
    # instant Guitar  and TK classes
    guitar = Guitar()
    root = tk.Tk()
    root.wm_title("Guitar Tuner")
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().grid(column=0, row=1)
    animation = FuncAnimation(fig, func=update_line, frames=np.arange(0, 10, 0.1), interval=200, fargs=[guitar])

    tk.mainloop()
