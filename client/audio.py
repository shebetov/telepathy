import pyaudio
import wave


CHUNK = 512
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 8000


def record_to_file(filename, channels, rate, frames):
    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(2)
    wf.setframerate(rate)
    wf.writeframes(b''.join(frames))
    wf.close()


class AudioRecorderCM():
    def __init__(self):
        print('init method called')
        self.frames = []
        self.channels = None
        self.rate = None

    def __enter__(self):
        self.p = pyaudio.PyAudio()
        device_info = self.p.get_default_input_device_info()
        self.channels = CHANNELS  # device_info["maxInputChannels"]
        self.rate = RATE  # device_info["defaultSampleRate"]

        self.stream = self.p.open(
            format=FORMAT,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=CHUNK
        )

        print("* recording")
        return self

    def read_stream(self):
        data = self.stream.read(CHUNK)
        self.frames.append(data)
        return data

    def __exit__(self, exc_type, exc_value, exc_traceback):
        print("* done recording")
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()


class AudioPlayer:

    def __init__(self):
        print('init method called')
        self.p = pyaudio.PyAudio()

        device_info = self.p.get_default_output_device_info()
        self.channels = CHANNELS  # device_info["maxOutputChannels"]
        self.rate = RATE  # device_info["defaultSampleRate"]

        self.stream = self.p.open(format=FORMAT,
                        channels=self.channels,
                        rate=self.rate,
                        output=True)

    def play_bytes(self, data):
        return self.stream.write(data)

    def stop(self):
        print("* done playing")
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()


def test_audio_recorder():
    frames = []
    with AudioRecorderCM() as rec:
        while True:
            frames.append(rec.read_stream())


def test_audio_player():
    ap = AudioPlayer()
    ap.stop()


if __name__ == '__main__':
    test_audio_recorder()
