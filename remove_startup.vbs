' Removes the automatic-start shortcut for the current user.
Option Explicit
Dim fso, shell, shortcut
Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")
shortcut = shell.SpecialFolders("Startup") & "\PC Type Assistant.lnk"
If fso.FileExists(shortcut) Then fso.DeleteFile shortcut, True
MsgBox "Automatic start has been removed.", 64, "PC Type Assistant"
