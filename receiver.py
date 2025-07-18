import cv2
import numpy as np
import time
import threading
from encoder_decoder import ManchesterDecoder
from utils import BrightnessDetector, SyncDetector

class CameraReceiver:
    def __init__(self):
        self.decoder = ManchesterDecoder()
        self.brightness_detector = BrightnessDetector()
        self.sync_detector = SyncDetector()
        self.cap = None
        self.is_receiving = False
        self.receive_thread = None
        
    def start_receiving(self, message_callback, info_callback):
        """Start camera and begin receiving messages"""
        if self.is_receiving:
            return
            
        # Initialize camera
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise Exception("Could not open camera")
            
        # Set camera properties for better performance
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        self.is_receiving = True
        self.message_callback = message_callback
        self.info_callback = info_callback
        
        # Start receiving thread
        self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
        self.receive_thread.start()
    
    def stop_receiving(self):
        """Stop receiving and release camera"""
        self.is_receiving = False
        
        if self.receive_thread:
            self.receive_thread.join(timeout=2.0)
            
        if self.cap:
            self.cap.release()
            self.cap = None
            
        cv2.destroyAllWindows()
    
    def _receive_loop(self):
        """Main receiving loop"""
        bit_buffer = []
        last_brightness = None
        frame_count = 0
        
        # Detection parameters
        stable_frames_needed = 3  # Frames needed to confirm bit transition
        current_bit_frames = 0
        current_bit_value = None
        
        try:
            while self.is_receiving:
                ret, frame = self.cap.read()
                if not ret:
                    continue
                    
                frame_count += 1
                
                # Extract brightness from center region
                brightness = self.brightness_detector.get_center_brightness(frame)
                
                # Convert brightness to binary (threshold-based)
                current_binary = 1 if brightness > 128 else 0
                
                # Show camera feed with overlay
                self._show_camera_feed(frame, brightness, current_binary)
                
                # Detect bit transitions
                if current_bit_value is None:
                    current_bit_value = current_binary
                    current_bit_frames = 1
                elif current_bit_value == current_binary:
                    current_bit_frames += 1
                else:
                    # Bit transition detected
                    if current_bit_frames >= stable_frames_needed:
                        bit_buffer.append(str(current_bit_value))
                        
                        # Update info
                        if self.info_callback:
                            self.info_callback(f"Bits received: {len(bit_buffer)} | Current: {current_bit_value} | Brightness: {brightness:.1f}")
                        
                        # Check for complete message
                        if len(bit_buffer) >= 16:  # Minimum for start + end sync
                            message = self._try_decode_message(bit_buffer)
                            if message:
                                if self.message_callback:
                                    self.message_callback(message)
                                bit_buffer = []  # Clear buffer after successful decode
                    
                    current_bit_value = current_binary
                    current_bit_frames = 1
                
                # Limit buffer size to prevent memory issues
                if len(bit_buffer) > 10000:  # Max ~1250 characters
                    bit_buffer = bit_buffer[-5000:]  # Keep last half
                
                # Small delay to prevent excessive CPU usage
                time.sleep(0.01)
                
        except Exception as e:
            if self.info_callback:
                self.info_callback(f"Error: {str(e)}")
    
    def _show_camera_feed(self, frame, brightness, current_bit):
        """Show camera feed with detection overlay"""
        # Create a copy for display
        display_frame = frame.copy()
        h, w = display_frame.shape[:2]
        
        # Draw center detection region (100x100 equivalent)
        center_x, center_y = w // 2, h // 2
        region_size = 50  # 50 pixels radius for detection region
        
        color = (0, 255, 0) if current_bit else (0, 0, 255)  # Green for 1, Red for 0
        cv2.rectangle(
            display_frame,
            (center_x - region_size, center_y - region_size),
            (center_x + region_size, center_y + region_size),
            color,
            2
        )
        
        # Add text overlay
        cv2.putText(display_frame, f"Brightness: {brightness:.1f}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(display_frame, f"Bit: {current_bit}", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        cv2.putText(display_frame, "Point at flicker area", (10, h - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        
        # Show frame
        cv2.imshow('WhisprNet - Camera Feed', display_frame)
        cv2.waitKey(1)
    
    def _try_decode_message(self, bit_buffer):
        """Try to decode message from bit buffer"""
        try:
            # Convert bit list to string
            bit_string = ''.join(bit_buffer)
            
            # Try to find and decode message
            message = self.decoder.decode_message(bit_string)
            return message
            
        except Exception as e:
            # Decoding failed, continue collecting bits
            return None
