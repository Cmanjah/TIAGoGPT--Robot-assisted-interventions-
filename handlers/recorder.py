import pyaudio
import numpy as np
import soundfile as sf
import time, os
from handlers.manager import AudioManager


class AudioRecorder:
    def __init__(self, duration=10, sample_rate=44100, channels=1, max_threshold=2000, min_threshold=20, silence_duration=1):
        self.duration = duration
        self.sample_rate = sample_rate
        self.channels = channels
        self.max_threshold = max_threshold
        self.min_threshold = min_threshold
        self.silence_duration = silence_duration

        self.audio_manager = AudioManager()
        # self.audio = pyaudio.PyAudio()
        self.frames = []
        self.stream = None
        self.is_recording = False

    def start_recording(self):
        self.frames = []
        silence_frames = []
        self.is_recording = True
        recording_started = False
        silence_started = False
        start_time = None
        silence_start_time = None
        # self.audio_manager = AudioManager()
        self.audio = pyaudio.PyAudio()

        print("Listening...")

        self.stream = self.audio.open(format=pyaudio.paInt16,
                                 channels=self.channels,
                                 rate=self.sample_rate,
                                 input=True,
                                 frames_per_buffer=1024)

        while self.is_recording:
            data = self.stream.read(1024)
            audio_data = np.frombuffer(data, dtype=np.int16)
            energy = np.abs(audio_data).mean()

            if energy > self.max_threshold:
                if not recording_started:
                    print("Recording started!")
                    print("Someone seems to be talking...")
                    recording_started = True
                    start_time = time.time()
                self.frames.append(audio_data)

            elif recording_started:
                self.frames.append(audio_data)
                if energy < self.min_threshold:
                    # if not silence_started:
                    silence_started = True
                    silence_start_time = time.time()
                    silence_frames.append(audio_data)
                    if len(silence_frames) * 1024 / (self.sample_rate * self.channels) >= self.silence_duration:
                        print("Recording ended")
                        print("End of speech detected...")
                        break

            if len(self.frames) * 1024 / (self.sample_rate * self.channels) >= self.duration:
                print("Maximum recording duration reached...")
                print("I have to stop listening. Let me respond to what you've just asked")
                break

        print("Recording completed.")

        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()

        if len(self.frames) > 0:
            # output_file = "recorded_audio.wav"

            self.audio_manager.set_audio_path("recorded")
            file_name = "recorded_audio_"
            output_file = f"{self.audio_manager.get_audio_path()}/{file_name}{self.audio_manager.current_timestamp()}.wav"
            if not os.path.exists(self.audio_manager.get_audio_path()):
                os.makedirs(self.audio_manager.get_audio_path())

            audio_data = np.concatenate(self.frames)
            sf.write(output_file, audio_data, self.sample_rate, 'PCM_16')
            print(f"Recorded audio saved as {output_file}")
            if start_time is not None:
                elapsed_time = time.time() - start_time
                print(f"Start time: {start_time}")
                print(f"Elapsed time: {elapsed_time} seconds")
            
            return output_file
        else:
            print("No audio recorded.")

        # These section is not too important. Therefore, it will be sideline
        if len(silence_frames) > 0:
            reduced_output_file = "reduced_energy_audio.wav"
            reduced_audio_data = np.concatenate(silence_frames)
            sf.write(reduced_output_file, reduced_audio_data, self.sample_rate, 'PCM_16')
            print(f"Reduced energy audio saved as {reduced_output_file}")
            if silence_start_time is not None:
                elapsed_time = time.time() - silence_start_time
                print(f"Start silence time: {silence_start_time}")
                print(f"Elapsed silence time: {elapsed_time} seconds")
        else:
            print("No frames with reduced energy.")

     
    def stop_recording(self):
        self.is_recording = False
        self.frames = []
        
    def pause_recording(self):
        self.is_recording = False

# Usage example
# recorder = AudioRecorder()
# recorder.start_recording()

