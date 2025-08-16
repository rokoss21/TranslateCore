#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Code-aware translation module for TranslateCore
Handles translation of code files while preserving syntax
"""

import re
from typing import List, Tuple, Dict, Any
from dataclasses import dataclass

@dataclass
class CodeTranslationConfig:
    """Configuration for code translation"""
    translate_comments: bool = True
    translate_strings: bool = False  # Usually False to avoid breaking code
    translate_docstrings: bool = True
    preserve_keywords: bool = True
    preserve_function_names: bool = True
    preserve_variable_names: bool = True

class CodeTranslator:
    """Translates code files while preserving syntax and functionality"""
    
    # Programming language keywords to preserve
    KEYWORDS = {
        'python': [
            'def', 'class', 'import', 'from', 'if', 'else', 'elif', 'for', 'while',
            'try', 'except', 'finally', 'with', 'as', 'return', 'yield', 'lambda',
            'and', 'or', 'not', 'in', 'is', 'True', 'False', 'None', 'break', 'continue',
            'pass', 'global', 'nonlocal', 'assert', 'del', 'raise', 'async', 'await'
        ],
        'javascript': [
            'function', 'var', 'let', 'const', 'if', 'else', 'for', 'while', 'do',
            'try', 'catch', 'finally', 'return', 'break', 'continue', 'switch', 'case',
            'default', 'true', 'false', 'null', 'undefined', 'new', 'this', 'typeof',
            'instanceof', 'class', 'extends', 'super', 'static', 'async', 'await'
        ],
        'java': [
            'public', 'private', 'protected', 'class', 'interface', 'extends', 'implements',
            'static', 'final', 'abstract', 'if', 'else', 'for', 'while', 'do', 'switch',
            'case', 'default', 'try', 'catch', 'finally', 'throw', 'throws', 'return',
            'break', 'continue', 'new', 'this', 'super', 'true', 'false', 'null'
        ]
    }
    
    def __init__(self, translator, config: CodeTranslationConfig = None):
        self.translator = translator
        self.config = config or CodeTranslationConfig()
        
    def detect_language(self, code: str) -> str:
        """Detect programming language from code"""
        if re.search(r'\bdef\s+\w+\(', code) or 'import ' in code:
            return 'python'
        elif re.search(r'\bfunction\s+\w+\(', code) or 'var ' in code or 'let ' in code:
            return 'javascript'
        elif re.search(r'\bpublic\s+class\s+\w+', code) or 'System.out.' in code:
            return 'java'
        else:
            return 'unknown'
    
    def extract_translatable_parts(self, code: str, lang: str = None) -> List[Tuple[str, int, int, str]]:
        """
        Extract parts of code that can be safely translated
        Returns list of (text, start, end, type) tuples
        """
        if not lang:
            lang = self.detect_language(code)
            
        translatable_parts = []
        
        # Extract single-line comments
        if self.config.translate_comments:
            for match in re.finditer(r'#.*$|//.*$', code, re.MULTILINE):
                comment_text = match.group().lstrip('#').lstrip('/').strip()
                if comment_text and not self._is_code_like(comment_text):
                    translatable_parts.append((
                        comment_text, match.start(), match.end(), 'comment'
                    ))
        
        # Extract multi-line comments and docstrings
        if self.config.translate_docstrings:
            # Python docstrings
            for match in re.finditer(r'"""(.*?)"""', code, re.DOTALL):
                docstring_text = match.group(1).strip()
                if docstring_text and not self._is_code_like(docstring_text):
                    translatable_parts.append((
                        docstring_text, match.start(1), match.end(1), 'docstring'
                    ))
            
            # JavaScript/Java multi-line comments
            for match in re.finditer(r'/\*(.*?)\*/', code, re.DOTALL):
                comment_text = match.group(1).strip()
                if comment_text and not self._is_code_like(comment_text):
                    translatable_parts.append((
                        comment_text, match.start(1), match.end(1), 'multiline_comment'
                    ))
        
        # Extract string literals (optional)
        if self.config.translate_strings:
            for match in re.finditer(r'"([^"\\\\]*(\\\\.[^"\\\\]*)*)"|\'([^\'\\\\]*(\\\\.[^\'\\\\]*)*)\'', code):
                string_text = match.group(1) or match.group(3)
                if string_text and len(string_text) > 3 and not self._is_code_like(string_text):
                    translatable_parts.append((
                        string_text, match.start(1) or match.start(3), 
                        match.end(1) or match.end(3), 'string'
                    ))
        
        return sorted(translatable_parts, key=lambda x: x[1])
    
    def _is_code_like(self, text: str) -> bool:
        """Check if text looks like code (should not be translated)"""
        # Skip very short texts
        if len(text.strip()) < 3:
            return True
            
        # Skip if contains mainly code patterns
        code_patterns = [
            r'\w+\(\)',  # function calls
            r'\w+\.\w+',  # method calls
            r'[{}\[\]();]',  # code punctuation
            r'\b\d+\b',  # numbers only
            r'^[A-Z_]+$',  # constants
            r'^\w+$',  # single words that might be variables
        ]
        
        for pattern in code_patterns:
            if re.search(pattern, text):
                return True
        
        return False
    
    def translate_code(self, code: str, target_lang: str, source_lang: str = 'auto') -> Dict[str, Any]:
        """
        Translate code while preserving functionality
        
        Returns:
            Dict with 'translated_code', 'translations', 'preserved_parts'
        """
        lang = self.detect_language(code)
        translatable_parts = self.extract_translatable_parts(code, lang)
        
        if not translatable_parts:
            return {
                'translated_code': code,
                'translations': [],
                'preserved_parts': ['No translatable content found'],
                'language_detected': lang
            }
        
        # Translate each part
        translations = []
        translated_code = code
        offset = 0
        
        for text, start, end, part_type in translatable_parts:
            try:
                result = self.translator.translate(text, source_lang=source_lang, target_lang=target_lang)
                translated_text = result.translated if hasattr(result, 'translated') else str(result)
                
                # Apply translation to code
                actual_start = start + offset
                actual_end = end + offset
                
                translated_code = (
                    translated_code[:actual_start] + 
                    translated_text + 
                    translated_code[actual_end:]
                )
                
                # Update offset for next replacements
                offset += len(translated_text) - (end - start)
                
                translations.append({
                    'original': text,
                    'translated': translated_text,
                    'type': part_type,
                    'position': (start, end)
                })
                
            except Exception as e:
                translations.append({
                    'original': text,
                    'translated': text,  # Keep original on error
                    'type': part_type,
                    'position': (start, end),
                    'error': str(e)
                })
        
        preserved_parts = []
        if lang in self.KEYWORDS:
            preserved_parts.extend(self.KEYWORDS[lang])
        
        return {
            'translated_code': translated_code,
            'translations': translations,
            'preserved_parts': preserved_parts,
            'language_detected': lang,
            'config_used': self.config
        }

    def translate_file(self, file_path: str, target_lang: str, source_lang: str = 'auto', 
                      output_path: str = None) -> Dict[str, Any]:
        """Translate an entire code file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            result = self.translate_code(code, target_lang, source_lang)
            
            if output_path:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(result['translated_code'])
                result['output_file'] = output_path
            
            return result
            
        except Exception as e:
            return {
                'error': str(e),
                'file_path': file_path
            }

# Example usage and testing
if __name__ == "__main__":
    # Mock translator for testing
    class MockTranslator:
        def translate(self, text, source_lang='auto', target_lang='english'):
            # Simple mock translation
            translations = {
                'This is a comment': 'Это комментарий',
                'Calculate the sum': 'Вычислить сумму',
                'Print hello world': 'Напечатать привет мир'
            }
            
            class Result:
                def __init__(self, translated):
                    self.translated = translated
            
            return Result(translations.get(text, f"[TRANSLATED: {text}]"))
    
    # Test the code translator
    sample_code = '''
def calculate_sum(a, b):
    """Calculate the sum of two numbers"""
    # This is a comment
    result = a + b
    print("Hello world")  # Print hello world
    return result

class Calculator:
    """A simple calculator class"""
    
    def add(self, x, y):
        # Add two numbers
        return x + y
'''
    
    translator = MockTranslator()
    code_translator = CodeTranslator(translator)
    
    result = code_translator.translate_code(sample_code, 'russian')
    
    print("Original code:")
    print(sample_code)
    print("\nTranslated code:")
    print(result['translated_code'])
    print(f"\nLanguage detected: {result['language_detected']}")
    print(f"\nTranslations made: {len(result['translations'])}")
