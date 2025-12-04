; ========================================
; FINCAFACIL - INSTALADOR WINDOWS
; Script de Inno Setup 6.x
; ========================================

#define MyAppName "FincaFacil"
#define MyAppVersion "1.0"
#define MyAppPublisher "FincaFacil Development Team"
#define MyAppURL "https://github.com/juanmora97B/FincaFacil"
#define MyAppExeName "FincaFacil.exe"

[Setup]
; ========================================
; INFORMACIÓN BÁSICA
; ========================================
AppId={{FincaFacil-2024-Management-System}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; ========================================
; DIRECTORIOS
; ========================================
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes

; ========================================
; ARCHIVOS DE SALIDA
; ========================================
OutputDir=installer
OutputBaseFilename=FincaFacil_Setup_v{#MyAppVersion}
SetupIconFile=assets\Logo.ico
Compression=lzma2/max
SolidCompression=yes

; ========================================
; INTERFAZ DE USUARIO
; ========================================
WizardStyle=modern
WizardSizePercent=120
ShowLanguageDialog=no
LanguageDetectionMethod=none

; ========================================
; PRIVILEGIOS Y COMPATIBILIDAD
; ========================================
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

; ========================================
; CONFIGURACIONES ADICIONALES
; ========================================
AllowNoIcons=yes
DisableDirPage=no
DisableReadyPage=no
AlwaysShowDirOnReadyPage=yes
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallFilesDir={app}\uninst

; ========================================
; LICENCIA Y DOCUMENTACIÓN
; ========================================
LicenseFile=LICENSE.txt
InfoBeforeFile=docs\INSTALACION.txt
InfoAfterFile=docs\PRIMER_USO.txt

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; ========================================
; ARCHIVOS PRINCIPALES
; ========================================
Source: "dist\FincaFacil\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\FincaFacil\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; ========================================
; DOCUMENTACIÓN
; ========================================
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "docs\*"; DestDir: "{app}\docs"; Flags: ignoreversion recursesubdirs

; ========================================
; ARCHIVOS DE CONFIGURACIÓN
; ========================================
Source: "config.py"; DestDir: "{app}"; Flags: ignoreversion

[Dirs]
; ========================================
; DIRECTORIOS CON PERMISOS DE ESCRITURA
; ========================================
Name: "{app}\database"; Permissions: users-modify
Name: "{app}\backup"; Permissions: users-modify
Name: "{app}\exports"; Permissions: users-modify
Name: "{app}\logs"; Permissions: users-modify
Name: "{app}\uploads"; Permissions: users-modify
Name: "{app}\config"; Permissions: users-modify

[Icons]
; ========================================
; ACCESOS DIRECTOS
; ========================================
; Menú inicio
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\assets\Logo.ico"
Name: "{group}\Manual de Usuario"; Filename: "{app}\docs\Manual_Usuario_FincaFacil.md"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"

; Escritorio (opcional)
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\assets\Logo.ico"; Tasks: desktopicon

; Barra de inicio rápido (opcional)
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
; ========================================
; EJECUTAR DESPUÉS DE INSTALACIÓN
; ========================================
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; ========================================
; ARCHIVOS A ELIMINAR EN DESINSTALACIÓN
; ========================================
Type: files; Name: "{app}\logs\*.log"
Type: files; Name: "{app}\logs\*.log.*"
Type: filesandordirs; Name: "{app}\__pycache__"
Type: filesandordirs; Name: "{app}\*\__pycache__"

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
var
  ConfigDir: String;
  DatabaseDir: String;
begin
  if CurStep = ssPostInstall then
  begin
    ConfigDir := ExpandConstant('{app}\config');
    ForceDirectories(ConfigDir);
    DatabaseDir := ExpandConstant('{app}\database');
    ForceDirectories(DatabaseDir);
  end;
end;

[Messages]
; ========================================
; MENSAJES PERSONALIZADOS EN ESPAÑOL
; ========================================
WelcomeLabel1=Bienvenido al Asistente de Instalación de [name]
WelcomeLabel2=Este programa instalará [name/ver] en su computadora.%n%nSe recomienda cerrar todas las aplicaciones antes de continuar.
FinishedLabel=La instalación de [name] se ha completado exitosamente.%n%nLa aplicación está lista para usarse.
