import struct

class ManchesterEncoder:
    def __init__(self):
        self.start_sync = "11110000"  # Start synchronization pattern
        self.end_sync = "00001111"    # End synchronization pattern
    
    def encode_message(self, message):
        """Encode message with Manchester encoding"""
        # Convert message to binary (UTF-8)
        message_bytes = message.encode('utf-8')
        binary_data = ''.join(format(byte, '08b') for byte in message_bytes)
        
        # Apply Manchester encoding (0 -> 10, 1 -> 01)
        manchester_data = self.manchester_encode(binary_data)
        
        # Add sync patterns
        encoded_message = self.start_sync + manchester_data + self.end_sync
        
        return encoded_message
    
    def manchester_encode(self, binary_string):
        """Apply Manchester encoding: 0 -> 10, 1 -> 01"""
        encoded = ""
        for bit in binary_string:
            if bit == '0':
                encoded += "10"
            elif bit == '1':
                encoded += "01"
        return encoded

class ManchesterDecoder:
    def __init__(self):
        self.start_sync = "11110000"
        self.end_sync = "00001111"
    
    def decode_message(self, bit_string):
        """Decode Manchester encoded message"""
        # Find start and end sync patterns
        start_pos = bit_string.find(self.start_sync)
        if start_pos == -1:
            raise ValueError("Start sync pattern not found")
        
        # Look for end sync after start
        search_start = start_pos + len(self.start_sync)
        end_pos = bit_string.find(self.end_sync, search_start)
        if end_pos == -1:
            raise ValueError("End sync pattern not found")
        
        # Extract Manchester encoded data
        manchester_data = bit_string[search_start:end_pos]
        
        # Decode Manchester encoding
        binary_data = self.manchester_decode(manchester_data)
        
        # Convert binary to message
        message = self.binary_to_message(binary_data)
        
        return message
    
    def manchester_decode(self, manchester_string):
        """Decode Manchester encoding: 10 -> 0, 01 -> 1"""
        if len(manchester_string) % 2 != 0:
            raise ValueError("Manchester data length must be even")
        
        decoded = ""
        for i in range(0, len(manchester_string), 2):
            pair = manchester_string[i:i+2]
            if pair == "10":
                decoded += "0"
            elif pair == "01":
                decoded += "1"
            else:
                raise ValueError(f"Invalid Manchester pair: {pair}")
        
        return decoded
    
    def binary_to_message(self, binary_string):
        """Convert binary string to UTF-8 message"""
        if len(binary_string) % 8 != 0:
            raise ValueError("Binary data length must be multiple of 8")
        
        message_bytes = []
        for i in range(0, len(binary_string), 8):
            byte_str = binary_string[i:i+8]
            byte_val = int(byte_str, 2)
            message_bytes.append(byte_val)
        
        try:
            message = bytes(message_bytes).decode('utf-8')
            return message
        except UnicodeDecodeError:
            raise ValueError("Invalid UTF-8 data")
