' RetroDeck Windows Silent Launcher
' Runs RetroDeck.bat without keeping an open CMD console window in the background.
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "cmd /c RetroDeck.bat", 0, False
Set WshShell = Nothing
