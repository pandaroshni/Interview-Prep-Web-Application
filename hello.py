from gtts import gTTS

# Create a gTTS object
tts = gTTS(text='Hello Welcome to SKill Mitra', lang='en')

# Save the audio file
tts.save('hello.mp3')
