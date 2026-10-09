' Removes the automatic-start shortcut for the current user.
Option Explicit
Dim fso, shell, shortcut, cloudflareShortcut, lanShortcut
Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")
shortcut = shell.SpecialFolders("Startup") & "\PC Type Assistant.lnk"
cloudflareShortcut = shell.SpecialFolders("Startup") & "\PC Type Assistant - Cloudflare.lnk"
lanShortcut = shell.SpecialFolders("Startup") & "\PC Type Assistant - LAN.lnk"
If fso.FileExists(shortcut) Then fso.DeleteFile shortcut, True
If fso.FileExists(cloudflareShortcut) Then fso.DeleteFile cloudflareShortcut, True
If fso.FileExists(lanShortcut) Then fso.DeleteFile lanShortcut, True
MsgBox "Automatic start has been removed.", 64, "PC Type Assistant"
