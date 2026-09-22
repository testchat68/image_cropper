from tkinter import *
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import sys


class AdvancedCropper:
    def __init__(self, start_file=None):
        self.root = Tk()
        self.root.title("PNG / JPG / WebP Cropper")
        self.root.geometry("1150x780")

        self.original = None
        self.source_original = None
        self.display_img = None
        self.tk_img = None
        self.scale = 1.0
        self.original_format = "PNG"
        self.current_path = None
        self.current_dir = os.path.expanduser("~/Desktop")

        self.tool = None  # "crop" | "resize" | None
        self.rect_coords = None
        self.rect_id = None
        self.handles = []
        self.size_label_id = None
        self.mode = None
        self.start_x = self.start_y = 0
        self.start_rect = None
        self.resize_out = None  # (w, h) in original pixels
        self.whitened = False

        top = Frame(self.root)
        top.pack(pady=8)

        Button(top, text="📂  Отвори файл", command=self.open_browser,
               font=("Arial", 11), width=16, bg="#2196F3", fg="white").pack(side=LEFT, padx=5)
        Button(top, text="💾  Запази", command=self.save_crop,
               font=("Arial", 11), bg="#4CAF50", fg="white", width=18).pack(side=LEFT, padx=5)
        Button(top, text="↺  Нулирай", command=self.reset_selection,
               font=("Arial", 10), width=12).pack(side=LEFT, padx=5)

        self.tools = Frame(self.root)
        self.tools.pack(pady=(0, 6))

        self.btn_crop = Button(
            self.tools, text="✂  Crop", command=self.set_crop_tool,
            font=("Arial", 11), width=14, state=DISABLED)
        self.btn_crop.pack(side=LEFT, padx=5)

        self.btn_resize = Button(
            self.tools, text="✥  Resize", command=self.set_resize_tool,
            font=("Arial", 11), width=14, state=DISABLED)
        self.btn_resize.pack(side=LEFT, padx=5)

        self.btn_white = Button(
            self.tools, text="☀  Auto White", command=self.auto_white,
            font=("Arial", 11), width=16, state=DISABLED)
        self.btn_white.pack(side=LEFT, padx=5)

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
            if listbox.size() == 0:
                return "break"
            current = listbox.curselection()
            idx = current[0] if current else 0
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
            return "break"

        listbox.bind("<<ListboxSelect>>", update_preview)
        listbox.bind("<Up>", move_selection)
        listbox.bind("<Down>", move_selection)
        listbox.bind("<Double-Button-1>", lambda e: do_open())
        listbox.bind("<Return>", lambda e: do_open())
        listbox.focus_set()
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
                if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
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
        img = Image.open(path)
        self.original_format = (img.format or "PNG").upper()
        self.current_dir = os.path.dirname(path)
        self.current_path = path
        if img.mode in ("RGBA", "P") and self.original_format in ("JPEG", "JPG"):
            img = img.convert("RGB")
        elif img.mode == "P":
            img = img.convert("RGBA")
        self.source_original = img.copy()
        self.original = img.copy()
        self.whitened = False
        self.tool = None
        self.resize_out = list(self.original.size)
        self.refresh_display(reset_rect=True)
        self.enable_tools()
        self.highlight_tools()
        self.update_info()

    def refresh_display(self, reset_rect=False):
        if not self.original:
            return
        max_w, max_h = 1100, 620
        w, h = self.original.size
        self.scale = min(max_w / w, max_h / h, 1.0)
        new_size = (max(1, int(w * self.scale)), max(1, int(h * self.scale)))
        self.display_img = self.original.resize(new_size, Image.LANCZOS)
        self.tk_img = ImageTk.PhotoImage(self.display_img)
        self.canvas.delete("all")
        self.rect_id = None
        self.size_label_id = None
        self.handles.clear()
        self.canvas.config(width=new_size[0] + 80, height=new_size[1] + 80)
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_img)
        if reset_rect:
            self.rect_coords = None
        if self.tool == "crop":
            if reset_rect or not self.rect_coords:
                margin = 25
                self.rect_coords = [margin, margin, new_size[0] - margin, new_size[1] - margin]
            self.draw_rect()
        elif self.tool == "resize":
            self.sync_resize_rect_from_out()
            self.draw_rect()

    def enable_tools(self):
        state = NORMAL if self.original else DISABLED
        self.btn_crop.config(state=state)
        self.btn_resize.config(state=state)
        self.btn_white.config(state=state)

    def highlight_tools(self):
        idle = {"bg": "#eeeeee", "fg": "#222", "relief": RAISED}
        on = {"bg": "#00AA55", "fg": "white", "relief": SUNKEN}
        rz = {"bg": "#FF9800", "fg": "white", "relief": SUNKEN}
        self.btn_crop.config(**(on if self.tool == "crop" else idle))
        self.btn_resize.config(**(rz if self.tool == "resize" else idle))
        self.btn_white.config(**({"bg": "#FFF8E1", "fg": "#333", "relief": RAISED} if self.whitened else idle))

    def update_info(self):
        if not self.original:
            return
        name = os.path.basename(self.current_path) if self.current_path else ""
        w, h = self.original.size
        extra = "  |  Auto White" if self.whitened else ""
        if self.tool == "resize" and self.resize_out:
            ow, oh = self.resize_out
            extra += f"  |  изход: {ow}×{oh} px  {self.scale_text(ow, w)}"
        self.info.config(text=f"{name}  |  {w}×{h} px  |  {self.original_format}{extra}")

    def scale_text(self, out_w, orig_w):
        if orig_w <= 0:
            return "+1.0x"
        ratio = out_w / float(orig_w)
        if abs(ratio - 1.0) < 0.005:
            return "+1.0x"
        if ratio >= 1:
            return f"+{ratio:.1f}x"
        inv = 1.0 / ratio if ratio > 0 else 1.0
        return f"-{inv:.1f}x"

    def set_crop_tool(self):
        if not self.original:
            return
        self.tool = "crop"
        if self.display_img:
            margin = 25
            w, h = self.display_img.size
            self.rect_coords = [margin, margin, w - margin, h - margin]
        self.highlight_tools()
        self.draw_rect()
        self.update_info()

    def set_resize_tool(self):
        if not self.original:
            return
        self.tool = "resize"
        if not self.resize_out:
            self.resize_out = list(self.original.size)
        self.sync_resize_rect_from_out()
        self.highlight_tools()
        self.draw_rect()
        self.update_info()

    def sync_resize_rect_from_out(self):
        if not self.resize_out:
            return
        ow, oh = self.resize_out
        self.rect_coords = [0, 0, ow * self.scale, oh * self.scale]

    def sync_resize_out_from_rect(self):
        if not self.rect_coords or self.scale <= 0:
            return
        x1, y1, x2, y2 = self.rect_coords
        w = max(2, abs(x2 - x1) / self.scale)
        h = max(2, abs(y2 - y1) / self.scale)
        self.resize_out = [max(1, int(round(w))), max(1, int(round(h)))]

    def auto_white(self):
        if not self.original:
            return
        img = self.original
        rgb = img.convert("RGB")
        extrema = rgb.getextrema()
        peak = max(ch[1] for ch in extrema)
        if peak <= 0:
            messagebox.showinfo("Auto White", "Картинката е изцяло черна.")
            return
        if peak >= 255:
            messagebox.showinfo("Auto White", "Най-светлата част вече е чисто бяло.")
            self.whitened = True
            self.highlight_tools()
            return
        gain = 255.0 / float(peak)
        lut = [min(255, int(i * gain + 0.5)) for i in range(256)]
        if img.mode == "RGBA":
            r, g, b, a = img.split()
            r, g, b = r.point(lut), g.point(lut), b.point(lut)
            self.original = Image.merge("RGBA", (r, g, b, a))
        elif img.mode == "RGB":
            r, g, b = img.split()
            r, g, b = r.point(lut), g.point(lut), b.point(lut)
            self.original = Image.merge("RGB", (r, g, b))
        else:
            converted = img.convert("RGB")
            r, g, b = converted.split()
            r, g, b = r.point(lut), g.point(lut), b.point(lut)
            self.original = Image.merge("RGB", (r, g, b))
        self.whitened = True
        self.refresh_display(reset_rect=False)
        self.highlight_tools()
        self.update_info()
        self.info.config(
            text=self.info.cget("text") + f"  |  печалба ×{gain:.2f}  (пик {peak} → 255)"
        )

    def draw_rect(self):
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        if self.size_label_id:
            self.canvas.delete(self.size_label_id)
            self.size_label_id = None
        for h in self.handles:
            self.canvas.delete(h)
        self.handles.clear()
        if not self.rect_coords or not self.tool:
            return
        x1, y1, x2, y2 = self.rect_coords
        color = "#00FF66" if self.tool == "crop" else "#FFCC33"
        self.rect_id = self.canvas.create_rectangle(x1, y1, x2, y2, outline=color, width=2)
        s = 7
        for cx, cy in [(x1, y1), (x2, y1), (x1, y2), (x2, y2)]:
            h = self.canvas.create_rectangle(cx - s, cy - s, cx + s, cy + s,
                                             fill=color, outline="black")
            self.handles.append(h)
        if self.tool == "resize" and self.original:
            self.sync_resize_out_from_rect()
            ow, oh = self.resize_out
            txt = f"{ow} × {oh} px   {self.scale_text(ow, self.original.size[0])}"
            tx = min(x1, x2) + 8
            ty = min(y1, y2) + 8
            self.size_label_id = self.canvas.create_text(
                tx, ty, anchor="nw", text=txt,
                fill="#FFE082", font=("Arial", 13, "bold")
            )
            self.update_info()

    def get_mode(self, x, y):
        if not self.rect_coords or not self.tool:
            return None
        x1, y1, x2, y2 = self.rect_coords
        edge = 12
        near_l = abs(x - x1) < edge
        near_r = abs(x - x2) < edge
        near_t = abs(y - y1) < edge
        near_b = abs(y - y2) < edge
        if near_t and near_l:
            return "nw"
        if near_t and near_r:
            return "ne"
        if near_b and near_l:
            return "sw"
        if near_b and near_r:
            return "se"
        if near_t:
            return "n"
        if near_b:
            return "s"
        if near_l:
            return "w"
        if near_r:
            return "e"
        if x1 < x < x2 and y1 < y < y2:
            return "move"
        if self.tool == "crop":
            return "new"
        return None

    def on_motion(self, event):
        mode = self.get_mode(event.x, event.y)
        cursors = {
            "move": "fleur",
            "n": "sb_v_double_arrow", "s": "sb_v_double_arrow",
            "e": "sb_h_double_arrow", "w": "sb_h_double_arrow",
            "ne": "bottom_left_corner", "sw": "bottom_left_corner",
            "nw": "bottom_right_corner", "se": "bottom_right_corner",
            "new": "cross",
        }
        self.canvas.config(cursor=cursors.get(mode, "arrow" if self.tool else "cross"))

    def on_press(self, event):
        if not self.tool:
            return
        self.start_x, self.start_y = event.x, event.y
        self.mode = self.get_mode(event.x, event.y)
        self.start_rect = list(self.rect_coords) if self.rect_coords else None
        if self.tool == "crop" and self.mode == "new":
            self.rect_coords = [event.x, event.y, event.x, event.y]
            self.draw_rect()

    def on_drag(self, event):
        if not self.mode or not self.tool:
            return
        dx = event.x - self.start_x
        dy = event.y - self.start_y
        if self.tool == "resize":
            self.drag_resize(event, dx, dy)
            self.draw_rect()
            return
        if self.mode == "new":
            self.rect_coords[2] = event.x
            self.rect_coords[3] = event.y
        elif self.mode == "move" and self.start_rect:
            w = self.start_rect[2] - self.start_rect[0]
            h = self.start_rect[3] - self.start_rect[1]
            self.rect_coords = [self.start_rect[0] + dx, self.start_rect[1] + dy,
                                self.start_rect[0] + dx + w, self.start_rect[1] + dy + h]
        elif self.start_rect:
            x1, y1, x2, y2 = self.start_rect
            if "n" in self.mode:
                y1 += dy
            if "s" in self.mode:
                y2 += dy
            if "w" in self.mode:
                x1 += dx
            if "e" in self.mode:
                x2 += dx
            self.rect_coords = [x1, y1, x2, y2]
        self.normalize_rect()
        self.draw_rect()

    def drag_resize(self, event, dx, dy):
        if not self.start_rect or not self.original:
            return
        x1, y1, x2, y2 = self.start_rect
        ow, oh = self.original.size
        aspect = ow / float(oh) if oh else 1.0
        min_disp = 16

        if self.mode == "move":
            w = x2 - x1
            h = y2 - y1
            self.rect_coords = [x1 + dx, y1 + dy, x1 + dx + w, y1 + dy + h]
            return

        if self.mode in ("n", "s"):
            if self.mode == "n":
                y1 = self.start_rect[1] + dy
            else:
                y2 = self.start_rect[3] + dy
            new_h = max(min_disp, abs(y2 - y1))
            new_w = new_h * aspect
            cx = (self.start_rect[0] + self.start_rect[2]) / 2.0
            if self.mode == "n":
                y2 = self.start_rect[3]
                y1 = y2 - new_h
            else:
                y1 = self.start_rect[1]
                y2 = y1 + new_h
            x1 = cx - new_w / 2.0
            x2 = cx + new_w / 2.0
        elif self.mode in ("e", "w"):
            if self.mode == "w":
                x1 = self.start_rect[0] + dx
            else:
                x2 = self.start_rect[2] + dx
            new_w = max(min_disp, abs(x2 - x1))
            new_h = new_w / aspect
            cy = (self.start_rect[1] + self.start_rect[3]) / 2.0
            if self.mode == "w":
                x2 = self.start_rect[2]
                x1 = x2 - new_w
            else:
                x1 = self.start_rect[0]
                x2 = x1 + new_w
            y1 = cy - new_h / 2.0
            y2 = cy + new_h / 2.0
        else:
            anchors = {
                "se": (self.start_rect[0], self.start_rect[1]),
                "sw": (self.start_rect[2], self.start_rect[1]),
                "ne": (self.start_rect[0], self.start_rect[3]),
                "nw": (self.start_rect[2], self.start_rect[3]),
            }
            ax, ay = anchors[self.mode]
            raw_w = abs(event.x - ax)
            raw_h = abs(event.y - ay)
            if raw_w / aspect >= raw_h:
                new_w = max(min_disp, raw_w)
                new_h = new_w / aspect
            else:
                new_h = max(min_disp, raw_h)
                new_w = new_h * aspect
            if event.x >= ax:
                x1, x2 = ax, ax + new_w
            else:
                x2, x1 = ax, ax - new_w
            if event.y >= ay:
                y1, y2 = ay, ay + new_h
            else:
                y2, y1 = ay, ay - new_h

        self.rect_coords = [x1, y1, x2, y2]
        self.normalize_resize_rect()

    def on_release(self, event):
        self.mode = None
        if self.tool == "crop":
            self.normalize_rect()
        elif self.tool == "resize":
            self.normalize_resize_rect()
        if self.tool:
            self.draw_rect()

    def normalize_rect(self):
        if not self.rect_coords or not self.display_img:
            return
        x1, y1, x2, y2 = self.rect_coords
        self.rect_coords = [min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)]
        w, h = self.display_img.width, self.display_img.height
        self.rect_coords[0] = max(0, min(self.rect_coords[0], w - 5))
        self.rect_coords[1] = max(0, min(self.rect_coords[1], h - 5))
        self.rect_coords[2] = max(5, min(self.rect_coords[2], w))
        self.rect_coords[3] = max(5, min(self.rect_coords[3], h))

    def normalize_resize_rect(self):
        if not self.rect_coords:
            return
        x1, y1, x2, y2 = self.rect_coords
        self.rect_coords = [min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)]
        if self.rect_coords[2] - self.rect_coords[0] < 8:
            self.rect_coords[2] = self.rect_coords[0] + 8
        if self.rect_coords[3] - self.rect_coords[1] < 8:
            self.rect_coords[3] = self.rect_coords[1] + 8
        self.sync_resize_out_from_rect()

    def reset_selection(self):
        if self.source_original:
            self.original = self.source_original.copy()
            self.whitened = False
            self.resize_out = list(self.original.size)
            self.refresh_display(reset_rect=True)
            if self.tool == "crop":
                self.set_crop_tool()
            elif self.tool == "resize":
                self.set_resize_tool()
            else:
                self.highlight_tools()
                self.update_info()
            return
        if self.display_img and self.tool == "crop":
            m = 20
            self.rect_coords = [m, m, self.display_img.width - m, self.display_img.height - m]
            self.draw_rect()

    def save_crop(self):
        if not self.original:
            messagebox.showwarning("Внимание", "Няма какво да се запази!")
            return

        path = filedialog.asksaveasfilename(
            initialdir=os.path.expanduser("~/Desktop"),
            title="Запази",
            filetypes=[
                ("PNG", "*.png"),
                ("JPEG", "*.jpg"),
                ("WebP", "*.webp"),
                ("All files", "*.*"),
            ]
        )
        if not path:
            return

        lower = path.lower()
        if not (lower.endswith(".png") or lower.endswith(".jpg")
                or lower.endswith(".jpeg") or lower.endswith(".webp")):
            if self.original_format in ("JPEG", "JPG"):
                path += ".jpg"
            elif self.original_format == "WEBP":
                path += ".webp"
            else:
                path += ".png"

        out = self.original
        if self.tool == "crop":
            if not self.rect_coords:
                messagebox.showwarning("Внимание", "Няма избрана област за кроп!")
                return
            x1, y1, x2, y2 = self.rect_coords
            left = int(x1 / self.scale)
            top = int(y1 / self.scale)
            right = int(x2 / self.scale)
            bottom = int(y2 / self.scale)
            ow, oh = self.original.size
            left = max(0, min(left, ow - 1))
            top = max(0, min(top, oh - 1))
            right = max(left + 1, min(right, ow))
            bottom = max(top + 1, min(bottom, oh))
            out = self.original.crop((left, top, right, bottom))
        elif self.tool == "resize" and self.resize_out:
            rw, rh = self.resize_out
            out = self.original.resize((max(1, rw), max(1, rh)), Image.LANCZOS)

        try:
            if path.lower().endswith((".jpg", ".jpeg")):
                if out.mode in ("RGBA", "P"):
                    out = out.convert("RGB")
                out.save(path, format="JPEG", quality=100, subsampling=0, optimize=False)
            elif path.lower().endswith(".webp"):
                if out.mode in ("RGBA", "P"):
                    out.save(path, format="WEBP", lossless=True)
                else:
                    out.save(path, format="WEBP", quality=100)
            else:
                out.save(path, format="PNG", compress_level=0)
            messagebox.showinfo("Готово", f"Запазено успешно:\n{path}")
        except Exception as e:
            messagebox.showerror("Грешка при запазване", str(e))


if __name__ == "__main__":
    start_file = sys.argv[1] if len(sys.argv) > 1 else None
    AdvancedCropper(start_file)
