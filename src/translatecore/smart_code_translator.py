#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smart Code-Aware Universal Translator
Preserves Python code syntax while translating natural language text
Protects variables, functions, and expressions from being translated
"""

import os
import re
import ast
import json
import shutil
import unicodedata
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
import subprocess
import sys

class SmartCodeAwareTranslator:
    """Smart translator that protects code while translating text"""
    
    def __init__(self, source_lang: str = "auto", target_lang: str = "english"):
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.stats = {'files_processed': 0, 'translations_made': 0, 'ai_calls': 0}
        self.translation_cache = {}
        
        # Initialize translator engine
        self.translator_engine = self._init_translator_engine()
    
    def _init_translator_engine(self):
        """Initialize the best available translation engine"""
        try:
            # Import EnhancedTranslator from the same package
            from .enhanced_translator import EnhancedTranslator
            
            print("🤖 Using EnhancedTranslator with code-aware protection")
            return EnhancedTranslator(
                source_lang=self.source_lang,
                target_lang=self.target_lang,
                config_file="translation_api_config.json",
                service_config_name="development"
            )
        except Exception as e:
            print(f"⚠️ Could not initialize EnhancedTranslator: {e}")
            return None
    
    def detect_text_script(self, text: str) -> str:
        """Detects the writing system/script of text using Unicode categories"""
        if not text.strip():
            return "unknown"
        
        script_counts = {}
        
        for char in text:
            if char.isalpha():
                script_name = unicodedata.name(char, "").split()[0] if unicodedata.name(char, "") else "UNKNOWN"
                
                # Group similar scripts
                if "CYRILLIC" in script_name:
                    script = "cyrillic"
                elif "LATIN" in script_name:
                    script = "latin"
                elif "CJK" in script_name or "HIRAGANA" in script_name or "KATAKANA" in script_name:
                    script = "cjk"
                elif "ARABIC" in script_name:
                    script = "arabic"
                elif "HEBREW" in script_name:
                    script = "hebrew"
                elif "GREEK" in script_name:
                    script = "greek"
                else:
                    script = "other"
                
                script_counts[script] = script_counts.get(script, 0) + 1
        
        if not script_counts:
            return "unknown"
        
        # Return the most common script
        return max(script_counts.items(), key=lambda x: x[1])[0]
    
    def needs_translation(self, text: str) -> bool:
        """Determines if text needs translation using smart detection logic"""
        if not text or len(text.strip()) < 2:
            return False
        
        # Skip obvious code patterns
        code_indicators = [
            r'^\s*\w+\s*=',           # assignments
            r'^\s*(def|class|import|from|if|for|while|try|with|return)\s+',  # keywords
            r'^\s*#\s*\w+$',          # single word comments
            r'^\s*[{}()\[\]]+\s*$',   # only brackets/parens
            r'^\s*[0-9\.\,\-\+\*/=<>!&|]+\s*$',  # only numbers/operators
            r'^\w+\(\w*\)',           # function calls
            r'^\w+\.\w+',             # attribute access
            r'^[A-Z_][A-Z0-9_]*$',    # constants
        ]
        
        for pattern in code_indicators:
            if re.match(pattern, text.strip()):
                return False
        
        # Detect if text contains non-target language
        detected_script = self.detect_text_script(text)
        
        # Smart logic: if we're translating to English and text contains non-Latin scripts
        if self.target_lang.lower() == "english":
            return detected_script not in ["latin", "unknown"]
        
        # If translating from English, check for Latin script
        if self.source_lang.lower() == "english":
            return detected_script == "latin" and self._contains_english_words(text)
        
        # For other language pairs, use more sophisticated detection
        return self._is_natural_language_text(text)
    
    def _contains_english_words(self, text: str) -> bool:
        """Check if text contains common English words"""
        common_english = {
            "the", "and", "or", "of", "to", "in", "for", "with", "by", "from", 
            "up", "about", "into", "through", "during", "before", "after", 
            "above", "below", "between", "among", "is", "are", "was", "were",
            "be", "been", "being", "have", "has", "had", "do", "does", "did",
            "will", "would", "could", "should", "may", "might", "can", "must",
            "error", "warning", "info", "success", "failed", "loading", "loaded",
            "configuration", "service", "available", "ready", "method", "file"
        }
        
        words = re.findall(r'\b\w+\b', text.lower())
        english_count = sum(1 for word in words if word in common_english)
        
        return english_count > 0 and len(words) > 0
    
    def _is_natural_language_text(self, text: str) -> bool:
        """Determines if text is natural language vs code"""
        # Must have some letters
        if not re.search(r'[a-zA-Zа-яёА-ЯЁ\u4e00-\u9fff]', text):
            return False
        
        # Check ratio of letters to non-letters
        letters = sum(1 for c in text if c.isalpha())
        total_chars = len(text.replace(' ', ''))
        
        if total_chars == 0:
            return False
        
        letter_ratio = letters / total_chars
        
        # Natural language should have high letter ratio
        return letter_ratio > 0.6
    
    def extract_code_placeholders(self, text: str) -> Tuple[str, Dict[str, str]]:
        """
        Extracts Python code expressions and replaces them with placeholders
        Returns: (text_with_placeholders, placeholder_map)
        """
        placeholders = {}
        placeholder_counter = 0
        
        # Patterns to protect from translation (in order of priority)
        code_patterns = [
            # Python expressions in curly braces (f-strings) - must be first
            (r'\{[^}]+\}', 'expr'),
            # Dictionary/list access with square brackets
            (r'\[[^\]]+\]', 'index'),
            # Function calls with parentheses
            (r'\w+\([^)]*\)', 'func'),
            # Variable.attribute access
            (r'\b\w+(?:\.\w+)+', 'attr'),
            # Python keywords with following word
            (r'\b(?:def|class|import|from|if|elif|else|for|while|try|except|with|return|yield|break|continue|pass|assert|global|nonlocal|lambda)\s+\w+', 'keyword'),
            # Variable assignments
            (r'\b[a-zA-Z_а-яёА-ЯЁ][a-zA-Z0-9_а-яёА-ЯЁ]*\s*=', 'var'),
        ]
        
        result_text = text
        
        for pattern, code_type in code_patterns:
            matches = list(re.finditer(pattern, result_text))
            # Process matches from right to left to maintain positions
            for match in reversed(matches):
                placeholder_name = f"__CODE_PLACEHOLDER_{placeholder_counter}__"
                placeholders[placeholder_name] = match.group(0)
                
                result_text = (result_text[:match.start()] + 
                             placeholder_name + 
                             result_text[match.end():])
                placeholder_counter += 1
        
        return result_text, placeholders
    
    def restore_code_placeholders(self, text: str, placeholders: Dict[str, str]) -> str:
        """Restores original code expressions from placeholders"""
        result = text
        for placeholder, original_code in placeholders.items():
            # Case-insensitive replacement to handle AI changing case
            import re
            pattern = re.escape(placeholder)
            result = re.sub(pattern, original_code, result, flags=re.IGNORECASE)
        return result
    
    def ai_translate_safe(self, text: str) -> str:
        """Safely translates text while protecting code expressions"""
        if not text.strip():
            return text
        
        # Check cache first
        cache_key = f"{text}|{self.source_lang}|{self.target_lang}"
        if cache_key in self.translation_cache:
            return self.translation_cache[cache_key]
        
        if not self.translator_engine:
            return text  # No translation engine available
        
        try:
            # Extract and protect code
            protected_text, placeholders = self.extract_code_placeholders(text)
            
            # Skip translation if no natural language text remains
            if not self.needs_translation(protected_text):
                return text
            
            self.stats['ai_calls'] += 1
            
            # Translate the protected text
            result = self.translator_engine.translate(protected_text)
            translated = result.translated if hasattr(result, 'translated') else str(result)
            
            # Restore original code expressions
            final_result = self.restore_code_placeholders(translated, placeholders)
            
            # Cache the result
            self.translation_cache[cache_key] = final_result
            self.stats['translations_made'] += 1
            
            return final_result
            
        except Exception as e:
            print(f"  ⚠️ AI translation failed for '{text[:30]}...': {e}")
            return text
    
    def process_line_smart(self, line: str, line_num: int) -> Tuple[str, bool]:
        """Intelligently processes a line using code-aware AI logic"""
        if not line.strip():
            return line, False
        
        original_line = line
        result_line = line
        changes_made = False
        
        # Extract translatable segments using smart patterns
        segments_to_translate = []
        
        # 1. Comments - but protect code examples in comments
        comment_match = re.match(r'^(\s*#\s*)(.+)$', line)
        if comment_match:
            prefix, content = comment_match.groups()
            if self.needs_translation(content):
                segments_to_translate.append({
                    'original': content,
                    'start_pattern': prefix,
                    'end_pattern': '',
                    'type': 'comment',
                    'safe_translate': True
                })
        
        # 2. String literals - with special handling for f-strings and dictionary keys
        string_patterns = [
            # f-strings - need special code protection
            (r'(f["\'])([^"\']*)(["\'])', 'f-string', True),
            # Dictionary keys (single quotes) - these need to be translated but carefully
            (r"(\s*')([^']*?)('\s*:)", 'dict-key', True),
            # Dictionary keys (double quotes) - these need to be translated but carefully  
            (r'(\s*")([^"]*?)("\s*:)', 'dict-key', True),
            # Regular strings
            (r'(["\'])([^"\']*)(["\'])', 'string', False),
            # Raw strings
            (r'(r["\'])([^"\']*)(["\'])', 'raw-string', False),
        ]
        
        # Track processed positions to avoid duplicates
        processed_positions = set()
        
        for pattern, string_type, needs_code_protection in string_patterns:
            for match in re.finditer(pattern, line):
                quote_start, content, quote_end = match.groups()
                if self.needs_translation(content):
                    # Calculate position for replacement
                    start_pos = match.start()
                    end_pos = match.end()
                    
                    # Check if this position was already processed
                    position_key = (start_pos, end_pos, content)
                    if position_key in processed_positions:
                        continue
                    processed_positions.add(position_key)
                    
                    segments_to_translate.append({
                        'original': content,
                        'start_pos': start_pos,
                        'end_pos': end_pos,
                        'start_pattern': quote_start,
                        'end_pattern': quote_end,
                        'type': string_type,
                        'safe_translate': needs_code_protection
                    })
        
        # 3. Docstrings - also need code protection
        if '"""' in line or "'''" in line:
            quote_char = '"""' if '"""' in line else "'''"
            
            if line.count(quote_char) >= 1:
                # Extract content between quotes
                parts = line.split(quote_char)
                for i, part in enumerate(parts):
                    if i % 2 == 1 and self.needs_translation(part):  # Content inside quotes
                        segments_to_translate.append({
                            'original': part,
                            'start_pattern': quote_char,
                            'end_pattern': quote_char,
                            'type': 'docstring',
                            'safe_translate': True
                        })
        
        # Translate identified segments
        for segment in segments_to_translate:
            original_text = segment['original']
            
            # Use safe translation for code-containing text
            if segment.get('safe_translate', False):
                translated_text = self.ai_translate_safe(original_text)
            else:
                # For simple strings, check cache first
                cache_key = f"{original_text}|{self.source_lang}|{self.target_lang}"
                if cache_key in self.translation_cache:
                    translated_text = self.translation_cache[cache_key]
                else:
                    if self.translator_engine:
                        try:
                            result = self.translator_engine.translate(original_text)
                            translated_text = result.translated if hasattr(result, 'translated') else str(result)
                            self.translation_cache[cache_key] = translated_text
                            self.stats['ai_calls'] += 1
                            self.stats['translations_made'] += 1
                        except:
                            translated_text = original_text
                    else:
                        translated_text = original_text
            
            if translated_text != original_text:
                if 'start_pos' in segment:
                    # Replace by position
                    start_pos = segment['start_pos']
                    end_pos = segment['end_pos']
                    result_line = (result_line[:start_pos] + 
                                 segment['start_pattern'] + 
                                 translated_text + 
                                 segment['end_pattern'] + 
                                 result_line[end_pos:])
                else:
                    # Replace by pattern
                    old_pattern = segment['start_pattern'] + original_text + segment['end_pattern']
                    new_pattern = segment['start_pattern'] + translated_text + segment['end_pattern']
                    result_line = result_line.replace(old_pattern, new_pattern, 1)
                
                changes_made = True
                print(f"  🛡️ Line {line_num}: Code-safe {segment['type']}: '{original_text[:40]}...' → '{translated_text[:40]}...'")
        
        return result_line, changes_made
    
    def translate_file_smart(self, filepath: Path) -> bool:
        """Translates file using smart code-aware logic"""
        print(f"\n🛡️ Processing {filepath.name} with code-aware protection...")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"❌ Error reading {filepath}: {e}")
            return False
        
        # Quick check if translation is needed
        content = ''.join(lines)
        if not any(self.needs_translation(line) for line in lines[:50]):  # Check first 50 lines
            print(f"✅ No translation needed for {filepath.name}")
            return True
        
        # Process lines
        translated_lines = []
        changes_made = 0
        
        for line_num, line in enumerate(lines, 1):
            translated_line, was_changed = self.process_line_smart(line, line_num)
            translated_lines.append(translated_line)
            if was_changed:
                changes_made += 1
        
        if changes_made == 0:
            print(f"✅ No changes needed in {filepath.name}")
            return True
        
        # Validate syntax
        translated_content = ''.join(translated_lines)
        try:
            ast.parse(translated_content)
            print(f"✅ Syntax validation passed")
        except SyntaxError as e:
            print(f"❌ Syntax error would be introduced: {e}")
            print(f"   Error at line {e.lineno}: {e.text}")
            return False
        
        # Create backup
        backup_path = filepath.with_suffix('.py.backup_smart')
        if not backup_path.exists():
            shutil.copy2(filepath, backup_path)
            print(f"💾 Backup created: {backup_path.name}")
        
        # Write result
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(translated_content)
            print(f"✅ Successfully translated {filepath.name} ({changes_made} smart translations)")
            self.stats['files_processed'] += 1
            return True
        except Exception as e:
            print(f"❌ Error writing {filepath}: {e}")
            return False
    
    def run_smart_translation(self, files: List[str]) -> Dict:
        """Run smart code-aware translation on files"""
        print("🚀 Starting Smart Code-Aware Translation...")
        print(f"🎯 Source: {self.source_lang} → Target: {self.target_lang}")
        print(f"🛡️ Protecting Python code while translating text")
        print("=" * 70)
        
        success_count = 0
        
        for filepath_str in files:
            filepath = Path(filepath_str)
            
            if not filepath.exists():
                print(f"⚠️ File not found: {filepath}")
                continue
            
            if self.translate_file_smart(filepath):
                success_count += 1
        
        # Summary
        print("\n" + "=" * 70)
        print(f"📊 Smart Translation Summary:")
        print(f"   🤖 AI Translation Calls: {self.stats['ai_calls']}")
        print(f"   ✅ Files processed: {self.stats['files_processed']}")
        print(f"   🔄 Translations made: {self.stats['translations_made']}")
        print(f"   🎯 Success rate: {success_count}/{len(files)} files")
        print(f"   🛡️ Code expressions protected from translation")
        
        return {
            'files_processed': self.stats['files_processed'],
            'translations_made': self.stats['translations_made'],
            'ai_calls': self.stats['ai_calls'],
            'success_count': success_count,
            'total_files': len(files)
        }

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Smart code-aware translation script")
    parser.add_argument('--source', default='auto', help='Source language')
    parser.add_argument('--target', default='english', help='Target language')
    parser.add_argument('--files', nargs='+', help='Files to translate')
    
    args = parser.parse_args()
    
    # Default files if none specified
    if not args.files:
        args.files = [
            'src/translatecore/__init__.py',
            'src/translatecore/cli.py',
            'src/translatecore/enhanced_translator.py',
            'src/translatecore/config_loader.py',
            'src/translatecore/offline_translator.py'
        ]
    
    translator = SmartCodeAwareTranslator(args.source, args.target)
    results = translator.run_smart_translation(args.files)
    
    if results['success_count'] == results['total_files']:
        print("\n🎉 Smart code-aware translation completed successfully!")
        print("🛡️ All Python code expressions were protected!")
        print("🌍 Natural language translated, code syntax preserved!")
        print("\n💡 Test the results:")
        print("   python3 translate-cli.py \"Test message\" --source english --target russian")
    else:
        print(f"\n⚠️ {results['total_files'] - results['success_count']} files had issues")
        print("🔧 Check the error messages above and try again")

if __name__ == "__main__":
    main()
