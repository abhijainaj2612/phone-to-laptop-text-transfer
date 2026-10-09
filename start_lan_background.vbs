' Runs the LAN relay and PC typing client silently on the same Wi-Fi network.
Option Explicit
Dim fso, shell, root, pythonw, relayCommand, clientCommand, quote, relayLog, clientLog
Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")
root = fso.GetParentFolderName(WScript.ScriptFullName)
pythonw = root & "\.venv\Scripts\pythonw.exe"
quote = Chr(34)
relayLog = root & "\lan-relay.log"
clientLog = root & "\lan-client.log"

If Not fso.FileExists(pythonw) Then
  MsgBox "Python virtual environment was not found. Complete the one-time setup first.", 16, "PC Type Assistant"
  WScript.Quit 1
End If

' 0 = hidden window. 0.0.0.0 accepts connections only when Windows Firewall permits the local network.
relayCommand = "cmd.exe /c " & quote & quote & pythonw & quote & " -m uvicorn relay_server.main:app --host 0.0.0.0 --port 8000 >> " & quote & relayLog & quote & " 2>&1" & quote
clientCommand = "cmd.exe /c " & quote & quote & pythonw & quote & " -m pc_client.main >> " & quote & clientLog & quote & " 2>&1" & quote
shell.Run relayCommand, 0, False
WScript.Sleep 1200
shell.Run clientCommand, 0, False
