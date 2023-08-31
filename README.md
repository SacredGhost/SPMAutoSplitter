# SPM Auto Splitter
#### vBeta1
An external auto splitter for Dolphin Emulator speedruns of Super Paper Mario. <br />
Supports all versions of the game, and since it's external, will support all timers that use hotkeys.

Current only splits for Any%

### How to use
Simply launch Super Paper Mario on Dolphin, and open AutoSplitter.exe <br />
<br />
To change your hotkey split to match your LiveSplit, open hotkeys.config and change the key to one of the provided key bindings. <br />
Make sure in your LiveSplit settings or on other timers, to have global hotkeys enabled. <br />
<br />
If your key is not on this list and you would like it added, please let me know or input a github issue.

### Credits
SeekyCt - For all of the reverse engineering of SPM, helping this process greatly <br />
JohnP55 - Creating read and write functions for DME and general code optimization <br />
NmFlash8 - NmFlash8

### To Do
Add options to change when to split (CastleSR timing, etc)
Add options to change extra splits are active (6-1 -> 6-2 -> 6-? instead of 6-1 -> 6-?)
Add Return Pipe and Enter Pipe functions for Pit% and Deafeat Shadoo. <br />
Add 100% speedrun type splits. <br />
Console Support (Wii U)

### For Developers: 
Python 11 not supported by dolphin memory engine. Must use Python 10.