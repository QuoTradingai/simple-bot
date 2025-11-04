# Building QuoTrading AI Windows EXE

## 🎯 Goal
Create a standalone Windows executable that customers can double-click to run.
**NO Python installation required for customers!**

## 📋 Prerequisites (Developer Only)

1. **Install PyInstaller:**
   ```powershell
   pip install pyinstaller
   ```

2. **Create Icon (Optional but recommended):**
   - Create `icon.ico` (256x256 or 512x512 recommended)
   - Place in project root
   - Use tool like: https://www.icoconverter.com/

## 🔨 Build Process

### Step 1: Build Customer Package First
```powershell
python build_customer_version.py
```

This creates: `../simple-bot-customer/`

### Step 2: Navigate to Customer Folder
```powershell
cd ..\simple-bot-customer
```

### Step 3: Build EXE
```powershell
pyinstaller build_exe.spec
```

### Step 4: Find Your EXE
```
simple-bot-customer/
├── dist/
│   └── QuoTrading_AI.exe  ← THIS IS IT! (30-50 MB)
```

## 📦 What Customers Get

**Single file:** `QuoTrading_AI.exe`

That's it! They:
1. Download `QuoTrading_AI.exe`
2. Double-click it
3. Enter credentials
4. Start trading

**No Python, no dependencies, no setup!**

## 🚀 Distribution

### Option 1: Direct Download
- Upload `QuoTrading_AI.exe` to your server
- Customer downloads and runs

### Option 2: Installer (Professional)
- Use Inno Setup or NSIS to create installer
- Adds start menu shortcuts
- Professional uninstall

### Option 3: Auto-Update
- Host on server with version check
- Bot checks for updates on startup
- One-click update

## 🔒 Security Notes

1. **Code Signing (Recommended):**
   - Get a code signing certificate ($200-400/year)
   - Sign the EXE to avoid "Unknown Publisher" warnings
   - Customers trust it more

2. **License Validation:**
   - EXE calls your API to validate license key
   - Can disable stolen/shared licenses remotely

3. **Anti-Virus:**
   - Some AV may flag unsigned EXE
   - Code signing solves this
   - Submit to VirusTotal for whitelisting

## 📊 EXE Size

- **Minimal:** ~30 MB (just bot)
- **Full:** ~50 MB (with all dependencies)
- Compresses to ~15 MB with UPX

## 🛠️ Testing

Before releasing:
```powershell
# Test on clean Windows VM (no Python)
.\dist\QuoTrading_AI.exe

# Should open GUI immediately
```

## 🎨 Customization

Edit `build_exe.spec`:
- Change icon: `icon='your_icon.ico'`
- Change name: `name='YourBotName'`
- Add splash screen: Add splash parameter
- Console mode: `console=True` (for debugging)

## 📝 Version Updates

1. Edit `version_info.txt` (change version numbers)
2. Rebuild: `pyinstaller build_exe.spec`
3. New EXE in `dist/`

## ⚠️ Common Issues

**"Failed to execute script":**
- Check all imports in launcher
- Test with `console=True` first to see errors

**"DLL not found":**
- Add to `hiddenimports` in spec file

**EXE too large:**
- Enable UPX: `upx=True`
- Exclude unused packages in `excludes`

## 🎯 Final Customer Experience

**What they see:**
1. Download `QuoTrading_AI.exe` (one file)
2. Double-click
3. Beautiful GUI opens (no black console)
4. Enter license key + TopStep credentials
5. Click START BOT
6. Done!

**Professional, clean, no technical knowledge needed!**
