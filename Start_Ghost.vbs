Set WshShell = CreateObject("WScript.Shell")
' This runs the script using pythonw.exe (the windowless version)
WshShell.Run "C:\Users\jugad\PytonProjects\.venv\Scripts\pythonw.exe C:\Users\jugad\PytonProjects\vault_guard.py", 0, False