#!/usr/bin/env python3
"""
Comprehensive test script for Thai tone analysis algorithm.
Tests all the specific words mentioned by the user.
"""

import requests
import json

def test_word(word, expected_tone=None):
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
            actual_tone = result.get('tone', 'Unknown')
            tone_correct = expected_tone is None or actual_tone == expected_tone
            
            return {
                'word': word,
                'success': True,
                'tone': actual_tone,
                'expected_tone': expected_tone,
                'tone_correct': tone_correct,
                'explanation': result.get('explanation', ''),
                'syllables': result.get('syllables', []),
                'romanized': result.get('romanized', ''),
                'translation': result.get('translation', '')
            }
        else:
            return {
                'word': word,
                'success': False,
                'error': f'HTTP {response.status_code}',
                'expected_tone': expected_tone
            }
    except Exception as e:
        return {
            'word': word,
            'success': False,
            'error': str(e),
            'expected_tone': expected_tone
        }

# Test data with expected tones
test_cases = [
    # Words without tone marks (default tones)
    ("มา", "Mid"),  # mid tone
    ("ผม", "Low"),  # rising tone  
    ("พ่อ", "Falling"),  # falling tone (long vowel, stop final)
    ("สะ", "High"),  # high tone (short vowel)
    ("หมอ", "Rising"),  # rising tone
    
    # Words with tone marks (explicit tones)
    ("ก่า", "Low"),  # low tone (mai ek, low class)
    ("ข่า", "Low"),  # low tone (mai ek, high class)
    ("เก้า", "Falling"),  # falling tone (mai tho)
    ("ก๋า", "Rising"),  # rising tone (mai chattawa)
    ("ก๊า", "High"),  # high tone (mai tri)
    
    # All vowels with sample consonants (mid-class "ก")
    ("กะ", "Low"), ("กา", "Mid"),
    ("กิ", "Low"), ("กี", "Mid"),
    ("กึ", "Low"), ("กือ", "Mid"),
    ("กุ", "Low"), ("กู", "Mid"),
    ("เกะ", "Low"), ("เก", "Low"),
    ("แกะ", "Low"), ("แก", "Low"),
    ("โกะ", "Low"), ("โก", "Low"),
    ("เกาะ", "Mid"), ("กอ", "Mid"),
    ("เกอะ", "Low"), ("เกอ", "Low"),
    ("เกียะ", "Low"), ("เกีย", "Mid"),
    ("เกือะ", "Low"), ("เกือ", "Mid"),
    ("กัวะ", "Low"), ("กัว", "Mid"),
    ("ฤ", "Low"), ("ฤๅ", "Mid"),
    ("ฦ", "Low"), ("ฦๅ", "Mid"),
]

print("🧪 Comprehensive Thai Tone Analysis Test Suite")
print("=" * 60)

all_results = []
correct_tones = 0
total_tests = 0

for word, expected_tone in test_cases:
    result = test_word(word, expected_tone)
    all_results.append(result)
    total_tests += 1
    
    if result['success']:
        if result['tone_correct']:
            correct_tones += 1
            status = "✅"
        else:
            status = "⚠️"
        print(f"{status} {word:8} → {result['tone']:8} (expected: {expected_tone})")
    else:
        print(f"❌ {word:8} → ERROR: {result['error']}")

print(f"\n📊 Results Summary:")
print(f"Total tests: {total_tests}")
print(f"Successful requests: {sum(1 for r in all_results if r['success'])}")
print(f"Correct tones: {correct_tones}")
print(f"Tone accuracy: {(correct_tones/total_tests)*100:.1f}%")

# Show incorrect tones
incorrect_tones = [r for r in all_results if r['success'] and not r['tone_correct']]
if incorrect_tones:
    print(f"\n⚠️  Incorrect tones ({len(incorrect_tones)}):")
    for result in incorrect_tones:
        print(f"  {result['word']}: got '{result['tone']}', expected '{result['expected_tone']}'")

# Show failed requests
failed_requests = [r for r in all_results if not r['success']]
if failed_requests:
    print(f"\n❌ Failed requests ({len(failed_requests)}):")
    for result in failed_requests:
        print(f"  {result['word']}: {result['error']}")

print(f"\n✅ Test completed!")
