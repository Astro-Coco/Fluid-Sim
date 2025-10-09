# wallpaper.py  (Windows only)
import ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32

FindWindowW        = user32.FindWindowW
FindWindowExW      = user32.FindWindowExW
EnumWindows        = user32.EnumWindows
GetClassNameW      = user32.GetClassNameW
SendMessageTimeoutW= user32.SendMessageTimeoutW
SetParent          = user32.SetParent
SetWindowLongW     = user32.SetWindowLongW
GetWindowLongW     = user32.GetWindowLongW
SetWindowPos       = user32.SetWindowPos
ShowWindow         = user32.ShowWindow

# constants
GWL_STYLE   = -16
WS_CHILD            = 0x40000000
WS_VISIBLE          = 0x10000000
WS_CLIPSIBLINGS     = 0x04000000
WS_CLIPCHILDREN     = 0x02000000
WS_OVERLAPPEDWINDOW = 0x00CF0000

SWP_NOZORDER    = 0x0004
SWP_FRAMECHANGED= 0x0020
SW_SHOW         = 5

SMTO_NORMAL     = 0x0000
MSG_CREATE_WORKERW = 0x052C  # undocumented, used by Explorer

# WNDENUMPROC prototype: BOOL CALLBACK EnumWindowsProc(HWND hwnd, LPARAM lParam)
EnumWindowsProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

def _get_workerw():
    """Return the 'wallpaper' WorkerW handle (behind desktop icons)."""
    # 1) Ask Explorer to create a WorkerW behind icons
    progman = FindWindowW("Progman", None)
    if progman:
        _ = wintypes.DWORD()
        SendMessageTimeoutW(progman, MSG_CREATE_WORKERW, 0, 0, SMTO_NORMAL, 1000, ctypes.byref(_))

    # 2) Find the WorkerW that *contains* the icons (SHELLDLL_DefView)
    workerw_with_icons = []
    def enum_cb(hwnd, lparam):
        cls = ctypes.create_unicode_buffer(256)
        GetClassNameW(hwnd, cls, 256)
        if cls.value == "WorkerW":
            shell = FindWindowExW(hwnd, 0, "SHELLDLL_DefView", None)
            if shell:
                workerw_with_icons.append(hwnd)
        return True  # keep enumerating

    EnumWindows(EnumWindowsProc(enum_cb), 0)

    # 3) The wallpaper WorkerW is the next WorkerW sibling after the one with icons
    if workerw_with_icons:
        wallpaper_workerw = FindWindowExW(None, workerw_with_icons[0], "WorkerW", None)
        if wallpaper_workerw:
            return wallpaper_workerw

    # Fallbacks: sometimes Progman directly hosts the DefView; pick any WorkerW
    # that does NOT contain SHELLDLL_DefView.
    candidates = []
    def enum_cb2(hwnd, lparam):
        cls = ctypes.create_unicode_buffer(256)
        GetClassNameW(hwnd, cls, 256)
        if cls.value == "WorkerW":
            shell = FindWindowExW(hwnd, 0, "SHELLDLL_DefView", None)
            if not shell:
                candidates.append(hwnd)
        return True

    EnumWindows(EnumWindowsProc(enum_cb2), 0)
    return candidates[0] if candidates else None

def attach_window_to_wallpaper(hwnd, width, height):
    """Reparent an existing SDL/Pygame window (HWND) to the WorkerW and make it borderless."""
    workerw = _get_workerw()
    if not workerw:
        raise RuntimeError("Could not find WorkerW")

    style = GetWindowLongW(hwnd, GWL_STYLE)
    # remove normal frame; make it a child of WorkerW and visible
    style &= ~WS_OVERLAPPEDWINDOW
    style |= (WS_CHILD | WS_VISIBLE | WS_CLIPSIBLINGS | WS_CLIPCHILDREN)
    SetWindowLongW(hwnd, GWL_STYLE, style)

    # reparent + resize to cover desktop
    SetParent(hwnd, workerw)
    SetWindowPos(hwnd, 0, 0, 0, width, height, SWP_NOZORDER | SWP_FRAMECHANGED)
    ShowWindow(hwnd, SW_SHOW)
