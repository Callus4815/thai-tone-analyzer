#!/usr/bin/env python3
"""
Simplified test script for Thai tone analysis algorithm.
Tests a subset of vowels and patterns.
"""

import requests
import json

def test_word(word):
    """Test a single word and return the result."""
    try:
        response = requests.post(
            'http://localhost:5001/analyze',
            headers={'Content-Type': 'application/json'},
            json={'word': word},
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            return {
                'word': word,
                'success': True,
                'tone': result.get('tone', 'Unknown'),
                'explanation': result.get('explanation', ''),
                'syllables': result.get('syllables', []),
                'romanized': result.get('romanized', ''),
                'translation': result.get('translation', '')
            }
        else:
            return {
                'word': word,
                'success': False,
                'error': f'HTTP {response.status_code}'
            }
    except Exception as e:
        return {
            'word': word,
            'success': False,
            'error': str(e)
        }

# Test basic vowels
basic_vowels = [
    "กา", "กะ",  # a
    "กี", "กิ",  # i
    "กู", "กุ",  # u
    "เก", "เกะ", # e
    "แก", "แกะ", # ae
    "โก", "โกะ", # o
    "กอ", "เกาะ", # o
    "กือ", "กึ",  # ue
]

# Test tone marks
tone_marks = [
    "ก่า",  # mai ek
    "ก้า",  # mai tho
    "ก๊า",  # mai tri
    "ก๋า",  # mai chattawa
]

# Test edge cases
edge_cases = [
    "น่อง",  # อ as vowel
    "อะไร",  # อ as zero consonant
    "น่าเบื่อ",  # complex multi-syllable
    "โกรธ",  # consonant cluster
]

print("🧪 Thai Tone Analysis Test Suite")
print("=" * 50)

# Test basic vowels
print("\n📝 Testing basic vowels:")
print("-" * 30)
for word in basic_vowels:
    result = test_word(word)
    status = "✅" if result['success'] else "❌"
    tone_info = f" → {result['tone']}" if result['success'] else f" → ERROR"
    print(f"{status} {word}{tone_info}")

# Test tone marks
print("\n🎯 Testing tone marks:")
print("-" * 30)
for word in tone_marks:
    result = test_word(word)
    status = "✅" if result['success'] else "❌"
    tone_info = f" → {result['tone']}" if result['success'] else f" → ERROR"
    print(f"{status} {word}{tone_info}")

# Test edge cases
print("\n🔍 Testing edge cases:")
print("-" * 30)
for word in edge_cases:
    result = test_word(word)
    status = "✅" if result['success'] else "❌"
    tone_info = f" → {result['tone']}" if result['success'] else f" → ERROR"
    print(f"{status} {word}{tone_info}")
    if result['success'] and result['syllables']:
        for i, syllable in enumerate(result['syllables'], 1):
            print(f"    Syllable {i}: {syllable['syllable']} → {syllable['tone']}")

print("\n✅ Test completed!")
