# Audio Pronunciation Setup Guide

This guide explains how the audio pronunciation feature works in the Thai Tone Analyzer app.

## How It Works

The app uses **gTTS (Google Text-to-Speech)** - a free Python library that provides text-to-speech functionality without requiring API keys or complex setup.

## Features

- **Free to use** - No API keys or billing required
- **Thai language support** - Automatically detects and pronounces Thai text
- **Multiple voice options** - Various Thai voices available
- **Easy integration** - Works out of the box

## Technical Details

### Dependencies

The audio feature is included in `requirements.txt`:

```
gtts==2.5.4
```

### Implementation

The audio generation is handled by the `/audio` endpoint in `app.py`:

```python
def generate_audio(text, voice_name="th"):
    """Generate audio for Thai text using gTTS (Google Text-to-Speech)."""
    try:
        # Create gTTS object
        tts = gTTS(text=text, lang='th', slow=False)
        
        # Create a temporary file to store the audio
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
            tts.save(tmp_file.name)
            
            # Read the file and convert to base64
            with open(tmp_file.name, 'rb') as audio_file:
                audio_content = audio_file.read()
                audio_base64 = base64.b64encode(audio_content).decode('utf-8')
            
            # Clean up the temporary file
            os.unlink(tmp_file.name)
            
        return audio_base64
```

### Frontend Integration

The audio is played using HTML5 audio elements:

```javascript
function playPronunciation(text) {
    // Send request to /audio endpoint
    fetch('/audio', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            text: text,
            voice: selectedVoice
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Create audio element and play
            const audio = new Audio('data:audio/mp3;base64,' + data.audio);
            audio.play();
        }
    });
}
```

## Usage

### In the Web App

1. **Enter a Thai word** in the input field
2. **Click "🔊 Play Audio"** button
3. **The word will be pronounced** using gTTS

### Available Voices

gTTS provides several Thai voice options:
- **Default Thai voice** - Natural Thai pronunciation
- **Slow speech option** - Available by modifying the `slow` parameter

## Advantages of gTTS

### ✅ Pros
- **Free** - No cost or API limits
- **Simple setup** - No API keys required
- **Good quality** - Decent Thai pronunciation
- **Reliable** - Works consistently
- **Lightweight** - Small dependency

### ⚠️ Limitations
- **Internet required** - Needs connection to Google's servers
- **Limited customization** - Fewer voice options than paid services
- **Rate limiting** - Google may limit requests if overused
- **No offline support** - Requires internet connection

## Troubleshooting

### Common Issues

1. **"Audio not playing"**
   - Check internet connection
   - Verify browser supports HTML5 audio
   - Check browser console for errors

2. **"Audio generation failed"**
   - Check Flask app logs
   - Verify gTTS is installed: `pip install gtts==2.5.4`
   - Test with simple text first

3. **"Slow audio generation"**
   - This is normal for gTTS
   - Audio is generated on-demand
   - Consider caching for frequently used words

### Testing Audio Feature

You can test the audio feature directly:

```python
from gtts import gTTS
import tempfile
import os

# Test gTTS
tts = gTTS(text='สวัสดี', lang='th', slow=False)
tts.save('test.mp3')
print("Audio generated successfully!")
```

## Production Considerations

### For Railway Deployment

- **No additional setup required** - gTTS works out of the box
- **Environment variables** - Not needed for gTTS
- **Dependencies** - Already included in requirements.txt

### Performance

- **First request** - May be slower (generates audio)
- **Subsequent requests** - Faster (cached by browser)
- **Memory usage** - Minimal (temporary files cleaned up)

## Alternative Options

If you need more advanced features:

1. **Google Cloud Text-to-Speech** - Higher quality, more voices, but requires API key
2. **Amazon Polly** - AWS service with good Thai support
3. **Microsoft Azure Speech** - Enterprise-grade TTS
4. **Local TTS** - Offline solutions like espeak

## Support

If you encounter issues:

1. **Check internet connection** - gTTS requires internet
2. **Verify gTTS installation** - `pip list | grep gtts`
3. **Test with simple text** - Try "สวัสดี" first
4. **Check Flask logs** - Look for error messages
5. **Browser compatibility** - Ensure HTML5 audio support

## Conclusion

The gTTS implementation provides a simple, free solution for Thai text-to-speech that works well for educational purposes. It requires no setup and integrates seamlessly with the Flask app.