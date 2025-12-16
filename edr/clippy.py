import EDR_LOG from edrlog
import platform, os
import ctypes

def __winGetClipboard():
    ctypes.windll.user32.OpenClipboard(0)
    pcontents = ctypes.windll.user32.GetClipboardData(1) # 1 is CF_TEXT
    data = ctypes.c_char_p(pcontents).value
    #ctypes.windll.kernel32.GlobalUnlock(pcontents)
    ctypes.windll.user32.CloseClipboard()
    return data

def __winSetClipboard(text):
    text_bytes = bytes(str(text), 'utf-8')
    text_len = len(text_bytes)

    GMEM_DDESHARE = 0x2000
    CF_TEXT = 1

    ctypes.windll.user32.OpenClipboard(0)
    ctypes.windll.user32.EmptyClipboard()

    hCd = ctypes.windll.kernel32.GlobalAlloc(GMEM_DDESHARE, text_len + 1)
    pchData = ctypes.windll.kernel32.GlobalLock(hCd)
    
    # 1. Get a pointer type that can be written to
    # 2. Use ctypes.memmove to copy the raw bytes (including the null terminator, which is added after the copy)
    buffer = (ctypes.c_char * (text_len + 1)).from_address(pchData)
    
    try:
        # Copy the bytes into the buffer
        ctypes.memmove(buffer, text_bytes, text_len)
    except Exception as e:
        EDR_LOG.log(e, level=EDR_LOG.ERROR)
    
    # Manually add the null terminator
    buffer[text_len] = b'\x00'

    ctypes.windll.kernel32.GlobalUnlock(hCd)
    ctypes.windll.user32.SetClipboardData(CF_TEXT, hCd)
    ctypes.windll.user32.CloseClipboard()

def __macSetClipboard(text):
    text = str(text)
    outf = os.popen('pbcopy', 'w')
    outf.write(text)
    outf.close()

def __macGetClipboard():
    outf = os.popen('pbpaste', 'r')
    content = outf.read()
    outf.close()
    return content

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
copy = clipboard_set
paste = clipboard_get
