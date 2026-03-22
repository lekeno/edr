from edr.core.edrlog import EDR_LOG
import platform
import os
import ctypes
from ctypes import wintypes
import subprocess


# Setup Windows ctypes if necessary
if os.name == 'nt' or platform.system() == 'Windows':
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32

    # CRITICAL FIX: Define 32/64-bit agnostic return types and arguments
    kernel32.GlobalAlloc.restype = wintypes.HGLOBAL
    kernel32.GlobalAlloc.argtypes = [wintypes.UINT, ctypes.c_size_t]

    kernel32.GlobalLock.restype = ctypes.c_void_p
    kernel32.GlobalLock.argtypes = [wintypes.HGLOBAL]

    kernel32.GlobalUnlock.argtypes = [wintypes.HGLOBAL]

    user32.GetClipboardData.restype = wintypes.HANDLE
    user32.GetClipboardData.argtypes = [wintypes.UINT]

    user32.SetClipboardData.restype = wintypes.HANDLE
    user32.SetClipboardData.argtypes = [wintypes.UINT, wintypes.HANDLE]

    ctypes.memmove.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t]


def _win_get_clipboard():
    """Retrieve text from the Windows clipboard.

    Returns:
        str: clipboard content or None if failed.
    """
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


def _win_set_clipboard(text):
    """Set text to the Windows clipboard.

    Args:
        text (str): Content to copy to clipboard.

    Returns:
        bool: True if successful, False otherwise.
    """
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
                ctypes.memset(p_data + text_len, 0, 2)  # Null terminate
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


def _unix_set_clipboard(text):
    """Set text to the Unix/Mac clipboard.

    Args:
        text (str): Content to copy to clipboard.
    """
    try:
        text = str(text)
        if platform.system() == 'Darwin':
            subprocess.run(['pbcopy'], input=text, check=True, text=True)
        else:
            subprocess.run(['xclip', '-selection', 'clipboard'], input=text, check=True, text=True)
    except Exception as e:
        EDR_LOG.exception(f"Mac/Unix SetClipboard failed: {e}")


def _unix_get_clipboard():
    """Retrieve text from the Unix/Mac clipboard.

    Returns:
        str: clipboard content or None if failed.
    """
    try:
        if platform.system() == 'Darwin':
            result = subprocess.run(['pbpaste'], capture_output=True, check=True, text=True)
        else:
            result = subprocess.run(['xclip', '-selection', 'clipboard', '-o'], capture_output=True, check=True, text=True)
        return result.stdout
    except Exception as e:
        EDR_LOG.exception(f"Mac/Unix GetClipboard failed: {e}")
        return None


# Platform detection and assignment
if os.name == 'nt' or platform.system() == 'Windows':
    clipboard_get = _win_get_clipboard
    clipboard_set = _win_set_clipboard
elif platform.system() in ['Darwin', 'Linux']:
    clipboard_get = _unix_get_clipboard
    clipboard_set = _unix_set_clipboard
else:
    clipboard_get = lambda: None
    clipboard_set = lambda x: None

# Exported aliases
copy = clipboard_set
paste = clipboard_get
