import struct
import time
import pandas as pd
from scipy.fftpack import fft
import numpy as np
import pyaudio
import matplotlib.pyplot as plt
import keyboard
import asyncio

CHUNK = 1024 * 4  # 1 sec
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100  # data per sec

p = pyaudio.PyAudio()

stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    output=True,
    frames_per_buffer=CHUNK
)


async def main():
    # set up dict
    f = {"Time": [], "Data": [], "Fourier Data": []}
    # initial mod
    mod_count = 1
    df = pd.DataFrame(f)

    # objects for line
    fig, (ax, ax2) = plt.subplots(2, figsize=(15, 8))
    x = np.arange(0, 2 * CHUNK, 2)  # equivalent to lin-space
    x_fft = np.linspace(0, RATE, CHUNK)  # for fourier

    # time axis and initial line
    tx = (x / RATE)
    line, = ax.plot(tx, np.random.rand(len(tx)), '-', lw=2)
    line_fft, = ax2.plot(x_fft, np.random.rand(CHUNK), '-', lw=2)

    # basic formatting for the axes
    ax.set_title('AUDIO WAVEFORM')
    ax.set_xlabel('Time')
    ax.set_ylabel('volume')
    ax.set_xlim(0, 2 * CHUNK / RATE)
    ax.set_ylim(0, 255)

    # format for frequency
    ax2.set_title('Fourier Spectrum analysis')
    ax2.set_xlabel('Frequency')
    ax2.set_ylabel('Percentage')
    ax2.set_xscale('log')
    ax2.set_xlim(20, RATE / 2)

    plt.grid(which='both', axis='both')

    # show the plot
    plt.show(block=False)

    print('stream started')

    # for measuring frame rate
    start_time = time.time()

    while True:
        if keyboard.is_pressed('ESC'):
            break

        elapsed_time = time.time() - start_time
        # binary data
        data = stream.read(CHUNK)
        # print(tx)

        # convert data to integers, make np array, then offset it by 127
        data_int = struct.unpack(str(2 * CHUNK) + 'B', data)

        # create np array and offset by 128
        data_np = np.array(data_int, dtype='b')[::2] + 128

        # set data updates
        ax.set_xlim(0 + elapsed_time, 2 * CHUNK / RATE + elapsed_time)
        line.set_xdata(tx + elapsed_time)
        line.set_ydata(data_np)

        # fft function
        y_fft = fft(data_int)
        # sets line data, abs to remove conjugate, Chunk since conjugates in last half and len = 2 * chunk
        y_fft_norm = abs(y_fft[0:CHUNK]) / (128 * CHUNK)

        # if grater than x s then add to multiple then run under
        if elapsed_time > 5 * mod_count:
            mod_count += 1

            f["Time"], f["Data"], f["Fourier Data"] = elapsed_time, data_np, y_fft_norm
            df2 = pd.DataFrame({k: pd.Series(v) for k, v in f.items()})
            y_sor = y_fft_norm.sort()
            await plot_sin(y_sor[-5:])

            # print(df)
            df.append(df2, ignore_index=True)  # adds to dict

        line_fft.set_ydata(y_fft_norm)
        await asyncio.sleep(0.1)
        fig.canvas.draw()
        fig.canvas.flush_events()


# used to plot sin graphs of fourier
async def plot_sin(frq):
    t_sin = np.linspace(0, 2, num=50)
    y_sin = []
    print(len(t_sin))

    for gra in frq:  # turns each frequency into sine graph by making ag frq and then a list of x
        omega = 2 * np.pi / gra  # ang frq
        for n in range(len(t_sin)):
            y_sin.append(np.sin(omega * t_sin[n]))

        plt.plot(t_sin, y_sin)
        await asyncio.sleep(0.1)
    plt.xlabel("Time")
    plt.ylabel("Amplitude")
    plt.title("Five largest contributing Frequencies")
    plt.show()


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
