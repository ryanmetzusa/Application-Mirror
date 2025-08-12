#!/usr/bin/env python3
"""
Window Mirror - Clean Python Version for EXE Conversion
Mirrors window content without interrupting workflow
"""

import cv2
import numpy as np
import pygetwindow as gw
import mss
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import platform
import queue
from PIL import Image, ImageTk
import sys

# Windows-specific imports
if platform.system() == "Windows":
    try:
        import win32gui
        import win32con
        import win32ui
        import win32api
        from ctypes import windll
        WINDOWS_AVAILABLE = True
    except ImportError:
        WINDOWS_AVAILABLE = False
        print("Warning: pywin32 not available")
else:
    WINDOWS_AVAILABLE = False

class WindowMirror:
    def __init__(self):
        self.target_window = None
        self.running = False
        self.sct = None
        self.update_interval = 0.016  # 60 FPS
        self.exclude_title_bar = True
        self.hwnd = None
        self.original_foreground_window = None
        self.target_fps = 60
        
        # Threading for continuous capture
        self.frame_queue = queue.Queue(maxsize=5)
        self.capture_thread = None
        self.capture_running = False
        self.mirror_window = None
        
    def list_windows(self):
        """List all available windows with their titles"""
        windows = gw.getAllWindows()
        visible_windows = []
        
        for window in windows:
            if window.title and len(window.title.strip()) > 0:
                if window.width > 100 and window.height > 100:
                    visible_windows.append({
                        'title': window.title,
                        'window': window
                    })
        
        return visible_windows
    
    def find_window_handle(self, window):
        """Find Windows HWND for the window"""
        if not WINDOWS_AVAILABLE:
            return None
            
        try:
            def enum_window_callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    window_text = win32gui.GetWindowText(hwnd)
                    if window_text == window.title:
                        windows.append(hwnd)
                return True
            
            windows = []
            win32gui.EnumWindows(enum_window_callback, windows)
            return windows[0] if windows else None
        except Exception:
            return None
    
    def get_capture_coordinates(self, window):
        """Get the correct coordinates for capture based on settings"""
        try:
            if not self.exclude_title_bar:
                return {
                    'left': window.left,
                    'top': window.top,
                    'width': window.width,
                    'height': window.height
                }
            
            # For excluding title bar, use Win32 API if available
            if WINDOWS_AVAILABLE and self.hwnd:
                try:
                    client_rect = win32gui.GetClientRect(self.hwnd)
                    client_point = win32gui.ClientToScreen(self.hwnd, (0, 0))
                    
                    return {
                        'left': client_point[0],
                        'top': client_point[1],
                        'width': client_rect[2],
                        'height': client_rect[3]
                    }
                except Exception:
                    pass
            
            # Fallback: estimate title bar exclusion
            title_bar_height = 32
            border_width = 8
            
            return {
                'left': window.left + border_width,
                'top': window.top + title_bar_height,
                'width': max(100, window.width - (2 * border_width)),
                'height': max(100, window.height - title_bar_height - border_width)
            }
            
        except Exception:
            return {
                'left': window.left,
                'top': window.top,
                'width': window.width,
                'height': window.height
            }
    
    def capture_window_direct(self, window):
        """Try to capture window directly"""
        if not (WINDOWS_AVAILABLE and self.hwnd):
            return None
            
        try:
            if self.exclude_title_bar:
                client_rect = win32gui.GetClientRect(self.hwnd)
                width = client_rect[2]
                height = client_rect[3]
            else:
                window_rect = win32gui.GetWindowRect(self.hwnd)
                width = window_rect[2] - window_rect[0]
                height = window_rect[3] - window_rect[1]
            
            if width <= 0 or height <= 0:
                return None
            
            # Try PrintWindow with client-only flag
            hwndDC = win32gui.GetDC(self.hwnd) if self.exclude_title_bar else win32gui.GetWindowDC(self.hwnd)
            mfcDC = win32ui.CreateDCFromHandle(hwndDC)
            saveDC = mfcDC.CreateCompatibleDC()
            
            saveBitMap = win32ui.CreateBitmap()
            saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
            saveDC.SelectObject(saveBitMap)
            
            flag = 1 if self.exclude_title_bar else 2
            result = windll.user32.PrintWindow(self.hwnd, saveDC.GetSafeHdc(), flag)
            
            if result:
                bmpstr = saveBitMap.GetBitmapBits(True)
                img = np.frombuffer(bmpstr, dtype='uint8')
                img.shape = (height, width, 4)
                img_bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                
                # Cleanup
                saveDC.DeleteDC()
                mfcDC.DeleteDC()
                win32gui.ReleaseDC(self.hwnd, hwndDC)
                win32gui.DeleteObject(saveBitMap.GetHandle())
                
                # Check if image is not blank
                if not (np.all(img_bgr == 0) or np.all(img_bgr == 255)):
                    return img_bgr
            else:
                # Cleanup
                saveDC.DeleteDC()
                mfcDC.DeleteDC()
                win32gui.ReleaseDC(self.hwnd, hwndDC)
                win32gui.DeleteObject(saveBitMap.GetHandle())
            
        except Exception:
            pass
            
        return None
    
    def capture_window_screen(self, window):
        """Screen capture method"""
        try:
            if self.sct is None:
                self.sct = mss.mss()
            
            coords = self.get_capture_coordinates(window)
            
            monitor = {
                "top": coords['top'],
                "left": coords['left'],
                "width": coords['width'],
                "height": coords['height']
            }
            
            screenshot = self.sct.grab(monitor)
            img_array = np.array(screenshot)
            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_BGRA2BGR)
            
            return img_bgr
            
        except Exception:
            if self.sct:
                try:
                    self.sct.close()
                except:
                    pass
                self.sct = None
            return None
    
    def capture_window(self, window):
        """Main capture method"""
        try:
            if self.sct is None:
                self.sct = mss.mss()
            
            # Try direct capture first
            direct_result = self.capture_window_direct(window)
            if direct_result is not None:
                return direct_result
            
            # Fall back to screen capture
            return self.capture_window_screen(window)
            
        except Exception:
            if self.sct:
                try:
                    self.sct.close()
                except:
                    pass
                self.sct = None
            return None
    
    def window_exists(self, target_window):
        """Check if window still exists"""
        try:
            _ = target_window.left
            _ = target_window.top
            _ = target_window.width
            _ = target_window.height
            return True
        except:
            return False
    
    def start_mirroring(self, window_title):
        """Start mirroring the specified window"""
        windows = self.list_windows()
        target_window = None
        
        for window_info in windows:
            if window_info['title'] == window_title:
                target_window = window_info['window']
                break
        
        if not target_window:
            print(f"Window '{window_title}' not found!")
            return
        
        self.target_window = target_window
        self.hwnd = self.find_window_handle(target_window)
        self.running = True
        
        # Update frame rate based on target FPS
        self.update_interval = 1.0 / self.target_fps
        
        print(f"\nStarting Window Mirror...")
        print(f"Window: {window_title}")
        print(f"Target FPS: {self.target_fps}")
        print(f"Exclude title bar: {self.exclude_title_bar}")
        
        coords = self.get_capture_coordinates(target_window)
        print(f"Capture size: {coords['width']}x{coords['height']}")
        print("Press 'q' or close mirror window to stop\n")
        
        self.start_mirror_window()
    
    def start_mirror_window(self):
        """Create and start the Tkinter mirror window"""
        self.mirror_window = MirrorWindow(self)
        self.mirror_window.start()
    
    def capture_loop(self):
        """Continuous capture loop"""
        frame_count = 0
        last_time = time.time()
        
        while self.capture_running:
            try:
                if not self.window_exists(self.target_window):
                    print("Target window closed!")
                    break
                
                frame = self.capture_window(self.target_window)
                
                if frame is not None:
                    try:
                        self.frame_queue.put_nowait(frame)
                    except queue.Full:
                        try:
                            self.frame_queue.get_nowait()
                            self.frame_queue.put_nowait(frame)
                        except queue.Empty:
                            pass
                    
                    frame_count += 1
                    if frame_count % 120 == 0:
                        current_time = time.time()
                        actual_fps = 120 / (current_time - last_time)
                        print(f"Running at {actual_fps:.0f} FPS")
                        last_time = current_time
                
                time.sleep(self.update_interval)
                
            except Exception:
                time.sleep(0.01)
                continue
    
    def stop_mirroring(self):
        """Stop the mirroring process"""
        self.capture_running = False
        self.running = False
        
        if self.capture_thread and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=1.0)
        
        if self.sct:
            try:
                self.sct.close()
            except:
                pass
        
        print("Mirroring stopped")

class MirrorWindow:
    def __init__(self, mirror):
        self.mirror = mirror
        self.root = None
        self.canvas = None
        self.is_running = False
        
    def start(self):
        """Start the mirror window"""
        self.root = tk.Toplevel()
        self.root.title("Window Mirror")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        coords = self.mirror.get_capture_coordinates(self.mirror.target_window)
        self.root.geometry(f"{coords['width']}x{coords['height']}")
        
        self.canvas = tk.Canvas(self.root, bg='black', 
                               width=coords['width'], 
                               height=coords['height'],
                               highlightthickness=0,
                               bd=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        self.root.bind('<KeyPress-q>', self.on_key_q)
        self.root.focus_set()
        
        self.is_running = True
        
        self.mirror.capture_running = True
        self.mirror.capture_thread = threading.Thread(target=self.mirror.capture_loop, daemon=True)
        self.mirror.capture_thread.start()
        
        self.update_display()
        self.root.mainloop()
    
    def update_display(self):
        """Update the display with new frames"""
        if not self.is_running:
            return
            
        try:
            frame = None
            try:
                while not self.mirror.frame_queue.empty():
                    frame = self.mirror.frame_queue.get_nowait()
            except queue.Empty:
                pass
            
            if frame is not None:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(frame_rgb)
                
                canvas_width = self.canvas.winfo_width()
                canvas_height = self.canvas.winfo_height()
                
                if canvas_width > 1 and canvas_height > 1:
                    pil_image = pil_image.resize((canvas_width, canvas_height), Image.Resampling.LANCZOS)
                
                photo = ImageTk.PhotoImage(pil_image)
                
                self.canvas.delete("all")
                self.canvas.create_image(0, 0, image=photo, anchor=tk.NW)
                self.canvas.image = photo
        
        except Exception:
            pass
        
        if self.is_running:
            self.root.after(16, self.update_display)
    
    def on_key_q(self, event):
        """Handle 'q' key press"""
        self.close()
    
    def on_close(self):
        """Handle window close"""
        self.close()
    
    def close(self):
        """Close the mirror window"""
        self.is_running = False
        self.mirror.stop_mirroring()
        if self.root:
            self.root.destroy()

class WindowSelectorGUI:
    def __init__(self):
        self.mirror = WindowMirror()
        self.root = tk.Tk()
        self.root.title("Window Mirror")
        self.root.geometry("800x600")
        
        self.setup_gui()
        self.refresh_windows()
    
    def setup_gui(self):
        """Setup GUI"""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        title_label = ttk.Label(main_frame, text="Window Mirror - Select Window:", 
                               font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 15), sticky=tk.W)
        
        list_frame = ttk.Frame(main_frame)
        list_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.window_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, 
                                        height=15, font=("Consolas", 10))
        self.window_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.window_listbox.yview)
        
        settings_frame = ttk.LabelFrame(main_frame, text="Settings", padding="10")
        settings_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        self.exclude_title_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="Exclude title bar (content only)", 
                       variable=self.exclude_title_var).pack(anchor=tk.W, pady=5)
        
        fps_frame = ttk.Frame(settings_frame)
        fps_frame.pack(anchor=tk.W, pady=10)
        
        ttk.Label(fps_frame, text="Target FPS:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        
        self.fps_var = tk.StringVar(value="60")
        fps_spinbox = ttk.Spinbox(fps_frame, from_=10, to=240, increment=10, 
                                 width=6, textvariable=self.fps_var)
        fps_spinbox.pack(side=tk.LEFT, padx=(5, 0))
        
        ttk.Label(fps_frame, text="fps").pack(side=tk.LEFT, padx=(5, 0))
        
        fps_buttons_frame = ttk.Frame(fps_frame)
        fps_buttons_frame.pack(side=tk.LEFT, padx=(15, 0))
        
        ttk.Button(fps_buttons_frame, text="60", width=5,
                  command=lambda: self.fps_var.set("60")).pack(side=tk.LEFT, padx=2)
        ttk.Button(fps_buttons_frame, text="120", width=5,
                  command=lambda: self.fps_var.set("120")).pack(side=tk.LEFT, padx=2)
        ttk.Button(fps_buttons_frame, text="144", width=5,
                  command=lambda: self.fps_var.set("144")).pack(side=tk.LEFT, padx=2)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        ttk.Button(button_frame, text="Refresh List", 
                  command=self.refresh_windows).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="Start Mirroring", 
                  command=self.start_mirroring).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="Exit", 
                  command=self.root.quit).pack(side=tk.RIGHT)
        
        instructions = ttk.Label(main_frame, 
                               text="Select a window and click 'Start Mirroring'. The mirror will capture the window content "
                                   "without interrupting your workflow. Press 'q' in the mirror window or close it to stop.",
                               wraplength=650, justify=tk.LEFT, foreground="blue")
        instructions.grid(row=4, column=0, columnspan=2, pady=(15, 0), sticky=tk.W)
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
    
    def refresh_windows(self):
        """Refresh window list"""
        self.window_listbox.delete(0, tk.END)
        self.windows = self.mirror.list_windows()
        
        for i, window_info in enumerate(self.windows):
            title = window_info['title']
            if len(title) > 85:
                title = title[:82] + "..."
            self.window_listbox.insert(tk.END, f"{i+1:2d}. {title}")
    
    def start_mirroring(self):
        """Start mirroring"""
        selection = self.window_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a window to mirror!")
            return
        
        index = selection[0]
        window_title = self.windows[index]['title']
        
        self.mirror.exclude_title_bar = self.exclude_title_var.get()
        
        try:
            fps = int(self.fps_var.get())
            self.mirror.target_fps = max(10, min(240, fps))
        except ValueError:
            self.mirror.target_fps = 60
        
        mirror_thread = threading.Thread(
            target=self.mirror.start_mirroring, 
            args=(window_title,), 
            daemon=True
        )
        mirror_thread.start()
    
    def run(self):
        """Run GUI"""
        self.root.mainloop()

def main():
    """Main function"""
    try:
        app = WindowSelectorGUI()
        app.run()
    except KeyboardInterrupt:
        print("\nProgram interrupted")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
