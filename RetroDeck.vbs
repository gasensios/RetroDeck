' RetroDeck Windows Silent Launcher
' Runs RetroDeck.bat without keeping an open CMD console window in the background.
Set WshShell = CreateObject("WScript.Shell")
Set FSO = CreateObject("Scripting.FileSystemObject")
ScriptDir = FSO.GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = ScriptDir
WshShell.Run "cmd /c """ & ScriptDir & "\RetroDeck.bat""", 0, False
Set WshShell = Nothing
Set FSO = Nothing
