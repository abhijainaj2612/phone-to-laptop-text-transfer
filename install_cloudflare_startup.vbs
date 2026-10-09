' Adds the Cloudflare-mode background launcher to the current user's Startup folder.
Option Explicit
Dim fso, shell, root, startup, shortcut
Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")
root = fso.GetParentFolderName(WScript.ScriptFullName)
startup = shell.SpecialFolders("Startup")
Set shortcut = shell.CreateShortcut(startup & "\PC Type Assistant - Cloudflare.lnk")
shortcut.TargetPath = root & "\start_cloudflare_background.vbs"
shortcut.WorkingDirectory = root
shortcut.Description = "Start Phone PC Type Assistant through Cloudflare Tunnel"
shortcut.Save
MsgBox "PC Type Assistant will start automatically after you sign in.", 64, "PC Type Assistant"
