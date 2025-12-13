# Firewall Fix for Network Access

## Problem
The frontend server is running correctly on `0.0.0.0:8501` and responds to localhost, but network access times out. This is typically a **Windows Firewall** issue.

## Solution: Add Firewall Rule

### Option 1: Using PowerShell (as Administrator)
```powershell
netsh advfirewall firewall add rule name="Streamlit Frontend Port 8501" dir=in action=allow protocol=TCP localport=8501
```

### Option 2: Using Windows Firewall GUI
1. Open **Windows Defender Firewall with Advanced Security**
2. Click **Inbound Rules** → **New Rule**
3. Select **Port** → **Next**
4. Select **TCP** → Enter **8501** in "Specific local ports" → **Next**
5. Select **Allow the connection** → **Next**
6. Check all profiles (Domain, Private, Public) → **Next**
7. Name it: **Streamlit Frontend Port 8501** → **Finish**

### Option 3: Quick PowerShell Command (Run as Admin)
Right-click PowerShell → **Run as Administrator**, then run:
```powershell
netsh advfirewall firewall add rule name="Streamlit Frontend Port 8501" dir=in action=allow protocol=TCP localport=8501
```

## Verify Rule
```powershell
netsh advfirewall firewall show rule name="Streamlit Frontend Port 8501"
```

## Also Add for Backend (Port 8000)
```powershell
netsh advfirewall firewall add rule name="FastAPI Backend Port 8000" dir=in action=allow protocol=TCP localport=8000
```

## After Adding Rule
- The frontend should be accessible from network at: `http://192.168.10.150:8501`
- The backend should be accessible at: `http://192.168.10.150:8000`


