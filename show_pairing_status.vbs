' Opens the pairing/status file created by the background PC client.
Option Explicit
Dim fso, shell, statusFile
Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")
statusFile = shell.ExpandEnvironmentStrings("%USERPROFILE%") & "\PhonePCTypeAssistant-status.txt"

If Not fso.FileExists(statusFile) Then
  MsgBox "The background client has not created its status file yet. Start LAN mode, then wait a few seconds.", 48, "PC Type Assistant"
  WScript.Quit 1
End If
shell.Run "notepad.exe """ & statusFile & """", 1, False
