Simple PGN and JPG cropper for linux mint 22.2
Please see the pictures: Crop 1, Crop 2, Crop 3, Crop 4.
Put the file cropper.py in HOME directory
Right mouse button on the file/Properties/Permissions and check all EXECUTE boxes.
Put the file Image Cropper on Desktop and do the same: Right mouse button on the file/Properties/Permissions and check all EXECUTE boxes.
That's it. You can use the program.
To add in to context menu (open by ...) do the next:
Go to Home and click on right mouse button and check: Show All Hidden Files
Go to Home/.local/share/applications
Cut and paste the file: Cropper (leave Cropper only)
Rename to: Cropper 
This means - delete the text: (leave Cropper only)
type in terminal: chmod +x ~/.local/share/applications/cropper.desktop
type in terminal: update-desktop-database ~/.local/share/applications/
That's it - now when you press with right mouse button on any picture you will see the option: Open with cropper
Forever Free for use by everyone: private and/or public and/or business.
You are free to use as it is or change anything. 
Any issues or questions: good.vibes.github@gmail.com
