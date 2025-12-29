; Script de instalación para FincaFácil usando Inno Setup
; Versión 6.3+
; Uso: Compilar con Inno Setup Compiler

#define MyAppName "FincaFácil"
#define MyAppVersion "2.0"
#define MyAppPublisher "FincaFácil Development"
#define MyAppURL "https://www.fincafacil.com"
#define MyAppSupportEmail "jfburitica97@gmail.com"
#define MyAppSupportPhone "3013869653"
#define MyAppExeName "FincaFacil.exe"

[Setup]
; Información básica
AppId={{8B7D4E5C-9F2A-4D1E-B8C3-7A6F5E8D9C2B}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL=mailto:{#MyAppSupportEmail}
AppUpdatesURL={#MyAppURL}/descargas
; Soporte: {#MyAppSupportEmail} | Tel: {#MyAppSupportPhone}

; Configuración de instalación
; Instalación per-user para evitar requerir administrador y alinear con datos en AppData
DefaultDirName={localappdata}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=docs\LICENCIA.txt
InfoBeforeFile=docs\ANTES_DE_INSTALAR.txt
InfoAfterFile=docs\DESPUES_DE_INSTALAR.txt

; Configuración de compilación
OutputDir=dist
OutputBaseFilename=FincaFacil_Installer_v2.0
SetupIconFile=src\assets\Logo.ico
Compression=lzma
SolidCompression=yes

; Requisitos del sistema
MinVersion=10.0.0
; Identificador recomendado: x64compatible (evita advertencia de x64)
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest

; Firma digital (opcional)
; SignTool=signtool

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1,10.0

[Files]
; Ejecutable único (onefile)
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; Documentación
Source: "docs\*.txt"; DestDir: "{app}\docs"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion isreadme

; Base de datos inicial
Source: "src\database\fincafacil.db"; DestDir: "{app}\database"; Flags: ignoreversion onlyifdoesntexist

; Assets (iconos e imágenes)
Source: "src\assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs

; Configuración inicial (se crea en runtime)
; Source: "config\*.json"; DestDir: "{app}\config"; Flags: ignoreversion onlyifdoesntexist

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\assets\Logo.ico"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\assets\Logo.ico"; Tasks: desktopicon
Name: "{userstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}\database"
Type: filesandordirs; Name: "{app}\config"
Type: files; Name: "{app}\fincafacil.db"

[Code]
// Código personalizado (opcional)

[Messages]
spanish.FinishedLabelNoIcons=Se ha completado la instalación de %1. Para ejecutar la aplicación, use el acceso directo creado.
spanish.FinishedRestartLabel=Para completar la instalación de %1, la computadora debe reiniciarse. ¿Desea reiniciar ahora?
spanish.FinishedRestartMessage=Para completar la instalación de %1, la computadora debe reiniciarse.
spanish.ConfirmUninstall=¿Está seguro de que desea eliminar completamente %1 y sus componentes?
spanish.UninstalledAll=%1 ha sido removido exitosamente de su equipo.

english.FinishedLabelNoIcons=Installation of %1 has been completed. To execute the application, use the shortcut created.
english.FinishedRestartLabel=To complete the installation of %1, this computer must restart. Do you want to restart now?
english.FinishedRestartMessage=To complete the installation of %1, this computer must restart.
english.ConfirmUninstall=Are you sure you want to completely remove %1 and all its components?
english.UninstalledAll=%1 has been successfully removed from your computer.
