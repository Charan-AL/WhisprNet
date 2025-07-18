import numpy as np
import cv2

class BrightnessDetector:
    def __init__(self):
        self.region_size = 50  # Size of detection region (50x50 pixels)
    
    def get_center_brightness(self, frame):
        """Get average brightness of center region"""
        h, w = frame.shape[:2]
        center_x, center_y = w // 2, h // 2
        
        # Define region of interest (center square)
        x1 = max(0, center_x - self.region_size)
        y1 = max(0, center_y - self.region_size)
        x2 = min(w, center_x + self.region_size)
        y2 = min(h, center_y + self.region_size)
        
        # Extract region
        roi = frame[y1:y2, x1:x2]
        
        # Convert to grayscale if needed
        if len(roi.shape) == 3:
            roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        else:
            roi_gray = roi
        
        # Calculate average brightness
        brightness = np.mean(roi_gray)
        return brightness

class SyncDetector:
    def __init__(self):
        self.start_pattern = "11110000"
        self.end_pattern = "00001111"
    
    def find_sync_patterns(self, bit_string):
        """Find start and end sync patterns in bit string"""
        start_pos = bit_string.find(self.start_pattern)
        end_pos = bit_string.find(self.end_pattern)
        
        return start_pos, end_pos
    
    def validate_sync(self, bit_string):
        """Validate that sync patterns are present and properly positioned"""
        start_pos, end_pos = self.find_sync_patterns(bit_string)
        
        if start_pos == -1:
            return False, "Start sync pattern not found"
        
        if end_pos == -1:
            return False, "End sync pattern not found"
        
        if end_pos <= start_pos + len(self.start_pattern):
            return False, "End sync pattern appears before start pattern"
        
        return True, "Sync patterns valid"

def create_sync_pattern():
    """Create synchronization patterns for message framing"""
    return {
        'start': "11110000",
        'end': "00001111"
    }

def calculate_transmission_time(message_length, bit_duration_ms):
    """Calculate estimated transmission time"""
    # Each character = 8 bits, Manchester doubles it = 16 bits per char
    # Plus sync patterns (8 + 8 = 16 bits)
    total_bits = (message_length * 16) + 16
    total_time_ms = total_bits * bit_duration_ms
    return total_time_ms / 1000.0  # Return in seconds

def validate_message(message):
    """Validate message for transmission"""
    if not message:
        return False, "Message cannot be empty"
    
    if len(message) > 500:  # Reasonable limit
        return False, "Message too long (max 500 characters)"
    
    try:
        message.encode('utf-8')
    except UnicodeEncodeError:
        return False, "Message contains invalid characters"
    
    return True, "Message valid"

class BitBuffer:
    def __init__(self, max_size=10000):
        self.buffer = []
        self.max_size = max_size
    
    def add_bit(self, bit):
        """Add bit to buffer"""
        self.buffer.append(str(bit))
        
        # Prevent buffer overflow
        if len(self.buffer) > self.max_size:
            self.buffer = self.buffer[-self.max_size//2:]  # Keep last half
    
    def get_buffer_string(self):
        """Get buffer as string"""
        return ''.join(self.buffer)
    
    def clear(self):
        """Clear buffer"""
        self.buffer = []
    
    def size(self):
        """Get buffer size"""
        return len(self.buffer)
