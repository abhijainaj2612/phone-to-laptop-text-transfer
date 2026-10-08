' Starts the PC client without a visible PowerShell or console window.
Option Explicit
Dim fso, shell, root, pythonw, command
Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")
root = fso.GetParentFolderName(WScript.ScriptFullName)
pythonw = root & "\.venv\Scripts\pythonw.exe"

If Not fso.FileExists(pythonw) Then
  MsgBox "Python virtual environment was not found. Run the one-time setup in README.md first.", 16, "PC Type Assistant"
  WScript.Quit 1
End If

' 0 = hidden window, False = do not wait for the client to exit.
' pythonw.exe has no console window; keeping this command simple avoids quoting errors.
command = """" & pythonw & """ -m pc_client.main"
shell.Run command, 0, False
