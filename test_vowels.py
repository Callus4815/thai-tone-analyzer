#!/usr/bin/env python3
"""
Comprehensive test script for Thai tone analysis algorithm.
Tests all vowels, tone marks, and various consonant classes.
"""

import requests
import json
import time
from typing import List, Dict, Any

# Test data
no_tone_words = [
    "มา",  # mid tone
    "ผม",  # low tone
    "พ่อ",  # falling tone (long vowel, stop final)
    "สะ",  # high tone (short vowel)
    "หมอ",  # rising tone
]

tone_mark_words = [
    "ก่า",  # low tone (mai ek, low class)
    "ข่า",  # low tone (mai ek, high class)
    "เก้า",  # falling tone (mai tho)
    "ก๋า",  # high tone (mai tri)
    "ก๊า",  # high tone (mai tri with mid class consonant)
    "ก๋า",  # rising tone (mai chattawa, Northern Thai)
]

# All vowels with sample consonants (mid-class "ก")
vowel_words = [
    "กะ", "กา",
    "กิ", "กี",
    "กึ", "กือ",
    "กุ", "กู",
    "เกะ", "เก",
    "แกะ", "แก",
    "โกะ", "โก",
    "เกาะ", "กอ",
    "เกอะ", "เกอ",
    "เกียะ", "เกีย",
    "เกือะ", "เกือ",
    "กัวะ", "กัว",
    "ฤ", "ฤๅ",
    "ฦ", "ฦๅ",
]

# Additional test words for edge cases
edge_case_words = [
    "น่อง",  # อ as vowel
    "น่าเบื่อ",  # complex multi-syllable
    "อะไร",  # อ as zero consonant
    "อย่า",  # อ as silent tone modifier
    "โกรธ",  # consonant cluster
    "ใบบาง",  # complex syllable splitting
    "ใบแจ้ง",  # complex syllable splitting
    "กลับบ้าน",  # multi-syllable
    "มหาวิทยาลัย",  # complex multi-syllable
]

def test_word(word: str, expected_tone: str = None) -> Dict[str, Any]:
    """Test a single word and return the result."""
    try:
        response = requests.post(
            'http://localhost:5001/analyze',
            headers={'Content-Type': 'application/json'},
            json={'word': word},
            timeout=10
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
                'translation': result.get('translation', ''),
                'expected_tone': expected_tone,
                'tone_correct': expected_tone is None or result.get('tone') == expected_tone
            }
        else:
            return {
                'word': word,
                'success': False,
                'error': f'HTTP {response.status_code}: {response.text}',
                'expected_tone': expected_tone
            }
    except requests.exceptions.Timeout:
        return {
            'word': word,
            'success': False,
            'error': 'Request timeout',
            'expected_tone': expected_tone
        }
    except Exception as e:
        return {
            'word': word,
            'success': False,
            'error': str(e),
            'expected_tone': expected_tone
        }

def run_test_suite():
    """Run the complete test suite."""
    print("🧪 Thai Tone Analysis Test Suite")
    print("=" * 50)
    
    all_results = []
    
    # Test words without tone marks
    print("\n📝 Testing words without tone marks (default tones):")
    print("-" * 50)
    for word in no_tone_words:
        result = test_word(word)
        all_results.append(result)
        status = "✅" if result['success'] else "❌"
        tone_info = f" → {result['tone']}" if result['success'] else f" → ERROR: {result['error']}"
        print(f"{status} {word}{tone_info}")
        if result['success'] and result['explanation']:
            print(f"   Explanation: {result['explanation']}")
    
    # Test words with tone marks
    print("\n🎯 Testing words with tone marks (explicit tones):")
    print("-" * 50)
    for word in tone_mark_words:
        result = test_word(word)
        all_results.append(result)
        status = "✅" if result['success'] else "❌"
        tone_info = f" → {result['tone']}" if result['success'] else f" → ERROR: {result['error']}"
        print(f"{status} {word}{tone_info}")
        if result['success'] and result['explanation']:
            print(f"   Explanation: {result['explanation']}")
    
    # Test all vowels
    print("\n🔤 Testing all vowels with mid-class consonant 'ก':")
    print("-" * 50)
    for word in vowel_words:
        result = test_word(word)
        all_results.append(result)
        status = "✅" if result['success'] else "❌"
        tone_info = f" → {result['tone']}" if result['success'] else f" → ERROR: {result['error']}"
        print(f"{status} {word}{tone_info}")
        if result['success'] and result['explanation']:
            print(f"   Explanation: {result['explanation']}")
    
    # Test edge cases
    print("\n🔍 Testing edge cases:")
    print("-" * 50)
    for word in edge_case_words:
        result = test_word(word)
        all_results.append(result)
        status = "✅" if result['success'] else "❌"
        tone_info = f" → {result['tone']}" if result['success'] else f" → ERROR: {result['error']}"
        print(f"{status} {word}{tone_info}")
        if result['success'] and result['explanation']:
            print(f"   Explanation: {result['explanation']}")
    
    # Summary
    print("\n📊 Test Summary:")
    print("-" * 50)
    total_tests = len(all_results)
    successful_tests = sum(1 for r in all_results if r['success'])
    failed_tests = total_tests - successful_tests
    
    print(f"Total tests: {total_tests}")
    print(f"Successful: {successful_tests} ✅")
    print(f"Failed: {failed_tests} ❌")
    print(f"Success rate: {(successful_tests/total_tests)*100:.1f}%")
    
    # Show failed tests
    if failed_tests > 0:
        print("\n❌ Failed tests:")
        for result in all_results:
            if not result['success']:
                print(f"  - {result['word']}: {result['error']}")
    
    return all_results

def test_specific_words(words: List[str]):
    """Test specific words with detailed output."""
    print(f"\n🔍 Testing specific words: {', '.join(words)}")
    print("-" * 50)
    
    for word in words:
        result = test_word(word)
        print(f"\nWord: {word}")
        print(f"Success: {'✅' if result['success'] else '❌'}")
        
        if result['success']:
            print(f"Tone: {result['tone']}")
            print(f"Romanized: {result['romanized']}")
            print(f"Translation: {result['translation']}")
            print(f"Explanation: {result['explanation']}")
            
            if result['syllables']:
                print("Syllables:")
                for i, syllable in enumerate(result['syllables'], 1):
                    print(f"  {i}. {syllable['syllable']} → {syllable['tone']}")
                    print(f"     {syllable['explanation']}")
        else:
            print(f"Error: {result['error']}")

if __name__ == "__main__":
    print("Starting Thai Tone Analysis Test Suite...")
    print("Make sure the Flask app is running on http://localhost:5001")
    print()
    
    # Run the complete test suite
    results = run_test_suite()
    
    # Optionally test specific words with detailed output
    print("\n" + "="*50)
    test_specific_words(["น่าเบื่อ", "น่อง", "อะไร", "โกรธ"])
