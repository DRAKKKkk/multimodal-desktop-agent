#include<iostream>
#include<windows.h>
using namespace std;

int main(){
    // ---- STEP 1: Size Pata Karna ----
    int screenWidth = GetSystemMetrics(SM_CXSCREEN);
    int screenHeight = GetSystemMetrics(SM_CYSCREEN);

   // ---- STEP 2: Blank Canvas Taiyar Karna ----
    HWND desktopWindowHandle = GetDesktopWindow();
    HDC screenDeviceContext = GetDC(desktopWindowHandle);
    HDC memoryDeviceContext = CreateCompatibleDC(screenDeviceContext);
    HBITMAP screeenshotBitmapCanvas = CreateCompatibleBitmap(screenDeviceContext, screenWidth, screenHeight);
    SelectObject(memoryDeviceContext, screeenshotBitmapCanvas);

    // ---- STEP 3: Screen ko Copy karna ----
    BitBlt(
        memoryDeviceContext,
        0, 0,
        screenWidth, screenHeight,
        screenDeviceContext,
        0, 0,
        SRCCOPY
    );

    // 4.1 Image ki details (Header) set karna
    BITMAPINFOHEADER bi;
    bi.biSize = sizeof(BITMAPINFOHEADER);
    bi.biWidth = screenWidth;
    bi. biHeight = -screenHeight;
    bi.biPlanes = 1;
    bi.biBitCount = 32;
    bi.biCompression = BI_RGB;
    bi.biSizeImage = 0;
    bi.biXPelsPerMeter = 0;
    bi.biYPelsPerMeter = 0;
    bi.biClrUsed = 0;
    bi.biClrImportant = 0;

    // 4.2 Memory allocate karna pixels ke liye
    DWORD bitmapPixelDataSize = ((screenWidth * bi.biBitCount + 31)/32)*4*screenHeight;
    HANDLE memoryHandleForPixels = GlobalAlloc(GHND, bitmapPixelDataSize);
    char* pixelDataArray = (char*)GlobalLock(memoryHandleForPixels);

    // 4.3 Canvas se saare pixels nikal kar array mein daalna
    GetDIBits(screenDeviceContext, screeenshotBitmapCanvas, 0, (UINT)screenHeight, pixelDataArray, (BITMAPINFO*)&bi, DIB_RGB_COLORS);
    
    // 4.4 Hard drive par ek nayi file create karna
    HANDLE outputFileHandle = CreateFileA("mine_screenshot.bmp", GENERIC_WRITE, 0, NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);

    // File ka ek aur chhota header jo computer ko batata hai ki ye "BMP" image hai
    BITMAPFILEHEADER bfh;
    DWORD totalFileSize = bitmapPixelDataSize + sizeof(BITMAPFILEHEADER) + sizeof(BITMAPINFOHEADER);
    bfh.bfOffBits = (DWORD)sizeof(BITMAPFILEHEADER) + (DWORD)sizeof(BITMAPINFOHEADER);
    bfh.bfSize = totalFileSize;
    bfh.bfType = 0x4D42;

    DWORD bytesWrittenToFile = 0;

    // 4.5 File ke andar data likhna (Pehle dono Headers, phir Pixels ka data)
    WriteFile(outputFileHandle, (LPSTR)&bfh, sizeof(BITMAPFILEHEADER), &bytesWrittenToFile, NULL);
    WriteFile(outputFileHandle, (LPSTR)&bi, sizeof(BITMAPINFOHEADER), &bytesWrittenToFile, NULL);
    WriteFile(outputFileHandle, (LPSTR)pixelDataArray, bitmapPixelDataSize, &bytesWrittenToFile, NULL);

    // Windows ka rule hai: Jo cheez aap memory mein banate hain, kaam khatam hone ke baad use mitaana zaroori hai, warna RAM bhar jayegi.
    // ---- STEP 5: Safai (Clean Up) taaki RAM free ho jaye ----
    CloseHandle(outputFileHandle);
    GlobalUnlock(memoryHandleForPixels);
    GlobalFree(memoryHandleForPixels);
    DeleteObject(screeenshotBitmapCanvas);
    DeleteDC(memoryDeviceContext);
    ReleaseDC(desktopWindowHandle, screenDeviceContext);

    return 0;
}
