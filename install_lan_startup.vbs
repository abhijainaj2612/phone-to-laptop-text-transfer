' Adds the LAN-mode launcher to the current user's Startup folder.
Option Explicit
Dim fso, shell, root, startup, shortcut
Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")
root = fso.GetParentFolderName(WScript.ScriptFullName)
Set shortcut = shell.CreateShortcut(shell.SpecialFolders("Startup") & "\PC Type Assistant - LAN.lnk")
shortcut.TargetPath = root & "\start_lan_background.vbs"
shortcut.WorkingDirectory = root
shortcut.Description = "Start Phone PC Type Assistant on the local Wi-Fi"
shortcut.Save
MsgBox "LAN mode will now start automatically after you sign in.", 64, "PC Type Assistant"
