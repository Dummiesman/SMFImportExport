
# SMFImportExport
Blender addon for 4x4 Evolution and 4x4 Evolution 2 model files.

### How to install
Download the addon from the releases page. Open Blender, open Edit->Preferences, select the "Add-Ons" tab, click Install, then choose the zip file you downloaded. Once installed, make sure it's enabled in the list.

### Material setup
The addon relies on your materials being Principled BSDF, and will use the settings from the first material on the mesh. To make your mesh reflective, turn up the specular value. To make your mesh transparent, set the material alpha type to anything except "Opaque". 

### Texture setup
The addon will use the textures assigned to the "Base Color" and "Normal" (w/ Normal Map node) slots. If you need an example, import a SMF file from the game.

### RAW Textures
The addon will load RAW/ACT/OPA files. If you would like to load one manually, use the "Terminal Reality Tools" menu at the top of the screen.

### Switching, what is it?
Track objects containing L versions (OPAQUE+OPAQUEL for example) supports witching from the high detail, to the low detail (L) version based on their height on screen. Enable switching for these objects and double check the original files 4th line (second value) for the original switching height.

### 4x4 Evolution 2 Note
- Texture alpha channels from this game are not imported properly, this is a visual issue and won't affect exporting back to the game.
- Check the "Use v1 Materials" on export when exporting for Evo 2, to take advantage of bumpmapped materials.

### Special Thanks
Thanks to NytroDesigns who inspired this project in the first place, helped explain some values, and helped with testing.
