Simple PNG, JPG and WebP cropper for Linux Mint 22.2

Please see the pictures: Crop 1, Crop 2, Crop 3, Crop 4.

=== Installation ===

1. Put the file "cropper.py" in your HOME directory.
2. Right-click on cropper.py → Properties → Permissions → check all "Execute" boxes.

3. There are TWO different .desktop files:

   - File 1: "cropper.desktop"
     → Put this one on your Desktop
     → Right-click → Properties → Permissions → check all "Execute" boxes

4. Open Terminal and run these two commands:

sudo apt install python3-pillow
sudo apt install python3-pil.imagetk

That's it. You can now use the program from the Desktop shortcut.

=== Add to "Open With" context menu ===

1. Go to your Home folder.
2. Right-click on empty space → check "Show Hidden Files".
3. Go to the folder: .local/share/applications
4.There are TWO different .desktop files:

   - File 2: "cropper-openwith.desktop"
     → This one is for the context menu ("Open with")

6. Copy the file "cropper-openwith.desktop" into this folder.
7. Rename it to: cropper.desktop
8. Open Terminal and run:

chmod +x ~/.local/share/applications/cropper.desktop
update-desktop-database ~/.local/share/applications/

Done. Now when you right-click on any image you will see "Open with Cropper".

=== License ===

Forever free for everyone — private, public and business use.
You are free to use it as is or modify it.

Any issues or questions: good.vibes.github@gmail.com
