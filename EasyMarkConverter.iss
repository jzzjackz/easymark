[Setup]
; Application Information
AppName=EasyMark Converter
AppVersion=1.0.5
AppPublisher=rizzdev
AppPublisherURL=https://github.com/rizzdev
AppSupportURL=https://github.com/rizzdev
AppCopyright=Copyright (C) 2024 rizzdev
DefaultDirName={autopf}\EasyMark Converter
DefaultGroupName=EasyMark Converter
DisableProgramGroupPage=yes
LicenseFile=
OutputDir=installer
OutputBaseFilename=EasyMarkConverter-Setup
SetupIconFile=
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64

; UI Customization
WizardImageFile=
WizardSmallImageFile=
SetupLogging=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1

[Files]
; Main executable - installs as EasyMarkInterp.exe
Source: "dist\EasyMarkConverter.exe"; DestDir: "{app}"; DestName: "EasyMarkInterp.exe"; Flags: ignoreversion

[Registry]
; Add application directory to PATH for current user
Root: HKCU; Subkey: "Environment"; ValueType: expandsz; ValueName: "Path"; ValueData: "{olddata};{app}"; Check: NeedsAddPath('{app}'); Flags: preservestringtype

[UninstallDelete]
; Remove the batch file wrapper on uninstall
Type: files; Name: "{app}\eminterp.bat"

[Icons]
Name: "{group}\EasyMark Converter"; Filename: "{app}\EasyMarkInterp.exe"
Name: "{group}\{cm:UninstallProgram,EasyMark Converter}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\EasyMark Converter"; Filename: "{app}\EasyMarkInterp.exe"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\EasyMark Converter"; Filename: "{app}\EasyMarkInterp.exe"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\EasyMarkInterp.exe"; Description: "{cm:LaunchProgram,EasyMark Converter}"; Flags: nowait postinstall skipifsilent

[Code]
var
  RestartPage: TWizardPage;
  RestartNowButton: TButton;
  RestartLaterButton: TButton;
  InfoLabel: TLabel;

function NeedsAddPath(Param: string): boolean;
var
  OrigPath: string;
begin
  if not RegQueryStringValue(HKEY_CURRENT_USER,
    'Environment',
    'Path', OrigPath)
  then begin
    Result := True;
    exit;
  end;
  { look for the path with leading and trailing semicolon }
  { Pos() returns 0 if not found }
  Result := Pos(';' + Param + ';', ';' + OrigPath + ';') = 0;
end;

procedure RestartNowButtonClick(Sender: TObject);
var
  ResultCode: Integer;
begin
  if MsgBox('The computer will restart now. Make sure to save any unsaved work.' + #13#10 + #13#10 + 
            'Do you want to restart now?', mbConfirmation, MB_YESNO) = IDYES then
  begin
    RestartNowButton.Enabled := False;
    RestartLaterButton.Enabled := False;
    InfoLabel.Caption := 'Restarting your computer...';
    Exec('shutdown.exe', '/r /t 0', '', SW_HIDE, ewNoWait, ResultCode);
  end;
end;

procedure RestartLaterButtonClick(Sender: TObject);
begin
  WizardForm.Close;
end;

function InitializeSetup(): Boolean;
var
  BatchFile: string;
  BatchContent: TArrayOfString;
begin
  Result := True;
end;

procedure InitializeWizard();
begin
  { Create the restart page }
  RestartPage := CreateCustomPage(wpFinished, 'Restart Required', 
    'For some features to work, you may need to restart your computer.');
  
  { Create info label }
  InfoLabel := TLabel.Create(WizardForm);
  InfoLabel.Parent := RestartPage.Surface;
  InfoLabel.Caption := 'For some features to work, you may have to restart your computer.';
  InfoLabel.Left := 0;
  InfoLabel.Top := 16;
  InfoLabel.Width := RestartPage.SurfaceWidth;
  InfoLabel.Height := 30;
  InfoLabel.WordWrap := True;
  InfoLabel.Font.Size := 9;
  
  { Create "Restart Now" button }
  RestartNowButton := TButton.Create(WizardForm);
  RestartNowButton.Parent := RestartPage.Surface;
  RestartNowButton.Caption := 'Restart Now';
  RestartNowButton.Width := 150;
  RestartNowButton.Height := 30;
  RestartNowButton.Left := (RestartPage.SurfaceWidth div 2) - RestartNowButton.Width - 10;
  RestartNowButton.Top := InfoLabel.Top + InfoLabel.Height + 30;
  RestartNowButton.OnClick := @RestartNowButtonClick;
  
  { Create "I will restart manually later" button }
  RestartLaterButton := TButton.Create(WizardForm);
  RestartLaterButton.Parent := RestartPage.Surface;
  RestartLaterButton.Caption := 'I will restart manually later';
  RestartLaterButton.Width := 200;
  RestartLaterButton.Height := 30;
  RestartLaterButton.Left := (RestartPage.SurfaceWidth div 2) + 10;
  RestartLaterButton.Top := InfoLabel.Top + InfoLabel.Height + 30;
  RestartLaterButton.OnClick := @RestartLaterButtonClick;
end;

procedure CurPageChanged(CurPageID: Integer);
begin
  { Hide Next and Back buttons on the restart page }
  if (RestartPage <> nil) and (CurPageID = RestartPage.ID) then
  begin
    WizardForm.NextButton.Visible := False;
    WizardForm.BackButton.Visible := False;
    WizardForm.CancelButton.Visible := False;
  end
  else
  begin
    { Restore button visibility when not on restart page }
    WizardForm.NextButton.Visible := True;
    WizardForm.BackButton.Visible := True;
    WizardForm.CancelButton.Visible := True;
  end;
end;

function InstallVSCodeExtension(): Boolean;
var
  ResultCode: Integer;
  CodeCmdPath: string;
begin
  Result := False;
  
  // First, try using 'code' command (if it's in PATH or accessible)
  if Exec('cmd.exe', '/c code --install-extension rizzdev.easymark', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
  begin
    Result := True;
    Exit;
  end;
  
  // Try common VS Code installation paths
  // User installation (AppData)
  CodeCmdPath := ExpandConstant('{localappdata}\Programs\Microsoft VS Code\bin\code.cmd');
  if FileExists(CodeCmdPath) then
  begin
    if Exec(CodeCmdPath, '--install-extension rizzdev.easymark', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
    begin
      Result := True;
      Exit;
    end;
  end;
  
  // System-wide installation (Program Files)
  CodeCmdPath := ExpandConstant('{pf}\Microsoft VS Code\bin\code.cmd');
  if FileExists(CodeCmdPath) then
  begin
    if Exec(CodeCmdPath, '--install-extension rizzdev.easymark', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
    begin
      Result := True;
      Exit;
    end;
  end;
  
  // Program Files (x86)
  CodeCmdPath := ExpandConstant('{pf32}\Microsoft VS Code\bin\code.cmd');
  if FileExists(CodeCmdPath) then
  begin
    if Exec(CodeCmdPath, '--install-extension rizzdev.easymark', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
    begin
      Result := True;
      Exit;
    end;
  end;
  
  // Also try code.exe directly
  CodeCmdPath := ExpandConstant('{localappdata}\Programs\Microsoft VS Code\Code.exe');
  if FileExists(CodeCmdPath) then
  begin
    if Exec(CodeCmdPath, '--install-extension rizzdev.easymark', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
    begin
      Result := True;
      Exit;
    end;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  BatchFile: string;
  BatchContent: TArrayOfString;
begin
  if CurStep = ssPostInstall then
  begin
    // Create eminterp.bat wrapper file
    BatchFile := ExpandConstant('{app}\eminterp.bat');
    SetArrayLength(BatchContent, 1);
    BatchContent[0] := '@echo off' + #13#10 + 
                      '"%~dp0EasyMarkInterp.exe" %*';
    SaveStringsToFile(BatchFile, BatchContent, False);
    
    // Install VS Code extension automatically
    InstallVSCodeExtension();
  end;
end;

function RemovePathEntry(PathVar, Entry: string): string;
var
  NewPath: string;
  Part: string;
  SemicolonPos: Integer;
  WorkingPath: string;
begin
  NewPath := '';
  WorkingPath := PathVar + ';'; // Add semicolon at end for easier parsing
  
  // Parse each entry
  while Length(WorkingPath) > 0 do
  begin
    SemicolonPos := Pos(';', WorkingPath);
    if SemicolonPos > 0 then
    begin
      Part := Copy(WorkingPath, 1, SemicolonPos - 1);
      if (Part <> Entry) and (Part <> '') then
      begin
        if NewPath <> '' then
          NewPath := NewPath + ';';
        NewPath := NewPath + Part;
      end;
      WorkingPath := Copy(WorkingPath, SemicolonPos + 1, Length(WorkingPath));
    end
    else
      break;
  end;
  
  Result := NewPath;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  OrigPath: string;
  AppPath: string;
  NewPath: string;
begin
  if CurUninstallStep = usUninstall then
  begin
    AppPath := ExpandConstant('{app}');
    if RegQueryStringValue(HKEY_CURRENT_USER, 'Environment', 'Path', OrigPath) then
    begin
      // Remove the app path from PATH
      NewPath := RemovePathEntry(OrigPath, AppPath);
      RegWriteStringValue(HKEY_CURRENT_USER, 'Environment', 'Path', NewPath);
    end;
  end;
end;

