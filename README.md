# Image Cropper

Simple PNG, JPG and WebP cropper for **Linux Mint 22.2**.

Please see the pictures: `Crop 1`, `Crop 2`, `Crop 3`, `Crop 4`.

---

## Installation

1. Put the file `cropper.py` in your **HOME** directory.

2. Right-click on `cropper.py` → **Properties** → **Permissions** → check all **Execute** boxes.

3. There are **two** different `.desktop` files:

   - **File 1: `cropper.desktop`**  
     → Put this one on your **Desktop**  
     → Right-click → **Properties** → **Permissions** → check all **Execute** boxes

4. Open Terminal and run these two commands:

```bash
sudo apt install python3-pillow
sudo apt install python3-pil.imagetk
```
if you get ERROR than swap them: 

```bash
sudo apt install python3-pil.imagetk
sudo apt install python3-pillow
```

or type: 

```bash
sudo apt install python3-pil python3-pil.imagetk
```

That's it. You can now use the program from the Desktop shortcut.

---

## Add to "Open With" context menu

1. Go to your Home folder.

2. Right-click on empty space → check **Show Hidden Files**.

3. Go to the folder: `.local/share/applications`

4. There are **two** different `.desktop` files:

   - **File 2: `cropper-openwith.desktop`**  
     → This one is for the context menu ("Open with")

5. Cut/Paste the file `cropper-openwith.desktop` into this folder.

6. Rename it to: `cropper.desktop`  
   → Right-click → **Properties** → **Permissions** → check all **Execute** boxes

7. Open Terminal and run:

```bash
chmod +x ~/.local/share/applications/cropper.desktop
update-desktop-database ~/.local/share/applications/
```

Done. Now when you right-click on any image you will see **"Open with Cropper"**.

---

## License

**Forever Free** for use by everyone: private and/or public and/or business.

You are free to use it as it is or change anything you want depending on your whims.

Any issues, questions, or if you are too lazy to do the changes yourself:  
**good.vibes.github@gmail.com**

END
