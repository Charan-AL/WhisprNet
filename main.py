import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
from sender import ScreenFlicker
from receiver import CameraReceiver

class WhisprNetApp:
    def __init__(self, root):
        self.root = root
        self.root.title("WhisprNet - Optical Communication")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Initialize components
        self.screen_flicker = ScreenFlicker()
        self.camera_receiver = CameraReceiver()
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="WhisprNet", font=("Arial", 24, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        subtitle_label = ttk.Label(main_frame, text="Offline Anonymous Device-to-Device Chat", font=("Arial", 12))
        subtitle_label.grid(row=1, column=0, columnspan=2, pady=(0, 30))
        
        # Mode selection buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(0, 20))
        
        send_btn = ttk.Button(button_frame, text="📤 Send Message", command=self.open_sender_mode, width=20)
        send_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        receive_btn = ttk.Button(button_frame, text="📥 Receive Message", command=self.open_receiver_mode, width=20)
        receive_btn.pack(side=tk.LEFT)
        
        # Status area
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(20, 0))
        status_frame.columnconfigure(0, weight=1)
        
        self.status_text = scrolledtext.ScrolledText(status_frame, height=8, width=60)
        self.status_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Clear status button
        clear_btn = ttk.Button(status_frame, text="Clear Log", command=self.clear_status)
        clear_btn.grid(row=1, column=0, pady=(10, 0))
        
        self.log_message("WhisprNet initialized. Ready for optical communication!")
        
    def log_message(self, message):
        """Add message to status log"""
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)
        self.root.update_idletasks()
        
    def clear_status(self):
        """Clear the status log"""
        self.status_text.delete(1.0, tk.END)
        
    def open_sender_mode(self):
        """Open sender mode window"""
        sender_window = tk.Toplevel(self.root)
        sender_window.title("WhisprNet - Send Message")
        sender_window.geometry("500x400")
        sender_window.resizable(False, False)
        
        # Make window modal
        sender_window.transient(self.root)
        sender_window.grab_set()
        
        self.setup_sender_ui(sender_window)
        
    def setup_sender_ui(self, window):
        """Setup sender mode UI"""
        main_frame = ttk.Frame(window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Message input
        ttk.Label(main_frame, text="Enter your message:", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(0, 5))
        
        self.message_text = scrolledtext.ScrolledText(main_frame, height=8, width=50)
        self.message_text.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Controls frame
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Flicker speed
        ttk.Label(controls_frame, text="Flicker Speed (ms):").pack(side=tk.LEFT)
        self.speed_var = tk.StringVar(value="100")
        speed_entry = ttk.Entry(controls_frame, textvariable=self.speed_var, width=10)
        speed_entry.pack(side=tk.LEFT, padx=(5, 20))
        
        # Send button
        send_btn = ttk.Button(controls_frame, text="🚀 Start Transmission", command=self.start_transmission)
        send_btn.pack(side=tk.RIGHT)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=(10, 0))
        
    def start_transmission(self):
        """Start message transmission"""
        message = self.message_text.get(1.0, tk.END).strip()
        if not message:
            messagebox.showwarning("Warning", "Please enter a message to send!")
            return
            
        try:
            speed = int(self.speed_var.get())
            if speed < 50 or speed > 1000:
                raise ValueError("Speed must be between 50-1000ms")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid speed: {e}")
            return
            
        self.log_message(f"Starting transmission: '{message[:50]}{'...' if len(message) > 50 else ''}'")
        
        # Start transmission in separate thread
        def transmit():
            try:
                self.screen_flicker.send_message(message, speed, self.update_progress, self.log_message)
                self.log_message("✅ Transmission completed successfully!")
            except Exception as e:
                self.log_message(f"❌ Transmission failed: {str(e)}")
                
        thread = threading.Thread(target=transmit, daemon=True)
        thread.start()
        
    def update_progress(self, percentage):
        """Update progress bar"""
        self.progress_var.set(percentage)
        self.root.update_idletasks()
        
    def open_receiver_mode(self):
        """Open receiver mode window"""
        receiver_window = tk.Toplevel(self.root)
        receiver_window.title("WhisprNet - Receive Message")
        receiver_window.geometry("700x600")
        receiver_window.resizable(True, True)
        
        # Make window modal
        receiver_window.transient(self.root)
        receiver_window.grab_set()
        
        self.setup_receiver_ui(receiver_window)
        
    def setup_receiver_ui(self, window):
        """Setup receiver mode UI"""
        main_frame = ttk.Frame(window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Controls frame
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.start_receive_btn = ttk.Button(controls_frame, text="📹 Start Camera", command=self.start_receiving)
        self.start_receive_btn.pack(side=tk.LEFT)
        
        self.stop_receive_btn = ttk.Button(controls_frame, text="⏹️ Stop Camera", command=self.stop_receiving, state=tk.DISABLED)
        self.stop_receive_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # Camera status
        self.camera_status_label = ttk.Label(controls_frame, text="Camera: Stopped", foreground="red")
        self.camera_status_label.pack(side=tk.RIGHT)
        
        # Received messages
        ttk.Label(main_frame, text="Received Messages:", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(20, 5))
        
        self.received_text = scrolledtext.ScrolledText(main_frame, height=15, width=70)
        self.received_text.pack(fill=tk.BOTH, expand=True)
        
        # Detection info
        info_frame = ttk.LabelFrame(main_frame, text="Detection Info", padding="10")
        info_frame.pack(fill=tk.X, pady=(20, 0))
        
        self.detection_info = ttk.Label(info_frame, text="Waiting for camera...")
        self.detection_info.pack()
        
    def start_receiving(self):
        """Start camera and message reception"""
        self.start_receive_btn.config(state=tk.DISABLED)
        self.stop_receive_btn.config(state=tk.NORMAL)
        self.camera_status_label.config(text="Camera: Starting...", foreground="orange")
        
        def receive():
            try:
                self.camera_receiver.start_receiving(self.on_message_received, self.update_detection_info)
                self.camera_status_label.config(text="Camera: Active", foreground="green")
                self.log_message("📹 Camera started, listening for optical signals...")
            except Exception as e:
                self.log_message(f"❌ Camera error: {str(e)}")
                self.camera_status_label.config(text="Camera: Error", foreground="red")
                self.start_receive_btn.config(state=tk.NORMAL)
                self.stop_receive_btn.config(state=tk.DISABLED)
                
        thread = threading.Thread(target=receive, daemon=True)
        thread.start()
        
    def stop_receiving(self):
        """Stop camera and message reception"""
        self.camera_receiver.stop_receiving()
        self.start_receive_btn.config(state=tk.NORMAL)
        self.stop_receive_btn.config(state=tk.DISABLED)
        self.camera_status_label.config(text="Camera: Stopped", foreground="red")
        self.detection_info.config(text="Camera stopped")
        self.log_message("📹 Camera stopped")
        
    def on_message_received(self, message):
        """Handle received message"""
        self.received_text.insert(tk.END, f"📨 {message}\n" + "="*50 + "\n")
        self.received_text.see(tk.END)
        self.log_message(f"✅ Message received: '{message[:50]}{'...' if len(message) > 50 else ''}'")
        
    def update_detection_info(self, info):
        """Update detection information"""
        self.detection_info.config(text=info)

def main():
    root = tk.Tk()
    app = WhisprNetApp(root)
    
    # Handle window closing
    def on_closing():
        try:
            app.camera_receiver.stop_receiving()
        except:
            pass
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
