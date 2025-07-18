import tkinter as tk
import time
from encoder_decoder import ManchesterEncoder
from utils import create_sync_pattern

class ScreenFlicker:
    def __init__(self):
        self.encoder = ManchesterEncoder()
        self.flicker_window = None
        self.is_transmitting = False
        
    def send_message(self, message, bit_duration_ms=100, progress_callback=None, log_callback=None):
        """Send message using screen flickers"""
        if self.is_transmitting:
            return
            
        self.is_transmitting = True
        
        try:
            # Encode message
            if log_callback:
                log_callback("🔄 Encoding message...")
            
            encoded_bits = self.encoder.encode_message(message)
            total_bits = len(encoded_bits)
            
            if log_callback:
                log_callback(f"📊 Encoded {len(message)} characters into {total_bits} bits")
                log_callback(f"⏱️ Estimated transmission time: {(total_bits * bit_duration_ms) / 1000:.1f} seconds")
            
            # Create flicker window
            self.create_flicker_window()
            
            # Convert bit duration to seconds
            bit_duration = bit_duration_ms / 1000.0
            
            # Transmit bits
            if log_callback:
                log_callback("🚀 Starting transmission...")
            
            for i, bit in enumerate(encoded_bits):
                if not self.is_transmitting:  # Check for cancellation
                    break
                    
                # Update flicker window
                self.update_flicker(bit == '1')
                
                # Update progress
                if progress_callback:
                    progress = (i + 1) / total_bits * 100
                    progress_callback(progress)
                
                # Wait for bit duration
                time.sleep(bit_duration)
            
            # Final black screen
            self.update_flicker(False)
            time.sleep(bit_duration)
            
            if log_callback:
                log_callback("✅ Transmission sequence completed")
                
        finally:
            self.is_transmitting = False
            self.close_flicker_window()
    
    def create_flicker_window(self):
        """Create the flicker window"""
        self.flicker_window = tk.Toplevel()
        self.flicker_window.title("WhisprNet - Transmitting")
        self.flicker_window.geometry("200x200+100+100")  # 200x200 window at position 100,100
        self.flicker_window.resizable(False, False)
        self.flicker_window.attributes('-topmost', True)  # Keep on top
        
        # Create flicker area (canvas)
        self.flicker_canvas = tk.Canvas(
            self.flicker_window, 
            width=200, 
            height=200, 
            highlightthickness=0
        )
        self.flicker_canvas.pack()
        
        # Create the flicker rectangle (100x100 in center)
        self.flicker_rect = self.flicker_canvas.create_rectangle(
            50, 50, 150, 150,  # 100x100 rectangle in center
            fill='black',
            outline='gray',
            width=2
        )
        
        # Add instruction text
        self.flicker_canvas.create_text(
            100, 25, 
            text="Transmitting...", 
            fill='blue',
            font=('Arial', 10, 'bold')
        )
        
        self.flicker_canvas.create_text(
            100, 175, 
            text="Point camera here", 
            fill='blue',
            font=('Arial', 8)
        )
    
    def update_flicker(self, is_high):
        """Update flicker state"""
        if self.flicker_window and self.flicker_canvas:
            color = 'white' if is_high else 'black'
            self.flicker_canvas.itemconfig(self.flicker_rect, fill=color)
            self.flicker_window.update()
    
    def close_flicker_window(self):
        """Close the flicker window"""
        if self.flicker_window:
            self.flicker_window.destroy()
            self.flicker_window = None
    
    def stop_transmission(self):
        """Stop ongoing transmission"""
        self.is_transmitting = False
