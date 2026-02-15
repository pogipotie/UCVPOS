[Setup]
; Basic Information
AppName=DOUBLEA DRUGSTORE POS
AppVersion=1.0
AppPublisher=downstreamtech.net
AppPublisherURL=https://downstreamtech.net
AppSupportURL=https://downstreamtech.net
AppUpdatesURL=https://downstreamtech.net
 
; Installation Directory
DefaultDirName={autopf}\UCVPOS
DefaultGroupName=UCVPOS
DisableProgramGroupPage=yes

; Output Configuration
OutputDir=Installers
OutputBaseFilename=Update_Consumer_VPOS_Setup
SetupIconFile=assets\POS.ico
Compression=lzma2
SolidCompression=yes

; Branding & Docs
LicenseFile=assets\privacy_policy.txt
InfoBeforeFile=assets\developer_info.txt
WizardImageFile=assets\dst.bmp
WizardSmallImageFile=assets\dst_small.bmp

; Admin Privileges (Required for Program Files)
PrivilegesRequired=admin

; Uninstall Display Info
UninstallDisplayIcon={app}\PharmacyPOS.exe

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; The Main Executable
Source: "dist\PharmacyPOS.exe"; DestDir: "{app}"; Flags: ignoreversion

; Note: Since we are using --onefile PyInstaller mode, dependencies are bundled inside the EXE.
; If there were external config files or assets not bundled, they would be added here.

[Icons]
; Start Menu Shortcut
Name: "{group}\UCVPOS"; Filename: "{app}\PharmacyPOS.exe"
Name: "{group}\{cm:UninstallProgram,UCVPOS}"; Filename: "{uninstallexe}"

; Desktop Shortcut (Optional)
Name: "{autodesktop}\UCVPOS"; Filename: "{app}\PharmacyPOS.exe"; Tasks: desktopicon

[Run]
; Launch after install
Filename: "{app}\PharmacyPOS.exe"; Description: "{cm:LaunchProgram,UCVPOS}"; Flags: nowait postinstall skipifsilent
