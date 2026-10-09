' Runs the local relay and PC typing client silently. Cloudflared itself runs as a Windows service.
Option Explicit
Dim fso, shell, root, pythonw, relayCommand, clientCommand
Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")
root = fso.GetParentFolderName(WScript.ScriptFullName)
pythonw = root & "\.venv\Scripts\pythonw.exe"

If Not fso.FileExists(pythonw) Then
  MsgBox "Python virtual environment was not found. Complete the one-time setup first.", 16, "PC Type Assistant"
  WScript.Quit 1
End If

' 0 = hidden window. Start the relay first, then the client connects through Cloudflare.
relayCommand = """" & pythonw & """ -m uvicorn relay_server.main:app --host 127.0.0.1 --port 8000"
clientCommand = """" & pythonw & """ -m pc_client.main"
shell.Run relayCommand, 0, False
WScript.Sleep 1200
shell.Run clientCommand, 0, False
