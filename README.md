# WhisprNet - Optical Communication Desktop App

WhisprNet is a Python desktop application that enables offline, anonymous device-to-device communication using screen flickers and camera decoding. It implements optical communication using visible light modulation.

## Features

- **Sender Mode**: Convert text messages to binary, apply Manchester encoding, and transmit via screen flickers
- **Receiver Mode**: Use camera to detect light changes and decode messages back to text
- **Manchester Encoding**: Robust encoding scheme (0 → 10, 1 → 01) for reliable transmission
- **Sync Patterns**: Start (11110000) and end (00001111) sequences for message framing
- **Real-time Processing**: Live camera feed with brightness detection and bit visualization
- **User-friendly GUI**: Intuitive Tkinter interface with progress tracking and status logging

## Installation

1. **Install Python 3.7+**

2. **Install required dependencies:**
\`\`\`bash
pip install opencv-python numpy cryptography
\`\`\`

3. **Run the application:**
\`\`\`bash
python main.py
\`\`\`

## How It Works

### Transmission Process
1. User enters a text message
2. Message is encoded to UTF-8 binary
3. Manchester encoding is applied (0→10, 1→01)
4. Sync patterns are added (start + data + end)
5. Screen flickers white/black to represent 1s/0s
6. Each bit is displayed for ~100ms (configurable)

### Reception Process
1. Camera captures video feed
2. Brightness is analyzed in center region (100x100px equivalent)
3. Brightness changes are converted to binary
4. Manchester decoding recovers original binary data
5. Binary is converted back to UTF-8 text
6. Message is displayed when sync patterns are detected

### Manchester Encoding
- **0 bit** → **10** (Low-High transition)
- **1 bit** → **01** (High-Low transition)
- Provides clock recovery and error detection
- Doubles the transmission time but increases reliability

## Usage

### Sending Messages
1. Click "📤 Send Message"
2. Enter your message in the text area
3. Adjust flicker speed if needed (50-1000ms)
4. Click "🚀 Start Transmission"
5. Point the receiving device's camera at the flicker window

### Receiving Messages
1. Click "📥 Receive Message"
2. Click "📹 Start Camera"
3. Point camera at the sender's flicker window
4. Received messages will appear in the text area
5. Click "⏹️ Stop Camera" when done

## Technical Details

### File Structure
- `main.py` - Main GUI application and window management
- `sender.py` - Screen flickering and transmission logic
- `receiver.py` - Camera capture and signal processing
- `encoder_decoder.py` - Manchester encoding/decoding algorithms
- `utils.py` - Helper functions for brightness detection and sync

### Communication Protocol
\`\`\`
[Start Sync: 11110000] + [Manchester Encoded Data] + [End Sync: 00001111]
\`\`\`

### Performance
- **Transmission Speed**: ~10 characters per second (at 100ms/bit)
- **Range**: Depends on camera quality and lighting conditions
- **Reliability**: High with Manchester encoding and sync patterns

## Troubleshooting

### Camera Issues
- Ensure camera is not being used by another application
- Try different lighting conditions
- Adjust camera position and distance from screen

### Detection Problems
- Increase flicker duration for better detection
- Ensure good contrast between screen and background
- Point camera directly at the flicker area

### Decoding Errors
- Check for proper sync pattern alignment
- Verify lighting conditions are stable
- Ensure camera is focused on the flicker region

## Limitations

- Requires line-of-sight between devices
- Sensitive to lighting conditions
- Relatively slow transmission speed
- Limited range (typically 1-3 feet)

## Future Enhancements

- AES encryption for secure communication
- QR code fallback mode
- Error correction codes (Hamming)
- Adjustable detection regions
- Multiple flicker areas for higher bandwidth
- Audio feedback for successful transmission

## License

This project is for educational and experimental purposes. Use responsibly and in accordance with local regulations.
\`\`\`

```python file="scripts/test_encoding.py"
#!/usr/bin/env python3
"""
Test script for WhisprNet encoding/decoding functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from encoder_decoder import ManchesterEncoder, ManchesterDecoder
from utils import validate_message, calculate_transmission_time

def test_manchester_encoding():
    """Test Manchester encoding and decoding"""
    print("🧪 Testing Manchester Encoding/Decoding")
    print("=" * 50)
    
    encoder = ManchesterEncoder()
    decoder = ManchesterDecoder()
    
    test_messages = [
        "Hello World!",
        "Test 123",
        "🚀 Unicode test! 📡",
        "A",
        "This is a longer message to test the encoding and decoding process with more data.",
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\nTest {i}: '{message}'")
        print(f"Length: {len(message)} characters")
        
        # Validate message
        valid, error = validate_message(message)
        if not valid:
            print(f"❌ Validation failed: {error}")
            continue
        
        try:
            # Encode
            encoded_bits = encoder.encode_message(message)
            print(f"Encoded bits: {len(encoded_bits)} bits")
            print(f"Transmission time (100ms/bit): {calculate_transmission_time(len(message), 100):.1f}s")
            
            # Show first 50 bits for inspection
            print(f"First 50 bits: {encoded_bits[:50]}...")
            
            # Decode
            decoded_message = decoder.decode_message(encoded_bits)
            print(f"Decoded: '{decoded_message}'")
            
            # Verify
            if message == decoded_message:
                print("✅ Test passed!")
            else:
                print("❌ Test failed - messages don't match!")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")

def test_sync_patterns():
    """Test sync pattern detection"""
    print("\n🔍 Testing Sync Pattern Detection")
    print("=" * 50)
    
    encoder = ManchesterEncoder()
    decoder = ManchesterDecoder()
    
    # Test with noise
    message = "Test"
    encoded = encoder.encode_message(message)
    
    # Add noise before and after
    noisy_signal = "1010101010" + encoded + "0101010101"
    
    print(f"Original message: '{message}'")
    print(f"Signal with noise: {len(noisy_signal)} bits")
    
    try:
        decoded = decoder.decode_message(noisy_signal)
        print(f"Decoded from noisy signal: '{decoded}'")
        
        if message == decoded:
            print("✅ Sync pattern detection works!")
        else:
            print("❌ Sync pattern detection failed!")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_error_conditions():
    """Test error handling"""
    print("\n⚠️ Testing Error Conditions")
    print("=" * 50)
    
    decoder = ManchesterDecoder()
    
    error_cases = [
        ("No sync patterns", "1010101010101010"),
        ("Only start sync", "11110000101010101010"),
        ("Only end sync", "10101010100001111"),
        ("Invalid Manchester pair", "11110000111000001111"),  # 11 is invalid
        ("Odd length Manchester", "111100001010100001111"),  # Odd length
    ]
    
    for test_name, bit_string in error_cases:
        print(f"\nTesting: {test_name}")
        try:
            result = decoder.decode_message(bit_string)
            print(f"❌ Should have failed but got: '{result}'")
        except Exception as e:
            print(f"✅ Correctly caught error: {str(e)}")

if __name__ == "__main__":
    print("WhisprNet Encoding Test Suite")
    print("=" * 50)
    
    test_manchester_encoding()
    test_sync_patterns()
    test_error_conditions()
    
    print("\n🎉 Test suite completed!")
