from tkinter import *
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import sys

class AdvancedCropper:
    def __init__(self, start_file=None):
        self.root = Tk()
        self.root.title("PNG/JPG Cropper")
        self.root.geometry("1150x780")

        self.original = None
        self.display_img = None
        self.tk_img = None
        self.scale = 1.0
        self.original_format = "PNG"
        self.current_dir = os.path.expanduser("~/Desktop")

        self.rect_coords = None
        self.rect_id = None
        self.handles = []
        self.mode = None
        self.start_x = self.start_y = 0
        self.start_rect = None

        top = Frame(self.root)
        top.pack(pady=8)

        Button(top, text="📂  Отвори файл", command=self.open_browser,
               font=("Arial", 11), width=16, bg="#2196F3", fg="white").pack(side=LEFT, padx=5)

        Button(top, text="💾  Запази (оригинално качество)", command=self.save_crop,
               font=("Arial", 11), bg="#4CAF50", fg="white", width=26).pack(side=LEFT, padx=5)

        Button(top, text="↺  Нулирай", command=self.reset_selection,
               font=("Arial", 10), width=12).pack(side=LEFT, padx=5)

        self.info = Label(self.root, text="Отвори папка → стрелки или мишка → Отвори",
                          font=("Arial", 9), fg="#555")
        self.info.pack()

        self.canvas = Canvas(self.root, bg="#1e1e1e", cursor="cross")
        self.canvas.pack(fill=BOTH, expand=True, padx=10, pady=8)

        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Motion>", self.on_motion)

        if start_file and os.path.isfile(start_file):
            self.load_image(start_file)

        self.root.mainloop()

    # ==================== ФАЙЛОВ БРАУЗЪР ====================
    def open_browser(self):
        win = Toplevel(self.root)
        win.title("Избери картина")
        win.geometry("900x600")
        win.transient(self.root)
        win.grab_set()

        left = Frame(win, width=320)
        left.pack(side=LEFT, fill=Y, padx=8, pady=8)
        left.pack_propagate(False)

        Button(left, text="📁  Избери друга папка",
               command=lambda: self.change_dir(win, listbox, preview_label, path_label),
               font=("Arial", 10)).pack(fill=X, pady=(0, 6))

        path_label = Label(left, text=self.current_dir, wraplength=300, justify=LEFT, fg="#333")
        path_label.pack(fill=X, pady=(0, 6))

        list_frame = Frame(left)
        list_frame.pack(fill=BOTH, expand=True)

        scrollbar = Scrollbar(list_frame)
        scrollbar.pack(side=RIGHT, fill=Y)

        listbox = Listbox(list_frame, yscrollcommand=scrollbar.set, font=("Arial", 10),
                          selectmode=SINGLE, activestyle="dotbox", exportselection=False)
        listbox.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.config(command=listbox.yview)

        right = Frame(win)
        right.pack(side=LEFT, fill=BOTH, expand=True, padx=8, pady=8)

        Label(right, text="Превю (стрелки ↑↓ или мишка)", font=("Arial", 10, "bold")).pack()
        preview_label = Label(right, bg="#222", text="Няма избран файл")
        preview_label.pack(fill=BOTH, expand=True, pady=8)

        btn_frame = Frame(win)
        btn_frame.pack(side=BOTTOM, fill=X, padx=10, pady=8)

        def do_open():
            sel = listbox.curselection()
            if not sel:
                messagebox.showwarning("Внимание", "Избери файл първо!", parent=win)
                return
            filename = listbox.get(sel[0])
            fullpath = os.path.join(self.current_dir, filename)
            win.destroy()
            self.load_image(fullpath)

        Button(btn_frame, text="✓  Отвори избрания файл", command=do_open,
               bg="#4CAF50", fg="white", font=("Arial", 11), width=22).pack(side=LEFT, padx=5)
        Button(btn_frame, text="Отказ", command=win.destroy,
               font=("Arial", 11), width=10).pack(side=LEFT, padx=5)

        self.populate_list(listbox, path_label)

        def update_preview(event=None):
            sel = listbox.curselection()
            if not sel:
                return
            filename = listbox.get(sel[0])
            fullpath = os.path.join(self.current_dir, filename)
            self.show_thumbnail(fullpath, preview_label)

        def move_selection(event):
            """Мести маркировката + превюто със стрелките"""
            if listbox.size() == 0:
                return "break"

            current = listbox.curselection()
            if current:
                idx = current[0]
            else:
                idx = 0

            if event.keysym == "Up":
                new_idx = max(0, idx - 1)
            elif event.keysym == "Down":
                new_idx = min(listbox.size() - 1, idx + 1)
            else:
                return

            listbox.selection_clear(0, END)
            listbox.selection_set(new_idx)
            listbox.activate(new_idx)
            listbox.see(new_idx)
            update_preview()
            return "break"   # спира стандартното поведение

        # Мишка
        listbox.bind("<<ListboxSelect>>", update_preview)

        # Стрелки – собствена логика
        listbox.bind("<Up>", move_selection)
        listbox.bind("<Down>", move_selection)

        # Enter и двоен клик
        listbox.bind("<Double-Button-1>", lambda e: do_open())
        listbox.bind("<Return>", lambda e: do_open())

        listbox.focus_set()

        # Автоматично първият файл
        if listbox.size() > 0:
            listbox.selection_set(0)
            listbox.activate(0)
            update_preview()

    def change_dir(self, win, listbox, preview_label, path_label):
        new_dir = filedialog.askdirectory(initialdir=self.current_dir, parent=win)
        if new_dir:
            self.current_dir = new_dir
            self.populate_list(listbox, path_label)
            preview_label.config(image="", text="Няма избран файл")
            if listbox.size() > 0:
                listbox.selection_set(0)
                listbox.activate(0)
                filename = listbox.get(0)
                fullpath = os.path.join(self.current_dir, filename)
                self.show_thumbnail(fullpath, preview_label)

    def populate_list(self, listbox, path_label):
        listbox.delete(0, END)
        path_label.config(text=self.current_dir)
        try:
            files = sorted(os.listdir(self.current_dir))
            for f in files:
                if f.lower().endswith((".png", ".jpg", ".jpeg")):
                    listbox.insert(END, f)
        except Exception as e:
            messagebox.showerror("Грешка", str(e))

    def show_thumbnail(self, path, label):
        try:
            img = Image.open(path)
            w, h = img.size
            max_size = 480
            ratio = min(max_size / w, max_size / h, 1.0)
            thumb = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)
            tk_img = ImageTk.PhotoImage(thumb)
            label.config(image=tk_img, text="")
            label.image = tk_img
        except Exception as e:
            label.config(image="", text=f"Грешка:\n{e}")

    def load_image(self, path):
        self.original = Image.open(path)
        self.original_format = self.original.format or "PNG"
        self.current_dir = os.path.dirname(path)

        if self.original.mode in ("RGBA", "P") and self.original_format in ("JPEG", "JPG"):
            self.original = self.original.convert("RGB")

        max_w, max_h = 1100, 620
        w, h = self.original.size
        self.scale = min(max_w / w, max_h / h, 1.0)

        new_size = (int(w * self.scale), int(h * self.scale))
        self.display_img = self.original.resize(new_size, Image.LANCZOS)
        self.tk_img = ImageTk.PhotoImage(self.display_img)

        self.canvas.delete("all")
        self.canvas.config(width=new_size[0], height=new_size[1])
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_img)

        margin = 25
        self.rect_coords = [margin, margin, new_size[0]-margin, new_size[1]-margin]
        self.draw_rect()

        self.info.config(text=f"{os.path.basename(path)}  |  {w}×{h} px  |  {self.original_format}")

    # ==================== КРОП ЛОГИКА ====================
    def draw_rect(self):
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        for h in self.handles:
            self.canvas.delete(h)
        self.handles.clear()

        if not self.rect_coords:
            return

        x1, y1, x2, y2 = self.rect_coords
        self.rect_id = self.canvas.create_rectangle(x1, y1, x2, y2, outline="#00FF66", width=2)

        s = 7
        for cx, cy in [(x1,y1), (x2,y1), (x1,y2), (x2,y2)]:
            h = self.canvas.create_rectangle(cx-s, cy-s, cx+s, cy+s, fill="#00FF66", outline="black")
            self.handles.append(h)

    def get_mode(self, x, y):
        if not self.rect_coords:
            return "new"
        x1, y1, x2, y2 = self.rect_coords
        edge = 12
        near_l = abs(x - x1) < edge
        near_r = abs(x - x2) < edge
        near_t = abs(y - y1) < edge
        near_b = abs(y - y2) < edge

        if near_t and near_l: return "nw"
        if near_t and near_r: return "ne"
        if near_b and near_l: return "sw"
        if near_b and near_r: return "se"
        if near_t: return "n"
        if near_b: return "s"
        if near_l: return "w"
        if near_r: return "e"
        if x1 < x < x2 and y1 < y < y2: return "move"
        return "new"

    def on_motion(self, event):
        mode = self.get_mode(event.x, event.y)
        cursors = {
            "move": "fleur",
            "n": "sb_v_double_arrow", "s": "sb_v_double_arrow",
            "e": "sb_h_double_arrow", "w": "sb_h_double_arrow",
            "ne": "bottom_left_corner", "sw": "bottom_left_corner",
            "nw": "bottom_right_corner", "se": "bottom_right_corner",
            "new": "cross"
        }
        self.canvas.config(cursor=cursors.get(mode, "cross"))

    def on_press(self, event):
        self.start_x, self.start_y = event.x, event.y
        self.mode = self.get_mode(event.x, event.y)
        self.start_rect = list(self.rect_coords) if self.rect_coords else None
        if self.mode == "new":
            self.rect_coords = [event.x, event.y, event.x, event.y]
            self.draw_rect()

    def on_drag(self, event):
        if not self.mode:
            return
        dx = event.x - self.start_x
        dy = event.y - self.start_y

        if self.mode == "new":
            self.rect_coords[2] = event.x
            self.rect_coords[3] = event.y
        elif self.mode == "move" and self.start_rect:
            w = self.start_rect[2] - self.start_rect[0]
            h = self.start_rect[3] - self.start_rect[1]
            self.rect_coords = [self.start_rect[0]+dx, self.start_rect[1]+dy,
                                self.start_rect[0]+dx+w, self.start_rect[1]+dy+h]
        elif self.start_rect:
            x1, y1, x2, y2 = self.start_rect
            if "n" in self.mode: y1 += dy
            if "s" in self.mode: y2 += dy
            if "w" in self.mode: x1 += dx
            if "e" in self.mode: x2 += dx
            self.rect_coords = [x1, y1, x2, y2]

        self.normalize_rect()
        self.draw_rect()

    def on_release(self, event):
        self.mode = None
        self.normalize_rect()
        self.draw_rect()

    def normalize_rect(self):
        if not self.rect_coords:
            return
        x1, y1, x2, y2 = self.rect_coords
        self.rect_coords = [min(x1,x2), min(y1,y2), max(x1,x2), max(y1,y2)]
        w, h = self.display_img.width, self.display_img.height
        self.rect_coords[0] = max(0, min(self.rect_coords[0], w-5))
        self.rect_coords[1] = max(0, min(self.rect_coords[1], h-5))
        self.rect_coords[2] = max(5, min(self.rect_coords[2], w))
        self.rect_coords[3] = max(5, min(self.rect_coords[3], h))

    def reset_selection(self):
        if self.display_img:
            m = 20
            self.rect_coords = [m, m, self.display_img.width-m, self.display_img.height-m]
            self.draw_rect()

    def save_crop(self):
        if not self.original or not self.rect_coords:
            messagebox.showwarning("Внимание", "Няма какво да се запази!")
            return

        ext = ".jpg" if self.original_format in ("JPEG", "JPG") else ".png"

        path = filedialog.asksaveasfilename(
            initialdir=os.path.expanduser("~/Desktop"),
            defaultextension=ext,
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("All", "*.*")]
        )
        if not path:
            return

        x1, y1, x2, y2 = self.rect_coords
        left   = int(x1 / self.scale)
        top    = int(y1 / self.scale)
        right  = int(x2 / self.scale)
        bottom = int(y2 / self.scale)

        cropped = self.original.crop((left, top, right, bottom))

        if path.lower().endswith((".jpg", ".jpeg")):
            if cropped.mode in ("RGBA", "P"):
                cropped = cropped.convert("RGB")
            cropped.save(path, quality=100, subsampling=0, optimize=False)
        else:
            cropped.save(path, compress_level=0)

        messagebox.showinfo("Готово", f"Запазено с оригинално качество:\n{path}")


if __name__ == "__main__":
    start_file = sys.argv[1] if len(sys.argv) > 1 else None
    AdvancedCropper(start_file)
