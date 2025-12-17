from edrlog import EDR_LOG
import platform, os
import ctypes

if os.name == 'nt' or platform.system() == 'Windows':
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32

    # CRITICAL FIX: Define 32/64-bit agnostic return types and arguments
    # c_void_p and c_size_t scale automatically between 4 and 8 bytes.
    kernel32.GlobalAlloc.restype = wintypes.HGLOBAL
    kernel32.GlobalAlloc.argtypes = [wintypes.UINT, ctypes.c_size_t]

    kernel32.GlobalLock.restype = ctypes.c_void_p
    kernel32.GlobalLock.argtypes = [wintypes.HGLOBAL]

    kernel32.GlobalUnlock.argtypes = [wintypes.HGLOBAL]

    user32.GetClipboardData.restype = wintypes.HANDLE
    user32.GetClipboardData.argtypes = [wintypes.UINT]

    user32.SetClipboardData.restype = wintypes.HANDLE
    user32.SetClipboardData.argtypes = [wintypes.UINT, wintypes.HANDLE]

    # Ensures memmove handles lengths as 64-bit on 64-bit systems
    ctypes.memmove.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t]

def __winGetClipboard():
    CF_UNICODETEXT = 13
    if not user32.OpenClipboard(0):
        return None
    try:
        handle = user32.GetClipboardData(CF_UNICODETEXT)
        if not handle:
            return None
        p_contents = kernel32.GlobalLock(handle)
        if not p_contents:
            return None
        
        # Interpret pointer as a Unicode string directly
        data = ctypes.c_wchar_p(p_contents).value
        kernel32.GlobalUnlock(handle)
        return data
    except Exception as e:
        EDR_LOG.exception(f"Windows GetClipboard failed: {e}")
        return None
    finally:
        user32.CloseClipboard()

def __winSetClipboard(text):
    # Use Unicode (UTF-16 LE) for native Windows compatibility
    text_bytes = str(text).encode('utf-16-le')
    text_len = len(text_bytes)

    GMEM_MOVEABLE = 0x0002
    CF_UNICODETEXT = 13

    if not user32.OpenClipboard(0):
        return False
    try:
        user32.EmptyClipboard()
        # Allocate +2 bytes for the Unicode null terminator
        h_mem = kernel32.GlobalAlloc(GMEM_MOVEABLE, text_len + 2)
        p_data = kernel32.GlobalLock(h_mem)
        
        if p_data:
            try:
                ctypes.memmove(p_data, text_bytes, text_len)
                ctypes.memset(p_data + text_len, 0, 2) # Null terminate
            except Exception as e:
                EDR_LOG.exception(f"Clipboard memmove failed: {e}")
            finally:
                kernel32.GlobalUnlock(h_mem)

        if not user32.SetClipboardData(CF_UNICODETEXT, h_mem):
            kernel32.GlobalFree(h_mem)
            return False
        return True
    except Exception as e:
        EDR_LOG.exception(f"Windows SetClipboard failed: {e}")
        return False
    finally:
        user32.CloseClipboard()

def __macSetClipboard(text):
    try:
        text = str(text)
        tool = 'pbcopy' if platform.system() == 'Darwin' else 'xclip -selection clipboard'
        outf = os.popen(tool, 'w')
        outf.write(text)
        outf.close()
    except Exception as e:
        EDR_LOG.exception(f"Mac/Unix SetClipboard failed: {e}")

def __macGetClipboard():
    try:
        tool = 'pbpaste' if platform.system() == 'Darwin' else 'xclip -selection clipboard -o'
        outf = os.popen(tool, 'r')
        content = outf.read()
        outf.close()
        return content
    except Exception as e:
        EDR_LOG.exception(f"Mac/Unix GetClipboard failed: {e}")
        return ""

if os.name == 'nt' or platform.system() == 'Windows':
    import ctypes
    clipboard_get = __winGetClipboard
    clipboard_set = __winSetClipboard
elif os.name == 'mac' or platform.system() == 'Darwin':
    clipboard_get = __macGetClipboard
    clipboard_set = __macSetClipboard
elif os.name == 'linux' or platform.system() == 'Linux':
    clipboard_get = __macGetClipboard
    clipboard_set = __macSetClipboard
else:
    clipboard_get = lambda: None
    clipboard_set = lambda x: None

copy = clipboard_set
paste = clipboard_get
