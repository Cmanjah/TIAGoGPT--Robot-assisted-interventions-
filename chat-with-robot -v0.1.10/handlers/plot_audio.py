import wave
import numpy as np
import matplotlib.pyplot as plt

wav_obj = wave.open('output.wav', 'r')

sample_freq = wav_obj.getframerate()
print("Frame rate: ", sample_freq)

n_channels  = wav_obj.getnchannels()
print(f'No of channels: {n_channels}')

sample_width = wav_obj.getsampwidth()
print(f"Sample width: {sample_width}")

print("Values of a frame (parameters): ", wav_obj.getparams())


n_samples = wav_obj.getnframes()
print("No of samples: ", n_samples)

t_audio = n_samples/sample_freq
print(f"Duration: {t_audio} seconds")

signal_wave = wav_obj.readframes(n_samples)
signal_array = np.frombuffer(signal_wave, dtype=np.int16)
print(signal_array.shape)

# for stereo:
#l_channel = signal_array[0::2]
#r_channel = signal_array[1::2]

times = np.linspace(0, n_samples/sample_freq, num=n_samples)

plt.figure(figsize=(15, 5))
plt.plot(times, signal_array)
plt.title('Audio Signal')
plt.ylabel('Signal Value')
plt.xlabel('Time (s)')
plt.xlim(0, t_audio)
plt.show()

plt.figure(figsize=(15, 5))
plt.specgram(signal_array, Fs=sample_freq, vmin=-20, vmax=50)
plt.title('Left Channel')
plt.ylabel('Frequency (Hz)')
plt.xlabel('Time (s)')
plt.xlim(0, t_audio)
plt.colorbar()
plt.show()