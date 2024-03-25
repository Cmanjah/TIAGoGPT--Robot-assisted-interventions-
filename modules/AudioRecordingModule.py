# Import necessary libraries
import pyaudio
import numpy as np
import soundfile as sf
import time, os
from controller.AppController import AudioManager


# User Voice Input Layer (UIL): Automatic Speech Recognition (ASR)
class AudioRecorder:
    def __init__(self, duration=20, sample_rate=44100, channels=1, max_threshold=2000, min_threshold=20, silence_duration=1):
        # Initialize recording parameters
        self.duration = duration
        self.sample_rate = sample_rate
        self.channels = channels
        self.max_threshold = max_threshold
        self.min_threshold = min_threshold
        self.silence_duration = silence_duration

        # Initialize AudioManager for logging and audio management
        self.audio_manager = AudioManager()
        self.frames = []
        self.stream = None
        self.is_recording = False



    #### Speech Activity Detection (SAD) ####
    def startRecording(self):
        # Initialize variables for recording
        self.frames = []
        silence_frames = []
        self.is_recording = True
        recording_started = False
        silence_started = False
        start_time = None
        silence_start_time = None
        self.audio = pyaudio.PyAudio()

        print("Listening...")

        # Open audio stream
        self.stream = self.audio.open(format=pyaudio.paInt16,
                                 channels=self.channels,
                                 rate=self.sample_rate,
                                 input=True,
                                 frames_per_buffer=1024)

        # Recording loop
        while self.is_recording:
            data = self.stream.read(1024)
            audio_data = np.frombuffer(data, dtype=np.int16)
            energy = np.abs(audio_data).mean()

            # Check for speech start
            if energy > self.max_threshold:
                if not recording_started:
                    print("Recording started at maximum threshold-----------------------------------SUCCESS")
                    # Log audit event for file creation
                    self.audio_manager.logAuditEvent('Voice Recording', f"Recording started at maximum threshold")

                    recording_started = True
                    start_time = time.time()
                self.frames.append(audio_data)

            # Check for end of speech
            elif recording_started:
                self.frames.append(audio_data)
                if energy < self.min_threshold:
                    # if not silence_started:
                    silence_started = True
                    silence_start_time = time.time()
                    silence_frames.append(audio_data)
                    if len(silence_frames) * 1024 / (self.sample_rate * self.channels) >= self.silence_duration:
                        print("End of speech detected before the maximum recording duration---------------SUCCESS")
                        self.audio_manager.logAuditEvent('Voice Recording', f"End of speech detected before the maximum recording duration")
                        break

            # Check for maximum recording duration
            if len(self.frames) * 1024 / (self.sample_rate * self.channels) >= self.duration:
                print("Maximum recording duration reached..................................................SUCCESS")
                self.audio_manager.logAuditEvent('Voice Recording', f"Maximum recording duration reached")
                break

        print("Recording completed.")

       # Stop and close the audio stream
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()

        ##### Audio Recording Section #####
        output = self.__speechRecorder(
                            frames=self.frames, 
                            audio_manager=self.audio_manager, 
                            sample_rate=self.sample_rate, 
                            start_time=start_time, 
                            silence_frames=silence_frames, 
                            silence_start_time=silence_start_time
                            )
        return output


    ##### PRIVATE METHOD: AUDIO RECORDING #####
    def __speechRecorder(self, frames, audio_manager, sample_rate, start_time, silence_frames, silence_start_time):
        # Save recorded audio
        if len(frames) > 0:

            self.audio_manager.set_audio_path("recorded")
            file_name = "recorded_audio_"
            output_file = audio_manager.audioTempDir(f"{file_name}{audio_manager.getCurrentTimestamp()}.wav")
            audio_data = np.concatenate(frames)
            audio_manager.saveAudio(output_file, audio_data, sample_rate)
            print("Recorded audio saved as ---------------------------SUCCESS")
            audio_manager.logAuditEvent('Voice Recording created', f"Recording {output_file} created and encrypted")
            if start_time is not None:
                elapsed_time = time.time() - start_time
                print(f"Elapsed time: {elapsed_time} seconds")
            
            return output_file
        else:
            print("No audio recorded.")

        # Process silence frames (These section is not too important. Therefore, it will be sideline)
        if len(silence_frames) > 0:
            reduced_output_file = "reduced_energy_audio.wav"
            reduced_audio_data = np.concatenate(silence_frames)
            sf.write(reduced_output_file, reduced_audio_data, sample_rate, 'PCM_16')
            if silence_start_time is not None:
                elapsed_time = time.time() - silence_start_time
                print(f"Elapsed silence time: {elapsed_time} seconds")
        else:
            print("No frames with reduced energy.")
        
     
    def stopRecording(self):
        try:
           # Reset recording state and clean up resources
            self.frames = []
            if self.is_recording == True:
                self.is_recording = False
            if not self.stream.is_stopped:
                self.stream.stop_stream()
                self.stream.close()
            if self.audio.open:
                self.audio.terminate()
            print("Recording Stopped--------------------------------------------------SUCCESS")
            self.audio_manager.logAuditEvent('Voice Recording', f"Recording Stopped")
        except Exception as e:
            print(f"There's error in stopping the audio - {e}")

        
    def pauseRecording(self):
        # Pause the recording process
        self.is_recording = False

