[Setup]
AppName=AI Coders Proxy Fixer
AppVersion=2.1.0
AppPublisher=Vahid Valadi
AppPublisherURL=https://github.com/vahidvl/AI-Coders-Proxy-Fixer
DefaultDirName={autopf}\AI Coders Proxy Fixer
DisableProgramGroupPage=yes
OutputBaseFilename=AI_Coders_Proxy_Fixer_Setup
SetupIconFile=assets\app_icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\installer_source\AI_Coders_Proxy_Fixer\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "assets\app_icon.ico"; DestDir: "{app}\assets"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\AI Coders Proxy Fixer"; Filename: "{app}\AI_Coders_Proxy_Fixer.exe"; IconFilename: "{app}\assets\app_icon.ico"
Name: "{autodesktop}\AI Coders Proxy Fixer"; Filename: "{app}\AI_Coders_Proxy_Fixer.exe"; IconFilename: "{app}\assets\app_icon.ico"; Tasks: desktopicon

[Run]
Filename: "{app}\AI_Coders_Proxy_Fixer.exe"; Description: "{cm:LaunchProgram,AI Coders Proxy Fixer}"; Flags: nowait postinstall skipifsilent
