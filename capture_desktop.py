"""Capture the actual Windows desktop to PNG for layout verification."""
import ctypes
from ctypes import wintypes
import os
import struct
import zlib

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

# Capture metrics and pixels in the same physical coordinate space. Without
# this, a 125%-scaled 2048x1152 desktop is mislabeled as 1536x863 and the PNG
# appears to show windows hundreds of pixels lower than they really are.
try:
    user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
except Exception:
    user32.SetProcessDPIAware()
SM_XVIRTUALSCREEN = 76
SM_YVIRTUALSCREEN = 77
SM_CXVIRTUALSCREEN = 78
SM_CYVIRTUALSCREEN = 79
SRCCOPY = 0x00CC0020
CAPTUREBLT = 0x40000000
DIB_RGB_COLORS = 0


class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [("biSize", wintypes.DWORD), ("biWidth", wintypes.LONG),
                ("biHeight", wintypes.LONG), ("biPlanes", wintypes.WORD),
                ("biBitCount", wintypes.WORD), ("biCompression", wintypes.DWORD),
                ("biSizeImage", wintypes.DWORD), ("biXPelsPerMeter", wintypes.LONG),
                ("biYPelsPerMeter", wintypes.LONG), ("biClrUsed", wintypes.DWORD),
                ("biClrImportant", wintypes.DWORD)]


def chunk(kind: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)


def capture(path: str) -> None:
    x = user32.GetSystemMetrics(SM_XVIRTUALSCREEN)
    y = user32.GetSystemMetrics(SM_YVIRTUALSCREEN)
    width = user32.GetSystemMetrics(SM_CXVIRTUALSCREEN)
    height = user32.GetSystemMetrics(SM_CYVIRTUALSCREEN)
    src = user32.GetDC(0)
    mem = gdi32.CreateCompatibleDC(src)
    bitmap = gdi32.CreateCompatibleBitmap(src, width, height)
    old = gdi32.SelectObject(mem, bitmap)
    gdi32.BitBlt(mem, 0, 0, width, height, src, x, y, SRCCOPY | CAPTUREBLT)
    header = BITMAPINFOHEADER()
    header.biSize = ctypes.sizeof(BITMAPINFOHEADER)
    header.biWidth = width
    header.biHeight = -height
    header.biPlanes = 1
    header.biBitCount = 32
    size = width * height * 4
    pixels = ctypes.create_string_buffer(size)
    gdi32.GetDIBits(mem, bitmap, 0, height, pixels, ctypes.byref(header), DIB_RGB_COLORS)
    raw = pixels.raw
    scanlines = bytearray()
    for row in range(height):
        scanlines.append(0)
        start = row * width * 4
        for col in range(width):
            i = start + col * 4
            scanlines.extend((raw[i + 2], raw[i + 1], raw[i], 255))
    with open(path, "wb") as file:
        file.write(b"\x89PNG\r\n\x1a\n")
        file.write(chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)))
        file.write(chunk(b"IDAT", zlib.compress(bytes(scanlines), 7)))
        file.write(chunk(b"IEND", b""))
    gdi32.SelectObject(mem, old)
    gdi32.DeleteObject(bitmap)
    gdi32.DeleteDC(mem)
    user32.ReleaseDC(0, src)
    print(f"{width}x{height} -> {path}")


if __name__ == "__main__":
    capture(os.path.join(os.path.dirname(__file__), "full-desktop-validation.png"))
