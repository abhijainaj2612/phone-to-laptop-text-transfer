' Adds PC Type Assistant to the current Windows user's Startup folder.
Option Explicit
Dim fso, shell, root, startup, shortcut
Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")
root = fso.GetParentFolderName(WScript.ScriptFullName)
startup = shell.SpecialFolders("Startup")
Set shortcut = shell.CreateShortcut(startup & "\PC Type Assistant.lnk")
shortcut.TargetPath = root & "\start_background.vbs"
shortcut.WorkingDirectory = root
shortcut.Description = "Start Phone PC Type Assistant silently"
shortcut.Save
MsgBox "PC Type Assistant will now start automatically after you sign in.", 64, "PC Type Assistant"
