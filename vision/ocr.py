"""
OCR (Optical Character Recognition) Module for JARVIS Vision System

Extracts text from screenshots using Tesseract.
Supports multiple languages and formatting preservation.
"""

import pytesseract
import cv2
import numpy as np
from typing import Optional, List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class TextBlock:
    """Represents a block of extracted text."""
    text: str
    confidence: float
    bounding_box: Tuple[int, int, int, int]  # x, y, width, height
    language: str


class OCREngine:
    """
    Optical Character Recognition engine for text extraction.
    
    Features:
    - Extract text from images
    - Preserve text formatting
    - Detect language
    - Get text with confidence scores
    - Extract structured data
    """
    
    def __init__(self, tesseract_path: Optional[str] = None):
        """
        Initialize OCR engine.
        
        Args:
            tesseract_path: Optional path to Tesseract executable
        """
        if tesseract_path:
            pytesseract.pytesseract.pytesseract_cmd = tesseract_path
        
        self.languages = ['eng']  # Default English
        self.preprocessing_enabled = True
        self.confidence_threshold = 0.5
        
        # Test Tesseract availability
        self._test_tesseract()
    
    def _test_tesseract(self):
        """Test if Tesseract is available."""
        try:
            pytesseract.get_tesseract_version()
            print("✅ Tesseract OCR engine initialized")
        except Exception as e:
            print(f"⚠️  Tesseract not found: {e}")
            print("   Install with: choco install tesseract (Windows)")
    
    def extract_text(self, image: np.ndarray, languages: Optional[List[str]] = None) -> str:
        """
        Extract text from image.
        
        Args:
            image: Input image as numpy array
            languages: List of language codes (e.g., ['eng', 'fra'])
            
        Returns:
            Extracted text
        """
        try:
            # Preprocess if enabled
            if self.preprocessing_enabled:
                image = self._preprocess(image)
            
            # Set language
            lang = '+'.join(languages or self.languages)
            
            # Extract text
            text = pytesseract.image_to_string(image, lang=lang)
            
            return text.strip()
            
        except Exception as e:
            print(f"❌ OCR extraction error: {e}")
            return ""
    
    def extract_text_with_confidence(self, image: np.ndarray) -> List[TextBlock]:
        """
        Extract text with confidence scores and bounding boxes.
        
        Args:
            image: Input image as numpy array
            
        Returns:
            List of TextBlock objects with coordinates
        """
        try:
            if self.preprocessing_enabled:
                image = self._preprocess(image)
            
            # Get detailed information
            data = pytesseract.image_to_data(
                image,
                output_type=pytesseract.Output.DICT,
                lang='+'.join(self.languages)
            )
            
            blocks = []
            for i in range(len(data['text'])):
                text = data['text'][i]
                confidence = float(data['conf'][i]) / 100.0
                
                # Filter by confidence threshold
                if confidence < self.confidence_threshold:
                    continue
                
                if text.strip():  # Skip empty text
                    block = TextBlock(
                        text=text,
                        confidence=confidence,
                        bounding_box=(
                            data['left'][i],
                            data['top'][i],
                            data['width'][i],
                            data['height'][i]
                        ),
                        language=self.languages[0]
                    )
                    blocks.append(block)
            
            return blocks
            
        except Exception as e:
            print(f"❌ OCR confidence extraction error: {e}")
            return []
    
    def extract_code_blocks(self, image: np.ndarray) -> List[str]:
        """
        Extract code blocks from image (VS Code, terminal, etc.).
        
        Args:
            image: Input image as numpy array
            
        Returns:
            List of code blocks
        """
        text = self.extract_text(image)
        blocks = text.split('\n\n')  # Split by double newlines
        
        code_blocks = []
        for block in blocks:
            # Simple heuristic: code often has indentation or special chars
            if any(line.startswith((' ', '\t')) for line in block.split('\n')) or \
               any(char in block for char in ['{}', '[]', '()', '=>', '->']):
                code_blocks.append(block)
        
        return code_blocks
    
    def extract_numbers(self, image: np.ndarray) -> List[str]:
        """
        Extract numerical values from image.
        
        Args:
            image: Input image as numpy array
            
        Returns:
            List of numbers found
        """
        text = self.extract_text(image)
        
        import re
        numbers = re.findall(r'\d+\.?\d*', text)
        return numbers
    
    def extract_urls(self, image: np.ndarray) -> List[str]:
        """
        Extract URLs from image.
        
        Args:
            image: Input image as numpy array
            
        Returns:
            List of URLs found
        """
        text = self.extract_text(image)
        
        import re
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
        return urls
    
    def extract_emails(self, image: np.ndarray) -> List[str]:
        """
        Extract email addresses from image.
        
        Args:
            image: Input image as numpy array
            
        Returns:
            List of emails found
        """
        text = self.extract_text(image)
        
        import re
        emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        return emails
    
    def detect_language(self, image: np.ndarray) -> Dict[str, float]:
        """
        Detect language in image.
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Dictionary of detected languages with confidence
        """
        try:
            # Use Tesseract language detection
            osd = pytesseract.image_to_osd(image)
            
            # Parse output
            result = {}
            for line in osd.split('\n'):
                if 'Script:' in line or 'Confidence:' in line:
                    # Basic parsing
                    parts = line.split(':')
                    if len(parts) == 2:
                        key, value = parts
                        result[key.strip()] = value.strip()
            
            return result
            
        except Exception as e:
            print(f"⚠️  Language detection error: {e}")
            return {}
    
    def _preprocess(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for better OCR results.
        
        Args:
            image: Input image
            
        Returns:
            Preprocessed image
        """
        try:
            # Convert to grayscale
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # Apply threshold
            _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
            
            # Denoise
            denoised = cv2.medianBlur(binary, 3)
            
            return denoised
            
        except Exception as e:
            print(f"⚠️  Preprocessing error: {e}")
            return image
    
    def set_confidence_threshold(self, threshold: float):
        """
        Set minimum confidence threshold for text recognition.
        
        Args:
            threshold: Confidence threshold (0.0-1.0)
        """
        self.confidence_threshold = max(0.0, min(1.0, threshold))
        print(f"🔧 Confidence threshold set to {self.confidence_threshold}")
    
    def set_languages(self, languages: List[str]):
        """
        Set languages for OCR.
        
        Args:
            languages: List of language codes (e.g., ['eng', 'fra', 'deu'])
        """
        self.languages = languages
        print(f"🗣️  OCR languages set to: {', '.join(languages)}")
    
    def toggle_preprocessing(self, enable: bool = True):
        """
        Toggle image preprocessing.
        
        Args:
            enable: True to enable preprocessing
        """
        self.preprocessing_enabled = enable
        print(f"🔧 Image preprocessing {'enabled' if enable else 'disabled'}")
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages in Tesseract."""
        # Common language codes
        return [
            'eng',  # English
            'fra',  # French
            'deu',  # German
            'spa',  # Spanish
            'ita',  # Italian
            'por',  # Portuguese
            'rus',  # Russian
            'jpn',  # Japanese
            'chi_sim',  # Chinese Simplified
            'chi_tra',  # Chinese Traditional
        ]


# Global instance
_ocr_engine = None


def get_ocr_engine(tesseract_path: Optional[str] = None) -> OCREngine:
    """Get or create global OCR engine instance."""
    global _ocr_engine
    if _ocr_engine is None:
        _ocr_engine = OCREngine(tesseract_path)
    return _ocr_engine


# Example usage
if __name__ == "__main__":
    from vision.screen_capture import ScreenCapture
    
    print("🔍 OCR Engine Test")
    
    # Capture screen
    capture = ScreenCapture()
    screenshot = capture.capture_full_screen(resize=(800, 600))
    
    if screenshot is not None:
        # Initialize OCR
        ocr = OCREngine()
        
        print("\n📝 Extracting text...")
        text = ocr.extract_text(screenshot)
        print(f"Extracted text: {text[:200]}...")
        
        print("\n🔢 Extracting numbers...")
        numbers = ocr.extract_numbers(screenshot)
        print(f"Numbers found: {numbers}")
        
        print("\n🔗 Extracting URLs...")
        urls = ocr.extract_urls(screenshot)
        print(f"URLs found: {urls}")
        
        print("\n📧 Extracting emails...")
        emails = ocr.extract_emails(screenshot)
        print(f"Emails found: {emails}")
