# Thai Tone Analyzer

A Flask web application that determines the tone of Thai words and explains the rules that make them that tone.

## Features

- **Tone Detection**: Analyzes Thai words and determines their tone (Mid, Low, Falling, High, Rising)
- **Rule Explanation**: Provides detailed explanations of the tone rules applied
- **Romanization**: Converts Thai script to Latin alphabet using RTGS system
- **English Translation**: Provides English meanings for common Thai words
- **Consonant Cluster Detection**: Correctly identifies and analyzes consonant clusters
- **Multi-syllable Support**: Handles words with multiple syllables
- **Interactive Interface**: Clean, modern web interface with example words
- **Real-time Analysis**: Instant tone analysis as you type

## Thai Tone System

Thai has 5 distinct tones:
- **Mid Tone** (เสียงสามัญ): Level pitch
- **Low Tone** (เสียงเอก): Low pitch  
- **Falling Tone** (เสียงโท): High to low pitch
- **High Tone** (เสียงตรี): High pitch
- **Rising Tone** (เสียงจัตวา): Low to high pitch

## Tone Rules

The tone of a Thai syllable is determined by:

1. **Initial Consonant Class**:
   - **Mid-class**: ก, จ, ด, ต, บ, ป, อ
   - **High-class**: ข, ฉ, ฐ, ถ, ผ, ฝ, ศ, ษ, ส, ห
   - **Low-class**: ค, ฆ, ง, ช, ซ, ฌ, ญ, ฑ, ฒ, ณ, ท, ธ, น, พ, ฟ, ภ, ม, ย, ร, ล, ว, ฬ, ฮ

2. **Syllable Type**:
   - **Live syllables**: End in long vowels or sonorant consonants (ม, น, ง, ย, ร, ล, ว)
   - **Dead syllables**: End in short vowels or stop consonants (ก, ด, บ, ป, จ, ต)

3. **Tone Marks**:
   - ่ (mai ek): Low tone mark
   - ้ (mai tho): Falling tone mark
   - ๊ (mai tri): High tone mark
   - ๋ (mai chattawa): Rising tone mark

## Installation

1. Clone or download this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the Flask application:
   ```bash
   python app.py
   ```

2. Open your web browser and go to `http://localhost:5001`

3. Enter a Thai word in the input field and click "Analyze Tone"

4. The application will display:
   - The determined tone
   - Detailed explanation of the rules applied

## Example Words

Try these example words to see the tone analyzer in action:

- **กา** (Mid tone) - Mid-class consonant + live syllable
- **ขา** (Rising tone) - High-class consonant + live syllable  
- **คา** (Mid tone) - Low-class consonant + live syllable
- **เธอ** (Mid tone) - Low-class consonant + live syllable (starts with vowel symbol)
- **เกา** (Mid tone) - Mid-class consonant + live syllable (starts with vowel symbol)
- **ไก่** (Low tone) - Mid-class consonant + mai ek (starts with vowel symbol)
- **ก่า** (Low tone) - Mid-class consonant + mai ek
- **ข่า** (Low tone) - High-class consonant + mai ek
- **ค่า** (Falling tone) - Low-class consonant + mai ek
- **ก๊า** (High tone) - Any consonant + mai tri
- **ก๋า** (Rising tone) - Any consonant + mai chattawa

## Technical Details

The application uses a rule-based approach to determine tones:

1. **Character Analysis**: Identifies the initial consonant and its class
2. **Vowel Recognition**: Properly identifies both simple and complex vowels (diphthongs)
3. **Syllable Classification**: Determines if the syllable is live or dead based on vowel length
4. **Tone Mark Detection**: Checks for presence of tone marks
5. **Rule Application**: Applies the appropriate tone rules based on the analysis

### Complex Vowels (Diphthongs) Supported:
- **เ_อ** (oe) - as in เธอ (thoe)
- **เ_า** (ao) - as in เกา (gao)  
- **เ_ีย** (ia) - as in เกีย (gia)
- **เ_ือ** (uea) - as in เกือ (guea)
- **ไ_** (ai) - as in ไก่ (gai)
- **ใ_** (ai) - as in ใก้ (gai)

### Special อ (Zero Consonant) Cases:
- **Regular zero consonant**: อา, อี, อู, เอา, โอ, อะไร
- **Silent tone modifier**: อย่า, อยาก, อยู่, อย่าง (all have low tone due to mid-class consonant rules)

### Consonant Clusters:
- **Common clusters**: กร, กล, ขร, ขล, คร, คล, ตร, ปร, ปล, พร, พล
- **Tone determination**: Based on the class of the first consonant in the cluster
- **Examples**: โกรธ (low tone), กรอก (low tone), กล้อง (falling tone)

### Translation and Romanization:
- **Romanization**: Uses the Royal Thai General System of Transcription (RTGS)
- **Translation**: Built-in dictionary with common Thai words and their English meanings
- **Examples**: 
  - โกรธ → "kont" (romanized) → "to be angry" (translation)
  - สวัสดี → "satti" (romanized) → "hello, goodbye" (translation)

## Limitations

This is a simplified implementation of Thai tone rules. Some complex cases or exceptions may not be handled perfectly. The application focuses on the most common tone patterns and rules.

## Contributing

Feel free to improve the tone detection logic or add more comprehensive rule handling!
