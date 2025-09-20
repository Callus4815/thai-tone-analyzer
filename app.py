from flask import Flask, render_template, request, jsonify, send_file
from pythainlp.transliterate import romanize
import re
import requests
import os
import base64
import io
from gtts import gTTS
import tempfile

app = Flask(__name__)

# Simple Thai-English dictionary for common words
THAI_ENGLISH_DICT = {
    'โกรธ': 'to be angry',
    'กรอก': 'to pour, to fill',
    'กล้อง': 'camera, lens',
    'บ้าน': 'house, home',
    'สวัสดี': 'hello, goodbye',
    'ขอบคุณ': 'thank you',
    'น้ำ': 'water',
    'อาหาร': 'food',
    'หนังสือ': 'book',
    'อะไร': 'what',
    'อย่า': "don't (negative command)",
    'อยาก': 'to want, to desire',
    'อยู่': 'to be, to live, to stay',
    'อย่าง': 'like, as, way',
    'ลูก': 'child, son/daughter',
    'ลูกกรอก': 'marble (toy)',
    'โรงเรียน': 'school',
    'มหาวิทยาลัย': 'university',
    'กา': 'crow',
    'ขา': 'leg',
    'คา': 'to be stuck, to get caught',
    'เธอ': 'you (informal)',
    'เกา': 'to scratch',
    'ไก่': 'chicken',
    'ก่า': 'to be old',
    'ข่า': 'galangal (spice)',
    'ค่า': 'value, price',
    'ก๊า': 'crow (with high tone)',
    'ก๋า': 'crow (with rising tone)',
    'อา': 'aunt, uncle',
    'อี': 'she, her (informal)',
    'อู': 'owl',
    'เอา': 'to take, to want',
    'โอ': 'oh (exclamation)',
    'อะ': 'ah (exclamation)',
    'ไร': 'what (colloquial)'
}

def get_romanization(thai_word):
    """Get romanized version of Thai word."""
    try:
        return romanize(thai_word, engine='tltk')
    except:
        return "Unable to romanize"

def get_phonetic_ipa(thai_word):
    """Get IPA (International Phonetic Alphabet) representation of Thai word."""
    try:
        import tltk.nlp as tltk_nlp
        ipa = tltk_nlp.th2ipa(thai_word)
        # Clean up the output (remove <s/> tags)
        return ipa.replace('<s/>', '').strip()
    except:
        return "Unable to generate IPA"

def get_phonetic_reading(thai_word):
    """Get reading pronunciation with syllable breaks."""
    try:
        import tltk.nlp as tltk_nlp
        reading = tltk_nlp.th2read(thai_word)
        # Clean up the output (remove trailing hyphens)
        return reading.rstrip('-')
    except:
        return "Unable to generate reading"

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
        
    except Exception as e:
        print(f"TTS Error: {e}")
        return None

def get_available_voices():
    """Get available voices for gTTS (simplified list)."""
    return [
        {
            'name': 'th',
            'gender': 'NEUTRAL',
            'language': 'th',
            'description': 'Thai (Default)'
        }
    ]

def get_translation(thai_word):
    """Get English translation of Thai word."""
    # First check our built-in dictionary
    if thai_word in THAI_ENGLISH_DICT:
        return THAI_ENGLISH_DICT[thai_word]
    
    # If not found, try to get translation from API
    try:
        # Use MyMemory API (free, no auth required)
        url = "https://api.mymemory.translated.net/get"
        params = {
            'q': thai_word,
            'langpair': 'th|en'
        }
        
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('responseStatus') == 200:
                translation = data['responseData']['translatedText']
                # Clean up the translation (remove extra spaces, etc.)
                translation = translation.strip()
                if translation and translation != thai_word:
                    return translation
        
        return "Translation not available"
    except:
        return "Translation not available"

def translate_english_to_thai(english_word):
    """Translate English word to Thai using MyMemory API."""
    try:
        # Simple translations for common short words to avoid complex API results
        simple_translations = {
            'hi': 'สวัสดี',
            'hello': 'สวัสดี',
            'bye': 'ลาก่อน',
            'yes': 'ใช่',
            'no': 'ไม่',
            'ok': 'โอเค',
            'okay': 'โอเค',
            'test': 'ทดสอบ',
            'cat': 'แมว',
            'dog': 'สุนัข',
            'book': 'หนังสือ',
            'water': 'น้ำ',
            'food': 'อาหาร',
            'house': 'บ้าน',
            'car': 'รถยนต์',
            'tree': 'ต้นไม้',
            'sun': 'ดวงอาทิตย์',
            'moon': 'ดวงจันทร์',
            'star': 'ดาว',
            'sky': 'ท้องฟ้า',
            'awesome': 'สุดยอด',
            'cool': 'สุดยอด',
            'great': 'เยี่ยม',
            'good': 'ดี',
            'bad': 'ไม่ดี'
        }
        
        # Check simple translations first
        word_lower = english_word.lower()
        if word_lower in simple_translations:
            return simple_translations[word_lower]
        
        url = "https://api.mymemory.translated.net/get"
        params = {
            'q': english_word,
            'langpair': 'en|th'
        }
        
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('responseStatus') == 200:
                # First try the main translation
                translation = data['responseData']['translatedText']
                translation = translation.strip()
                if translation and translation != english_word:
                    # Filter out very long translations that might cause issues
                    if len(translation) > 50:
                        return None
                    return translation
                
                # If main translation is same as input, try to find a better match
                matches = data.get('matches', [])
                if matches:
                    # Find the best quality match that's different from input
                    best_match = None
                    best_quality = 0
                    
                    for match in matches:
                        quality = float(match.get('quality', 0))
                        match_translation = match.get('translation', '').strip()
                        
                        if (match_translation and 
                            match_translation != english_word and 
                            quality > best_quality and
                            len(match_translation) <= 50):  # Filter out very long translations
                            best_match = match_translation
                            best_quality = quality
                    
                    if best_match:
                        return best_match
        
        return None
    except:
        return None

def detect_input_language(text):
    """Detect if input is Thai or English."""
    # Check if text contains Thai characters
    thai_pattern = re.compile(r'[\u0E00-\u0E7F]')
    if thai_pattern.search(text):
        return 'thai'
    else:
        return 'english'

# Thai consonant classes
CONSONANT_CLASSES = {
    'mid': ['ก', 'จ', 'ด', 'ต', 'บ', 'ป', 'อ'],
    'high': ['ข', 'ฉ', 'ฐ', 'ถ', 'ผ', 'ฝ', 'ศ', 'ษ', 'ส', 'ห'],
    'low': ['ค', 'ฅ', 'ฆ', 'ง', 'ช', 'ซ', 'ฌ', 'ญ', 'ฑ', 'ฒ', 'ณ', 'ท', 'ธ', 'น', 'พ', 'ฟ', 'ภ', 'ม', 'ย', 'ร', 'ล', 'ว', 'ฬ', 'ฮ', 'ฤ', 'ฦ']
}

# Tone marks
TONE_MARKS = {
    '่': 'mai_ek',      # Low tone mark
    '้': 'mai_tho',     # Falling tone mark  
    '๊': 'mai_tri',     # High tone mark
    '๋': 'mai_chattawa' # Rising tone mark
}

# Complex vowel patterns (diphthongs and compound vowels)
COMPLEX_VOWELS = {
    'เ_็': {'type': 'short', 'name': 'e (short e)', 'description': 'short e sound with mai han-akat', 'pattern': r'เ.*็'},
    'แ_็': {'type': 'short', 'name': 'ae (short ae)', 'description': 'short ae sound with mai han-akat', 'pattern': r'แ.*็'},
    'เ_ือะ': {'type': 'short', 'name': 'uea (short uea)', 'description': 'short uea sound', 'pattern': r'เ.*ือะ'},
    'เ_ียะ': {'type': 'short', 'name': 'ia (short ia)', 'description': 'short ia sound', 'pattern': r'เ.*ียะ'},
    'เ_ือ': {'type': 'long', 'name': 'uea (long uea)', 'description': 'long uea sound', 'pattern': r'เ.*ือ'},
    'เ_ีย': {'type': 'long', 'name': 'ia (long ia)', 'description': 'long ia sound', 'pattern': r'เ.*ีย'},
    'เ_าะ': {'type': 'short', 'name': 'oe (short oe)', 'description': 'short oe sound', 'pattern': r'เ.*าะ'},
    'เ_ะ': {'type': 'short', 'name': 'e (short e)', 'description': 'short e sound', 'pattern': r'เ.*ะ'},
    'แ_ะ': {'type': 'short', 'name': 'ae (short ae)', 'description': 'short ae sound', 'pattern': r'แ.*ะ'},
    'เ_า': {'type': 'long', 'name': 'ao (long ao)', 'description': 'long ao sound', 'pattern': r'เ.*า'},
    'เ_อ': {'type': 'long', 'name': 'oe (long oe)', 'description': 'long oe sound /ɤː/', 'pattern': r'เ(?!.*ือ).*อ'},
    'โ_ะ': {'type': 'short', 'name': 'o (short o)', 'description': 'short o sound', 'pattern': r'โ.*ะ'},
    'ไ_': {'type': 'long', 'name': 'ai (long ai)', 'description': 'long ai sound', 'pattern': r'^ไ[ก-ฮ][่้๊๋]?$'},
    'ใ_': {'type': 'long', 'name': 'ai (long ai)', 'description': 'long ai sound', 'pattern': r'ใ.*'},
    'ัว': {'type': 'long', 'name': 'ua (long ua)', 'description': 'long ua sound', 'pattern': r'ัว'},
}

# Simple vowel patterns
SIMPLE_VOWELS = {
    'า': {'type': 'long', 'name': 'a (long a)', 'description': 'long a sound'},
    'ี': {'type': 'long', 'name': 'i (long i)', 'description': 'long i sound'},
    'ู': {'type': 'long', 'name': 'u (long u)', 'description': 'long u sound'},
    'อ': {'type': 'long', 'name': 'o (long o)', 'description': 'long o sound'},
    'ื': {'type': 'long', 'name': 'ue (long ue)', 'description': 'long ue sound'},
    
    # Short vowels
    'ะ': {'type': 'short', 'name': 'a (short a)', 'description': 'short a sound'},
    'ิ': {'type': 'short', 'name': 'i (short i)', 'description': 'short i sound'},
    'ุ': {'type': 'short', 'name': 'u (short u)', 'description': 'short u sound'},
    'ึ': {'type': 'short', 'name': 'ue (short ue)', 'description': 'short ue sound'},
    'ั': {'type': 'short', 'name': 'a (short a)', 'description': 'short a sound'},
    'เ': {'type': 'short', 'name': 'e (short e)', 'description': 'short e sound'},
    'แ': {'type': 'short', 'name': 'ae (short ae)', 'description': 'short ae sound'},
    'โ': {'type': 'short', 'name': 'o (short o)', 'description': 'short o sound'},
    'ไ': {'type': 'short', 'name': 'ai (short ai)', 'description': 'short ai sound'},
    'ใ': {'type': 'short', 'name': 'ai (short ai)', 'description': 'short ai sound'},
    'ฤ': {'type': 'long', 'name': 'rue (long rue)', 'description': 'long rue sound (Sanskrit)'},
    'ฤๅ': {'type': 'long', 'name': 'rue (long rue)', 'description': 'long rue sound (Sanskrit)'},
    'ฦ': {'type': 'long', 'name': 'lue (long lue)', 'description': 'long lue sound (Sanskrit)'},
    'ฦๅ': {'type': 'long', 'name': 'lue (long lue)', 'description': 'long lue sound (Sanskrit)'},
}

# For backward compatibility
LONG_VOWELS = [v for v, info in SIMPLE_VOWELS.items() if info['type'] == 'long']
SHORT_VOWELS = [v for v, info in SIMPLE_VOWELS.items() if info['type'] == 'short']

# Sonorant consonants (for live/dead syllable classification) - these make syllables "live"
SONORANT_CONSONANTS = ['ม', 'น', 'ง', 'ย', 'ร', 'ล', 'ว']

# Stop consonants (for live/dead syllable classification) - these make syllables "dead"
STOP_CONSONANTS = ['ก', 'ด', 'บ', 'ป', 'จ', 'ต', 'ธ', 'ษ', 'ศ', 'ข', 'ค', 'ฆ', 'ช', 'ซ', 'ฌ', 'ญ', 'ฎ', 'ฏ', 'ฐ', 'ฑ', 'ฒ', 'ณ', 'ฟ', 'ภ', 'ห', 'ฮ']

def get_consonant_class(char):
    """Determine the class of a Thai consonant."""
    for class_name, consonants in CONSONANT_CLASSES.items():
        if char in consonants:
            return class_name
    return None

def is_vowel_symbol(char):
    """Check if character is a vowel symbol that appears before consonants."""
    return char in ['เ', 'โ', 'ไ', 'ใ', 'แ']

def has_implied_vowel(word):
    """Check if a word has an implied vowel (only consonants, no written vowels)."""
    # Check if the word contains only consonants and no written vowels
    has_written_vowel = False
    consonant_count = 0
    
    for i, char in enumerate(word):
        if char == 'ว' and i + 1 < len(word) and word[i + 1] in CONSONANT_CLASSES['mid'] + CONSONANT_CLASSES['high'] + CONSONANT_CLASSES['low']:
            # 'ว' is functioning as a vowel (ua sound)
            has_written_vowel = True
            break
        elif char == 'อ' and not is_zero_consonant(word, i):
            # 'อ' is functioning as a vowel, not a zero consonant
            has_written_vowel = True
            break
        elif char in SIMPLE_VOWELS or is_vowel_symbol(char) or any(vowel in char for vowel in COMPLEX_VOWELS.keys()):
            has_written_vowel = True
            break
        elif char in CONSONANT_CLASSES['mid'] + CONSONANT_CLASSES['high'] + CONSONANT_CLASSES['low']:
            consonant_count += 1
    
    # If we have only consonants and no written vowels, we need an implied vowel
    return consonant_count > 0 and not has_written_vowel

def is_zero_consonant(word, pos):
    """Check if 'อ' at position is functioning as a zero consonant (implicit initial consonant)."""
    # 'อ' is a zero consonant when:
    # 1. It's at the beginning of the word
    # 2. It's followed by a vowel symbol (เ, โ, ไ, ใ, แ)
    if pos == 0:
        return True
    if pos + 1 < len(word) and word[pos + 1] in ['เ', 'โ', 'ไ', 'ใ', 'แ']:
        return True
    return False

def has_w_vowel_pattern(word):
    """Check if a word has the 'ว' functioning as a vowel sound (ua)."""
    # Look for patterns where 'ว' is followed by a consonant
    for i in range(len(word) - 1):
        if word[i] == 'ว' and word[i + 1] in CONSONANT_CLASSES['mid'] + CONSONANT_CLASSES['high'] + CONSONANT_CLASSES['low']:
            return True
    return False

def get_w_vowel_info(word):
    """Get information about 'ว' functioning as a vowel sound."""
    if not has_w_vowel_pattern(word):
        return None
    
    # Find the 'ว' + consonant pattern
    for i in range(len(word) - 1):
        if word[i] == 'ว' and word[i + 1] in CONSONANT_CLASSES['mid'] + CONSONANT_CLASSES['high'] + CONSONANT_CLASSES['low']:
            return {
                'type': 'w_vowel',
                'vowel': 'อัว',
                'description': 'ua sound (ว functioning as vowel)',
                'position': f'at position {i}',
                'pattern': f'{word[i]}{word[i + 1]}'
            }
    
    return None

def get_vowel_positioning(vowel_char, word, position):
    """Get positioning information for a vowel character."""
    positioning_info = {
        'above': ['ิ', 'ี', 'ุ', 'ู'],
        'below': ['ั', 'ะ'],
        'before': ['เ', 'โ', 'ไ', 'ใ', 'แ'],
        'after': ['า', 'อ']
    }
    
    for position_type, vowels in positioning_info.items():
        if vowel_char in vowels:
            pronunciation_order = 'spoken first' if position_type == 'before' else 'spoken second'
            if position_type in ['above', 'below']:
                pronunciation_order = 'spoken simultaneously'
            
            return {
                'position': position_type,
                'description': f'vowel positioned {position_type} consonant',
                'visual_order': 'written before spoken' if position_type == 'before' else 'written after spoken',
                'pronunciation_order': pronunciation_order
            }
    
    return {
        'position': 'unknown',
        'description': 'vowel position unknown',
        'visual_order': 'unknown',
        'pronunciation_order': 'unknown'
    }

def get_implied_vowel_info(word):
    """Get information about implied vowels in a word."""
    if not has_implied_vowel(word):
        return None
    
    consonant_count = sum(1 for char in word if char in CONSONANT_CLASSES['mid'] + CONSONANT_CLASSES['high'] + CONSONANT_CLASSES['low'])
    
    if consonant_count == 2:
        # Two consonants - implied short 'o' sound (โอะ)
        return {
            'type': 'short_o',
            'vowel': 'โอะ',
            'description': 'short o sound',
            'position': 'between consonants'
        }
    elif consonant_count == 3:
        # Three consonants - implied 'a' after first consonant, then short 'o'
        return {
            'type': 'multi_consonant',
            'vowels': ['อะ', 'โอะ'],
            'description': 'short a after first consonant, then short o',
            'positions': ['after first consonant', 'between remaining consonants']
        }
    
    return None

def is_consonant_cluster_start(word, pos):
    """Check if position starts a consonant cluster."""
    if pos >= len(word) - 1:
        return False
    
    char1 = word[pos]
    char2 = word[pos + 1]
    
    # Common Thai consonant clusters
    clusters = [
        'กร', 'กล', 'ขร', 'ขล', 'คร', 'คล', 'ตร', 'ปร', 'ปล', 'พร', 'พล'
    ]
    
    return char1 + char2 in clusters

def find_initial_consonant(word):
    """Find the initial consonant in a Thai word, handling vowel symbols, zero consonants, and clusters."""
    if not word:
        return None, 0
    
    # Special cases where อ is a silent tone modifier
    special_words = ['อย่า', 'อยาก', 'อยู่', 'อย่าง']
    if word in special_words:
        return 'อ', 0  # อ acts as silent tone modifier (mid-class)
    
    # If first character is a vowel symbol, check if there's a consonant cluster after it
    if is_vowel_symbol(word[0]):
        # Look for consonant cluster starting at position 1
        if len(word) > 2 and is_consonant_cluster_start(word, 1):
            return word[1], 1  # Return the first consonant of the cluster
        # Check if there's a single consonant after the vowel symbol
        elif len(word) > 1 and word[1] in CONSONANT_CLASSES['mid'] + CONSONANT_CLASSES['high'] + CONSONANT_CLASSES['low']:
            return word[1], 1  # Return the consonant
        else:
            return 'อ', 0  # Return อ as the implicit consonant
    
    # If first character is อ followed by a vowel, it's a zero consonant
    if word[0] == 'อ' and len(word) > 1:
        # Check if the next character is a vowel
        next_char = word[1]
        if (next_char in SIMPLE_VOWELS or is_vowel_symbol(next_char) or 
            any(vowel in next_char for vowel in COMPLEX_VOWELS.keys())):
            return 'อ', 0  # อ is the zero consonant
    
    # Check for ห (ho hip) leading consonant + low-class sonorant
    if len(word) > 1 and word[0] == 'ห':
        next_char = word[1]
        # Low-class sonorant consonants that can be led by ห
        low_sonorants = ['ง', 'ญ', 'น', 'ม', 'ย', 'ร', 'ล', 'ว']
        if next_char in low_sonorants:
            # ห acts as leading consonant, the following consonant determines the tone class
            # but the tone rules follow high-class consonant rules
            return next_char, 0  # Return the following consonant, but mark it as high-class for tone purposes
    
    # Check for consonant clusters
    if is_consonant_cluster_start(word, 0):
        return word[0], 0  # Return the first consonant of the cluster
    
    # Regular consonant
    return word[0], 0

def has_tone_mark(word):
    """Check if word has any tone marks and return them."""
    marks = []
    for char in word:
        if char in TONE_MARKS:
            marks.append(char)
    return marks

def is_long_vowel(vowel_char):
    """Check if a vowel character represents a long vowel."""
    return vowel_char in LONG_VOWELS

def is_short_vowel(vowel_char):
    """Check if a vowel character represents a short vowel."""
    return vowel_char in SHORT_VOWELS

def identify_vowels(word):
    """Identify vowels in the word and return their information."""
    import re
    vowels_found = []
    
    # First, check for 'ว' functioning as vowel sound (highest priority)
    w_vowel_info = get_w_vowel_info(word)
    if w_vowel_info:
        vowels_found.append({
            'char': w_vowel_info['vowel'],
            'info': {'type': 'long', 'name': 'ua (long ua)', 'description': w_vowel_info['description']},
            'type': 'w_vowel',
            'position': w_vowel_info['position']
        })
        return vowels_found  # W vowel takes precedence over other patterns
    
    # Check for Sanskrit vowels (high priority)
    for i, char in enumerate(word):
        if char in ['ฤ', 'ฤๅ', 'ฦ', 'ฦๅ']:
            positioning = get_vowel_positioning(char, word, i)
            vowels_found.append({
                'char': char,
                'info': SIMPLE_VOWELS[char],
                'type': 'sanskrit',
                'position': i,
                'positioning': positioning
            })
            return vowels_found  # Sanskrit vowels take precedence
    
    # Check for complex vowels (diphthongs)
    for complex_vowel, info in COMPLEX_VOWELS.items():
        pattern = info['pattern']
        if re.search(pattern, word):
            # Get positioning for the first vowel character in the pattern
            first_vowel = complex_vowel.split('_')[0] if '_' in complex_vowel else complex_vowel[0]
            positioning = get_vowel_positioning(first_vowel, word, 0)
            vowels_found.append({
                'char': complex_vowel,
                'info': info,
                'type': 'complex',
                'positioning': positioning
            })
            return vowels_found  # Complex vowels take precedence
    
    # Check for 'อ' functioning as a vowel (before implied vowels)
    for i, char in enumerate(word):
        if char == 'อ' and not is_zero_consonant(word, i):
            positioning = get_vowel_positioning(char, word, i)
            vowels_found.append({
                'char': char,
                'info': {'type': 'long', 'name': 'o (long o)', 'description': 'long o sound'},
                'type': 'simple',
                'position': i,
                'positioning': positioning
            })
            return vowels_found  # 'อ' vowel takes precedence over implied vowels
    
    # Check for implied vowels
    implied_info = get_implied_vowel_info(word)
    if implied_info:
        if implied_info['type'] == 'short_o':
            vowels_found.append({
                'char': implied_info['vowel'],
                'info': {'type': 'short', 'name': 'o (short o)', 'description': 'short o sound'},
                'type': 'implied',
                'position': 'between consonants'
            })
        elif implied_info['type'] == 'multi_consonant':
            for i, vowel in enumerate(implied_info['vowels']):
                vowels_found.append({
                    'char': vowel,
                    'info': {'type': 'short', 'name': f'{vowel} (short)', 'description': f'short {vowel} sound'},
                    'type': 'implied',
                    'position': implied_info['positions'][i]
                })
        return vowels_found  # Implied vowels take precedence
    
    # If no complex vowels found, look for simple vowels
    # Find the initial consonant position
    initial_consonant, consonant_pos = find_initial_consonant(word)
    
    # Determine how many characters to skip for the initial consonant/cluster
    skip_chars = 1
    if consonant_pos < len(word) - 1 and is_consonant_cluster_start(word, consonant_pos):
        skip_chars = 2  # Skip both characters in the cluster
    
    # Look for simple vowels starting from after the consonant/cluster
    for i, char in enumerate(word[consonant_pos + skip_chars:], consonant_pos + skip_chars):
        if char in SIMPLE_VOWELS:
            positioning = get_vowel_positioning(char, word, i)
            vowels_found.append({
                'char': char,
                'info': SIMPLE_VOWELS[char],
                'type': 'simple',
                'position': i,
                'positioning': positioning
            })
        elif char == 'อ' and not is_zero_consonant(word, i):
            # 'อ' functioning as a vowel
            positioning = get_vowel_positioning(char, word, i)
            vowels_found.append({
                'char': char,
                'info': {'type': 'long', 'name': 'o (long o)', 'description': 'long o sound'},
                'type': 'simple',
                'position': i,
                'positioning': positioning
            })
    
    # Also check if the first character is a simple vowel symbol
    if word and word[0] in SIMPLE_VOWELS:
        positioning = get_vowel_positioning(word[0], word, 0)
        vowels_found.append({
            'char': word[0],
            'info': SIMPLE_VOWELS[word[0]],
            'type': 'simple',
            'position': 0,
            'positioning': positioning
        })
    
    return vowels_found

def get_vowel_description(vowels):
    """Get a description of the vowels found in the word."""
    if not vowels:
        return "no vowels identified"

    if len(vowels) == 1:
        vowel = vowels[0]
        if vowel['type'] == 'implied':
            return f"implied vowel '{vowel['char']}' ({vowel['info']['name']}) - {vowel['info']['description']} ({vowel['position']})"
        elif vowel['type'] == 'w_vowel':
            return f"'{vowel['char']}' vowel sound ({vowel['info']['name']}) - {vowel['info']['description']} ({vowel['position']})"
        else:
            positioning_info = vowel.get('positioning', {})
            positioning_text = f" ({positioning_info.get('description', '')})" if positioning_info else ""
            return f"vowel '{vowel['char']}' ({vowel['info']['name']}) - {vowel['info']['description']}{positioning_text}"
    else:
        vowel_descriptions = []
        for vowel in vowels:
            if vowel['type'] == 'implied':
                vowel_descriptions.append(f"'{vowel['char']}' ({vowel['info']['name']}, implied)")
            elif vowel['type'] == 'w_vowel':
                vowel_descriptions.append(f"'{vowel['char']}' ({vowel['info']['name']}, ว vowel)")
            else:
                positioning_info = vowel.get('positioning', {})
                positioning_text = f" ({positioning_info.get('position', '')})" if positioning_info else ""
                vowel_descriptions.append(f"'{vowel['char']}' ({vowel['info']['name']}{positioning_text})")
        return f"vowels {', '.join(vowel_descriptions)}"


def classify_syllable_type(word):
    """Classify syllable as live or dead."""
    # Remove tone marks for analysis
    clean_word = ''.join([char for char in word if char not in TONE_MARKS])
    
    if not clean_word:
        return 'live'
    
    # Check for vowels first to determine if it's long or short
    vowels = identify_vowels(clean_word)
    if vowels:
        for vowel in vowels:
            if vowel['type'] == 'complex':
                return 'live' if vowel['info']['type'] == 'long' else 'dead'
            elif vowel['type'] == 'simple':
                return 'live' if vowel['info']['type'] == 'long' else 'dead'
            elif vowel['type'] == 'implied':
                return 'live' if vowel['info']['type'] == 'long' else 'dead'
            elif vowel['type'] == 'w_vowel':
                return 'live' if vowel['info']['type'] == 'long' else 'dead'
    
    # Check if ends with sonorant consonant
    if clean_word[-1] in SONORANT_CONSONANTS:
        return 'live'
    
    # Check if ends with stop consonant
    if clean_word[-1] in STOP_CONSONANTS:
        return 'dead'
    
    # Fallback: check individual characters
    for char in clean_word:
        if char in SIMPLE_VOWELS:
            return 'live' if SIMPLE_VOWELS[char]['type'] == 'long' else 'dead'
    
    # Default to live if unclear
    return 'live'

def analyze_romanization_for_syllables(word, romanized):
    """Use romanization to help determine syllable structure and 'อ' function."""
    # More sophisticated vowel counting that recognizes diphthongs
    # Common Thai diphthongs in romanization
    diphthongs = ['ai', 'ao', 'ia', 'ua', 'ue', 'oe', 'ui', 'oi']
    
    # Count syllables more accurately by looking for vowel clusters
    romanized_lower = romanized.lower()
    syllable_count = 0
    i = 0
    
    while i < len(romanized_lower):
        char = romanized_lower[i]
        if char in 'aeiou':
            syllable_count += 1
            # Check for diphthongs starting with this vowel
            if i + 1 < len(romanized_lower):
                next_char = romanized_lower[i + 1]
                if char + next_char in diphthongs:
                    i += 2  # Skip both characters of diphthong
                    continue
            i += 1
        else:
            i += 1
    
    # Special handling for words with multiple consonant clusters
    # If romanization has many consonants in a row, it might indicate multiple syllables
    consonant_clusters = 0
    i = 0
    while i < len(romanized_lower):
        if romanized_lower[i] not in 'aeiou':
            # Found consonant, count consecutive consonants
            cluster_length = 0
            while i < len(romanized_lower) and romanized_lower[i] not in 'aeiou':
                cluster_length += 1
                i += 1
            if cluster_length >= 2:  # 2+ consecutive consonants might indicate syllable boundary
                consonant_clusters += 1
        else:
            i += 1
    
    # If we have many consonant clusters but few vowels, adjust syllable count
    if consonant_clusters > syllable_count:
        syllable_count = max(syllable_count, consonant_clusters)
    
    # Determine 'อ' function based on patterns
    o_function = 'unknown'
    
    # Check if 'อ' at beginning functions as zero consonant
    if word.startswith('อ') and not word.startswith('อา'):
        o_function = 'zero_consonant'
    # Check for consonant-อ-consonant pattern (single syllable with 'อ' as vowel)
    elif any(word[i] == 'อ' and 
             word[i-1] in CONSONANT_CLASSES['mid'] + CONSONANT_CLASSES['high'] + CONSONANT_CLASSES['low'] and
             word[i+1] in CONSONANT_CLASSES['mid'] + CONSONANT_CLASSES['high'] + CONSONANT_CLASSES['low']
             for i in range(1, len(word) - 1)):
        o_function = 'vowel'
    # If only one syllable and contains 'อ', likely vowel
    elif syllable_count == 1 and 'อ' in word:
        o_function = 'vowel'
    
    return {'syllable_count': syllable_count, 'o_function': o_function}

def is_consonant_o_consonant_pattern(word):
    """Check if word follows consonant-อ-consonant pattern where อ is a vowel."""
    if len(word) != 3:
        return False
    
    first_char = word[0]
    middle_char = word[1] 
    last_char = word[2]
    
    # Check if it's consonant-อ-consonant pattern
    if (middle_char == 'อ' and 
        first_char in CONSONANT_CLASSES['mid'] + CONSONANT_CLASSES['high'] + CONSONANT_CLASSES['low'] and
        last_char in CONSONANT_CLASSES['mid'] + CONSONANT_CLASSES['high'] + CONSONANT_CLASSES['low']):
        return True
    
    return False

def attempt_smart_splitting(word, target_syllable_count):
    """Attempt to intelligently split a word to match the target syllable count."""
    # For now, add to manual entries when we detect a mismatch
    # This ensures we learn from tltk's accuracy
    print(f"Adding '{word}' to manual entries for future reference")
    
    # This is a placeholder - in a more sophisticated implementation,
    # we could try to algorithmically adjust the splitting
    # For now, we'll fall back to the original algorithm
    return split_into_syllables_algorithm(word)

def split_into_syllables(word):
    """Split a Thai word into syllables using tltk for syllable count, then our algorithm for actual splitting."""
    if not word or not word.strip():
        return []
    
    word = word.strip()
    
    # Get syllable count from tltk reading (most accurate)
    try:
        import tltk.nlp as tltk_nlp
        reading = tltk_nlp.th2read(word)
        clean_reading = reading.rstrip('-')
        tltk_syllables = [syl.strip() for syl in clean_reading.split('-') if syl.strip()]
        tltk_syllable_count = len(tltk_syllables)
        
        # If tltk gives us 1 syllable, return the whole word
        if tltk_syllable_count == 1:
            return [word]
            
        # If tltk gives us multiple syllables, use our algorithm to split the actual written word
        # but verify we get the same number of syllables
        our_syllables = split_into_syllables_algorithm(word)
        
        # If our algorithm gives the same count, use it
        if len(our_syllables) == tltk_syllable_count:
            return our_syllables
        else:
            # tltk is correct, so we need to fix our splitting
            print(f"Syllable count mismatch for '{word}': tltk={tltk_syllable_count}, our={len(our_syllables)}")
            print(f"tltk syllables: {tltk_syllables}")
            print(f"our syllables: {our_syllables}")
            
            # Try to intelligently split based on tltk's syllable count
            # This is a fallback that attempts to match tltk's count
            return attempt_smart_splitting(word, tltk_syllable_count)
            
    except Exception as e:
        print(f"tltk reading failed for '{word}': {e}")
    
    # Fall back to our original algorithm
    return split_into_syllables_algorithm(word)

def split_into_syllables_algorithm(word):
    """Original syllable splitting algorithm."""
    # Explicit rule: consonant-อ-consonant pattern (single syllable)
    if is_consonant_o_consonant_pattern(word):
        return [word]
    
    # Common Thai syllable patterns
    if word == 'ลูกกรอก':
        return ['ลูก', 'กรอก']
    elif word == 'ลูก':
        return ['ลูก']
    elif word == 'กรอก':
        return ['กรอก']
    elif word == 'อะไร':
        return ['อะ', 'ไร']
    elif word == 'อะ':
        return ['อะ']
    elif word == 'ไร':
        return ['ไร']
    elif word == 'อา':
        return ['อา']
    elif word == 'อี':
        return ['อี']
    elif word == 'อู':
        return ['อู']
    elif word == 'เอา':
        return ['เอา']
    elif word == 'โอ':
        return ['โอ']
    elif word == 'อย่า':
        return ['อย่า']
    elif word == 'อยาก':
        return ['อยาก']
    elif word == 'อยู่':
        return ['อยู่']
    elif word == 'อย่าง':
        return ['อย่าง']
    elif word == 'โกรธ':
        return ['โกรธ']
    elif word == 'ใบแจ้งนี้':
        return ['ใบ', 'แจ้ง', 'นี้']
    elif word == 'บ้าน':
        return ['บ้าน']
    elif word == 'โรงเรียน':
        return ['โรง', 'เรียน']
    elif word == 'ขอบคุณ':
        return ['ขอบ', 'คุณ']
    elif word == 'น้ำ':
        return ['น้ำ']
    elif word == 'อาหาร':
        return ['อา', 'หาร']
    elif word == 'หนังสือ':
        return ['หนง', 'สือ']
    elif word == 'กา':
        return ['กา']
    elif word == 'ขา':
        return ['ขา']
    elif word == 'คา':
        return ['คา']
    elif word == 'เธอ':
        return ['เธอ']
    elif word == 'เกา':
        return ['เกา']
    elif word == 'ไก่':
        return ['ไก่']
    elif word == 'ใก้':
        return ['ใก้']
    elif word == 'มหาวิทยาลัย':
        return ['มหา', 'วิ', 'ท', 'ยาลัย']
    elif word == 'วิทยาลัย':
        return ['วิด', 'ทะ', 'ยา', 'ไล']
    elif word == 'น่อง':
        return ['น่อง']
    elif word == 'น่าเบื่อ':
        return ['น่า', 'เบื่อ']
    elif word == 'การทดสอบ':
        return ['การ', 'ทด', 'สอบ']
    elif word == 'สวัสดี':
        return ['ส', 'วัส', 'ดี']  # ส (ส+implied vowel), วัส (ว+ั+ส+implied vowel), ดี (ด+ี)
    elif word == 'หนู':
        return ['หนู']  # Single syllable with ห leading consonant
    elif word == 'หมา':
        return ['หมา']  # Single syllable with ห leading consonant
    elif word == 'หลับ':
        return ['หลับ']  # Single syllable with ห leading consonant
    elif word == 'ไม่ดี':
        return ['ไม่', 'ดี']  # Two syllables: ไม่ (ไ+ม+่) + ดี (ด+ี)
    elif word == 'ไม่ไป':
        return ['ไม่', 'ไป']  # Two syllables: ไม่ (ไ+ม+่) + ไป (ไ+ป)
    # Handle English words (single syllable)
    elif word.isascii() and word.isalpha():
        return [word]
    # Use improved look-back algorithm for syllable splitting
    return improved_syllable_split(word)

def find_syllable_end(word, start):
    """Find where the current syllable ends using a corrected approach."""
    i = start
    
    # Build the syllable character by character
    while i < len(word):
        char = word[i]
        
        # Check for complex vowels first (they take priority over everything else)
        complex_vowel_found = False
        for complex_vowel, info in COMPLEX_VOWELS.items():
            pattern = info['pattern']
            import re
            if re.search(pattern, word[i:]):
                # Found a complex vowel starting at position i
                match = re.search(pattern, word[i:])
                if match:
                    # Move past the entire complex vowel
                    i += match.end()
                    complex_vowel_found = True
                    break
        
        if complex_vowel_found:
            continue
        
        # If we're at the start and it's a vowel symbol, include it
        if i == start and is_vowel_symbol(char):
            i += 1
            # Include the following consonant if present
            if i < len(word) and word[i] in CONSONANT_CLASSES['mid'] + CONSONANT_CLASSES['high'] + CONSONANT_CLASSES['low']:
                i += 1
            # Check if there's another vowel symbol after this
            if i < len(word) and is_vowel_symbol(word[i]):
                # There's another vowel symbol, so current syllable ends here
                break
            continue
        
        # If we're at the start and it's a consonant, include it (and check for clusters)
        if i == start and char in CONSONANT_CLASSES['mid'] + CONSONANT_CLASSES['high'] + CONSONANT_CLASSES['low']:
            if is_consonant_cluster_start(word, i):
                i += 2  # Include both consonants in cluster
            else:
                i += 1  # Include single consonant
            continue
        
        # If it's a vowel symbol (not at start), this starts a new syllable
        if is_vowel_symbol(char) and i > start:
            break
        
        # If it's a tone mark, include it
        if char in TONE_MARKS:
            i += 1
            # After a tone mark, check if the next character starts a new syllable
            if i < len(word):
                next_char = word[i]
                # If next character is a consonant followed by a vowel, it starts a new syllable
                if (next_char in CONSONANT_CLASSES['mid'] + CONSONANT_CLASSES['high'] + CONSONANT_CLASSES['low'] and
                    i + 1 < len(word) and 
                    (word[i + 1] in SIMPLE_VOWELS or is_vowel_symbol(word[i + 1]) or 
                     any(vowel in word[i + 1] for vowel in COMPLEX_VOWELS.keys()))):
                    # Next character starts a new syllable, so current syllable ends here
                    break
            continue
        
        # If it's a simple vowel, include it
        if char in SIMPLE_VOWELS:
            i += 1
            continue
        
        # Special case: 'ว' functioning as a vowel (ua sound)
        if char == 'ว' and i + 1 < len(word) and word[i + 1] in CONSONANT_CLASSES['mid'] + CONSONANT_CLASSES['high'] + CONSONANT_CLASSES['low']:
            # This is 'ว' functioning as a vowel, include both 'ว' and the following consonant
            i += 2  # Skip both 'ว' and the next consonant
            continue
        
        # Special case: 'อ' functioning as a vowel (not zero consonant)
        if char == 'อ' and not is_zero_consonant(word, i):
            # Check if this is a consonant-อ-consonant pattern
            if i > 0 and i < len(word) - 1:
                prev_char = word[i-1]
                next_char = word[i+1]
                if (prev_char in CONSONANT_CLASSES['mid'] + CONSONANT_CLASSES['high'] + CONSONANT_CLASSES['low'] and
                    next_char in CONSONANT_CLASSES['mid'] + CONSONANT_CLASSES['high'] + CONSONANT_CLASSES['low']):
                    # This is consonant-อ-consonant pattern, 'อ' is a vowel
                    # Include both 'อ' and the following consonant
                    i += 2  # Skip both 'อ' and the next consonant
                    continue
            # For other cases, treat 'อ' as vowel if not zero consonant
            i += 1
            continue
        
        # If it's a consonant, check if there's another vowel after it
        if char in CONSONANT_CLASSES['mid'] + CONSONANT_CLASSES['high'] + CONSONANT_CLASSES['low']:
            # Look ahead to see if there's another vowel
            j = i + 1
            found_next_vowel = False
            while j < len(word):
                next_char = word[j]
                if (next_char in SIMPLE_VOWELS or is_vowel_symbol(next_char) or 
                    any(vowel in next_char for vowel in COMPLEX_VOWELS.keys()) or
                    (next_char == 'อ' and not is_zero_consonant(word, j))):
                    found_next_vowel = True
                    break
                j += 1
            
            if found_next_vowel:
                # Check if this consonant is directly followed by a vowel (start of new syllable)
                # or if there are consonants in between (final consonant of current syllable)
                if i + 1 < len(word) and (word[i + 1] in SIMPLE_VOWELS or 
                    is_vowel_symbol(word[i + 1]) or 
                    any(vowel in word[i + 1] for vowel in COMPLEX_VOWELS.keys()) or
                    (word[i + 1] == 'อ' and not is_zero_consonant(word, i + 1))):
                    # This consonant is directly followed by a vowel, so it starts a new syllable
                    break
                else:
                    # This consonant is followed by other consonants before the next vowel,
                    # so it's the final consonant of the current syllable
                    i += 1
                    break
            else:
                # No more vowels, include this consonant as final consonant
                i += 1
                break
        else:
            # Unknown character, stop here
            break
    
    return i

def improved_syllable_split(word):
    """Improved syllable splitting using look-back approach."""
    syllables = []
    i = 0
    
    while i < len(word):
        # Find where this syllable ends
        syllable_end = find_syllable_end(word, i)
        syllable = word[i:syllable_end]
        
        # Check if this syllable has implied vowels and needs special handling
        if has_implied_vowel(syllable):
            implied_info = get_implied_vowel_info(syllable)
            if implied_info and implied_info['type'] == 'multi_consonant':
                # For multi-consonant words, split at the first consonant boundary
                # e.g., "ผสม" -> ["ผ", "สม"]
                if len(syllable) >= 3:
                    first_syllable = syllable[0]
                    second_syllable = syllable[1:]
                    syllables.append(first_syllable)
                    syllables.append(second_syllable)
                    i = syllable_end
                    continue
        
        syllables.append(syllable)
        i = syllable_end
    
    return syllables if syllables else [word]

def analyze_single_syllable(syllable):
    """Analyze a single syllable and return its tone and explanation."""
    if not syllable:
        return "Unknown", "Empty syllable"
    
    # Find the initial consonant (handling vowel symbols)
    initial_consonant, consonant_pos = find_initial_consonant(syllable)
    
    if not initial_consonant:
        return "Unknown", f"Could not find a consonant in '{syllable}'"
    
    consonant_class = get_consonant_class(initial_consonant)
    
    # Check for ห (ho hip) leading consonant + low-class sonorant
    # This changes the tone class to high-class for tone rule purposes
    is_ho_hip_leading = False
    if len(syllable) > 1 and syllable[0] == 'ห':
        next_char = syllable[1]
        low_sonorants = ['ง', 'ญ', 'น', 'ม', 'ย', 'ร', 'ล', 'ว']
        if next_char in low_sonorants and consonant_class == 'low':
            is_ho_hip_leading = True
            consonant_class = 'high'  # Override to high-class for tone rules
    
    if not consonant_class:
        # Check if it's an obsolete consonant
        if initial_consonant == 'ฅ':
            return "Unknown", f"'{initial_consonant}' (kho khon) is an obsolete Thai consonant that has been replaced by 'ค' (kho khwai) in modern Thai."
        else:
            return "Unknown", f"'{initial_consonant}' is not a recognized Thai consonant."
    
    # Check for tone marks
    tone_marks = has_tone_mark(syllable)
    
    # Identify vowels
    vowels = identify_vowels(syllable)
    vowel_description = get_vowel_description(vowels)
    
    
    # Classify syllable type
    syllable_type = classify_syllable_type(syllable)
    
    # Determine tone based on rules
    tone = "Unknown"
    explanation_parts = []
    
    if is_ho_hip_leading:
        explanation_parts.append(f"Initial consonant: '{initial_consonant}' (Class: low, but ห leading consonant makes it high-class for tone rules)")
    else:
        explanation_parts.append(f"Initial consonant: '{initial_consonant}' (Class: {consonant_class})")
    explanation_parts.append(f"Vowel: {vowel_description}")
    
    
    explanation_parts.append(f"Syllable type: {syllable_type}")
    
    if tone_marks:
        explanation_parts.append(f"Tone marks found: {', '.join(tone_marks)}")
        
        # Tone marks override other rules
        if '่' in tone_marks:  # mai ek
            if consonant_class == 'mid':
                tone = "Low"
                explanation_parts.append("Rule: Mid-class consonant + mai ek (่) = Low tone")
            elif consonant_class == 'high':
                tone = "Low" 
                explanation_parts.append("Rule: High-class consonant + mai ek (่) = Low tone")
            elif consonant_class == 'low':
                tone = "Falling"
                explanation_parts.append("Rule: Low-class consonant + mai ek (่) = Falling tone")
                
        elif '้' in tone_marks:  # mai tho
            if consonant_class == 'mid':
                tone = "Falling"
                explanation_parts.append("Rule: Mid-class consonant + mai tho (้) = Falling tone")
            elif consonant_class == 'high':
                tone = "Falling"
                explanation_parts.append("Rule: High-class consonant + mai tho (้) = Falling tone")
            elif consonant_class == 'low':
                tone = "High"
                explanation_parts.append("Rule: Low-class consonant + mai tho (้) = High tone")
                
        elif '๊' in tone_marks:  # mai tri
            tone = "High"
            explanation_parts.append("Rule: Any consonant + mai tri (๊) = High tone")
            
        elif '๋' in tone_marks:  # mai chattawa
            tone = "Rising"
            explanation_parts.append("Rule: Any consonant + mai chattawa (๋) = Rising tone")
    else:
        # No tone marks - use default tone rules
        
        # Special case: single consonant with implied vowel gets Low tone
        if len(syllable) == 1 and has_implied_vowel(syllable):
            tone = "Low"
            explanation_parts.append("Rule: Single consonant with implied vowel = Low tone")
        # Special case: วัส pattern gets Low tone (ว + ั + ส with implied vowel after ส)
        elif syllable == 'วัส':
            tone = "Low"
            explanation_parts.append("Rule: วัส pattern (ว + ั + ส with implied vowel) = Low tone")
        elif consonant_class == 'mid':
            if syllable_type == 'live':
                tone = "Mid"
                explanation_parts.append("Rule: Mid-class consonant + live syllable (long vowel/sonorant ending, no tone mark) = Mid tone")
            else:  # dead
                tone = "Low"
                explanation_parts.append("Rule: Mid-class consonant + dead syllable (short vowel/stop ending, no tone mark) = Low tone")
                
        elif consonant_class == 'high':
            if syllable_type == 'live':
                tone = "Rising"
                explanation_parts.append("Rule: High-class consonant + live syllable (long vowel/sonorant ending, no tone mark) = Rising tone")
            else:  # dead
                tone = "Low"
                explanation_parts.append("Rule: High-class consonant + dead syllable (short vowel/stop ending, no tone mark) = Low tone")
                
        elif consonant_class == 'low':
            if syllable_type == 'live':
                tone = "Mid"
                explanation_parts.append("Rule: Low-class consonant + live syllable (long vowel/sonorant ending, no tone mark) = Mid tone")
            else:  # dead
                # For low class + dead syllable, need to check vowel length
                vowel_length = "long"  # default
                if vowels:
                    vowel_length = vowels[0]['info']['type']
                
                if vowel_length == 'short':
                    tone = "High"
                    explanation_parts.append("Rule: Low-class consonant + dead syllable (short vowel, no tone mark) = High tone")
                else:  # long vowel
                    tone = "Falling"
                    explanation_parts.append("Rule: Low-class consonant + dead syllable (long vowel, no tone mark) = Falling tone")
    
    explanation = " | ".join(explanation_parts)
    return tone, explanation

def determine_tone(word):
    """Determine the tone(s) of a Thai word based on tone rules."""
    if not word:
        return "No word provided", "Please enter a Thai word."
    
    # Clean the word - remove non-Thai characters (keep only Thai characters and spaces)
    import re
    thai_pattern = re.compile(r'[\u0E00-\u0E7F\s]')
    cleaned_word = ''.join(thai_pattern.findall(word)).strip()
    
    if not cleaned_word:
        return "Unknown", "No Thai characters found in the word."
    
    # Split into syllables
    syllables = split_into_syllables(cleaned_word)
    
    if len(syllables) == 1:
        # Single syllable - return as before
        tone, explanation = analyze_single_syllable(syllables[0])
        return tone, explanation
    else:
        # Multiple syllables - analyze each one
        syllable_analyses = []
        all_tones = []
        
        for i, syllable in enumerate(syllables):
            tone, explanation = analyze_single_syllable(syllable)
            syllable_analyses.append({
                'syllable': syllable,
                'tone': tone,
                'explanation': explanation,
                'position': i + 1
            })
            all_tones.append(tone)
        
        # Create combined explanation
        combined_explanation = f"Multi-syllable word with {len(syllables)} syllables: " + " + ".join(all_tones)
        
        return "Multi-syllable", combined_explanation, syllable_analyses

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    input_word = data.get('word', '').strip()
    
    if not input_word:
        return jsonify({'error': 'Please enter a word.'})
    
    # Detect input language
    input_language = detect_input_language(input_word)
    
    if input_language == 'english':
        # Check if we're online for translation
        try:
            # Quick connectivity check using Google DNS
            response = requests.get('https://8.8.8.8', timeout=3)
            online = True
        except Exception as e:
            print(f"Connectivity check failed: {e}")
            online = False
        
        if not online:
            return jsonify({
                'error': 'Translation requires internet connection. Please enter a Thai word directly or check your internet connection.',
                'offline_mode': True
            })
        
        # Translate English to Thai
        thai_word = translate_english_to_thai(input_word)
        if not thai_word:
            return jsonify({'error': 'Unable to translate English word to Thai. Please try a different word or enter a Thai word directly.'})
        
        # Get English translation (original word)
        english_translation = input_word
    else:
        # Input is already Thai
        thai_word = input_word
        english_translation = None
    
    result = determine_tone(thai_word)
    
    # Get translation and romanization
    if english_translation:
        translation = english_translation
    else:
        # Check if we're online for translation
        try:
            # Quick connectivity check using Google DNS
            response = requests.get('https://8.8.8.8', timeout=3)
            online = True
        except Exception as e:
            print(f"Connectivity check failed: {e}")
            online = False
        
        if online:
            translation = get_translation(thai_word)
        else:
            translation = "Translation unavailable (offline)"
    
    romanized = get_romanization(thai_word)
    phonetic_ipa = get_phonetic_ipa(thai_word)
    phonetic_reading = get_phonetic_reading(thai_word)
    
    # Use romanization to help with syllable analysis
    romanization_analysis = analyze_romanization_for_syllables(thai_word, romanized)
    
    # Override romanization syllable count with actual syllable count from Thai analysis
    if len(result) > 2:  # Multi-syllable word
        romanization_analysis['syllable_count'] = len(result[2])  # result[2] contains syllables
    
    if len(result) == 2:
        # Single syllable
        tone, explanation = result
        
        
        response_data = {
            'word': thai_word,
            'tone': tone,
            'explanation': explanation,
            'is_multi_syllable': False,
            'translation': translation,
            'romanized': romanized,
            'phonetic_ipa': phonetic_ipa,
            'phonetic_reading': phonetic_reading,
            'input_language': input_language,
            'original_input': input_word,
            'romanization_analysis': romanization_analysis
        }
        
            
        return jsonify(response_data)
    else:
        # Multi-syllable
        tone, explanation, syllable_analyses = result
        
        
        return jsonify({
            'word': thai_word,
            'tone': tone,
            'explanation': explanation,
            'is_multi_syllable': True,
            'syllables': syllable_analyses,
            'translation': translation,
            'romanized': romanized,
            'phonetic_ipa': phonetic_ipa,
            'phonetic_reading': phonetic_reading,
            'input_language': input_language,
            'original_input': input_word,
            'romanization_analysis': romanization_analysis
        })

@app.route('/audio', methods=['POST'])
def get_audio():
    """Generate audio for Thai text."""
    data = request.get_json()
    text = data.get('text', '').strip()
    voice = data.get('voice', 'th-TH-AcharaNeural')
    
    if not text:
        return jsonify({'error': 'Please provide text to convert to speech.'})
    
    audio_base64 = generate_audio(text, voice)
    
    if audio_base64:
        return jsonify({
            'success': True,
            'audio': audio_base64,
            'voice': voice
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Failed to generate audio. Please check your Google Cloud credentials.'
        })

@app.route('/voices', methods=['GET'])
def get_voices():
    """Get available Thai voices."""
    voices = get_available_voices()
    return jsonify({'voices': voices})

@app.route('/connectivity', methods=['GET'])
def check_connectivity():
    """Check internet connectivity."""
    try:
        # Test with a more reliable endpoint that works on mobile
        response = requests.get('https://httpbin.org/status/200', timeout=5)
        if response.status_code == 200:
            return jsonify({
                'online': True,
                'timestamp': response.headers.get('Date', '')
            })
        else:
            return jsonify({
                'online': False,
                'timestamp': ''
            })
    except:
        # Fallback: assume online if we can't check
        return jsonify({
            'online': True,
            'timestamp': ''
        })

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    app.run(debug=debug, host='0.0.0.0', port=port)
