import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
import threading


class WatermarkApp:
    def __init__(self, root):
        self.root = root
        self.root.title("图片批量水印工具 - Image Watermark Tool")
        self.root.geometry("1200x850")
        self.root.minsize(1100, 700)

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.image_list = []
        self.watermark_path = None
        self.watermark_image = None
        self.preview_image = None
        self.preview_photo = None

        self.watermark_position = "bottom-right"
        self.watermark_size = 0.15
        self.watermark_opacity = 128

        self.create_widgets()

    def create_widgets(self):
        main_container = ttk.Frame(self.root, padding="20")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_container.columnconfigure(0, weight=1)
        main_container.columnconfigure(1, weight=1)
        main_container.rowconfigure(4, weight=1)

        # ===== 标题 =====
        title_frame = ttk.Frame(main_container)
        title_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))

        title = ttk.Label(title_frame, text="图片批量水印工具", font=('Microsoft YaHei', 24, 'bold'))
        title.pack(side=tk.LEFT)

        subtitle = ttk.Label(title_frame, text="Batch Watermark Tool", font=('Microsoft YaHei', 12))
        subtitle.pack(side=tk.LEFT, padx=(15, 0), pady=(5, 0))

        ttk.Separator(main_container, orient='horizontal').grid(
            row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20)
        )

        # ===== 左侧控制面板 =====
        control_frame = ttk.Frame(main_container)
        control_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 15))
        control_frame.columnconfigure(0, weight=1)

        # -- 1. 图片选择 --
        section1 = ttk.LabelFrame(control_frame, text="📁 选择图片文件", padding="15")
        section1.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        section1.columnconfigure(0, weight=1)

        btn_frame1 = ttk.Frame(section1)
        btn_frame1.grid(row=0, column=0, sticky=(tk.W, tk.E))

        ttk.Button(btn_frame1, text="选择文件", command=self.select_files, width=15).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(btn_frame1, text="选择文件夹", command=self.select_folder, width=15).grid(row=0, column=1, padx=(0, 8))
        ttk.Button(btn_frame1, text="清空列表", command=self.clear_files, width=15).grid(row=0, column=2)

        self.file_label = ttk.Label(section1, text="未选择任何文件", font=('Microsoft YaHei', 9))
        self.file_label.grid(row=1, column=0, sticky=tk.W, pady=(10, 0))

        # -- 2. 水印设置 --
        section2 = ttk.LabelFrame(control_frame, text="🖼️ 水印设置", padding="15")
        section2.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        section2.columnconfigure(0, weight=1)

        ttk.Button(section2, text="选择水印图片", command=self.select_watermark, width=20).grid(
            row=0, column=0, columnspan=2, sticky=tk.W
        )

        self.watermark_label = ttk.Label(section2, text="未选择水印文件", font=('Microsoft YaHei', 9), foreground='#666')
        self.watermark_label.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(5, 15))

        ttk.Separator(section2, orient='horizontal').grid(
            row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15)
        )

        param_frame = ttk.Frame(section2)
        param_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E))

        ttk.Label(param_frame, text="水印大小：", font=('Microsoft YaHei', 10)).grid(row=0, column=0, sticky=tk.W)
        self.size_scale = ttk.Scale(
            param_frame, from_=0.05, to=0.5, orient=tk.HORIZONTAL,
            length=200, value=0.15, command=self.update_watermark_params
        )
        self.size_scale.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        self.size_value_label = ttk.Label(param_frame, text="15%", font=('Microsoft YaHei', 10), width=6)
        self.size_value_label.grid(row=0, column=2, sticky=tk.W)

        ttk.Label(param_frame, text="透明度：", font=('Microsoft YaHei', 10)).grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.opacity_scale = ttk.Scale(
            param_frame, from_=50, to=255, orient=tk.HORIZONTAL,
            length=200, value=128, command=self.update_watermark_params
        )
        self.opacity_scale.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=(10, 0))
        self.opacity_value_label = ttk.Label(param_frame, text="50%", font=('Microsoft YaHei', 10), width=6)
        self.opacity_value_label.grid(row=1, column=2, sticky=tk.W, pady=(10, 0))

        # -- 3. 位置选择 --
        section3 = ttk.LabelFrame(control_frame, text="📍 水印位置", padding="15")
        section3.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        section3.columnconfigure(0, weight=1)

        self.position_var = tk.StringVar(value="bottom-right")
        positions = [
            ("左上", "top-left", 0, 0),
            ("右上", "top-right", 0, 1),
            ("左下", "bottom-left", 1, 0),
            ("右下", "bottom-right", 1, 1)
        ]

        grid_frame = ttk.Frame(section3)
        grid_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        grid_frame.columnconfigure((0, 1), weight=1)
        grid_frame.rowconfigure((0, 1), weight=1)

        for label, value, row, col in positions:
            rb = ttk.Radiobutton(
                grid_frame, text=label, variable=self.position_var,
                value=value, command=self.update_position, width=10
            )
            rb.grid(row=row, column=col, padx=8, pady=8, sticky=(tk.W, tk.E))

        # -- 4. 批处理 --
        section4 = ttk.LabelFrame(control_frame, text="⚡ 批处理", padding="15")
        section4.grid(row=3, column=0, sticky=(tk.W, tk.E))
        section4.columnconfigure(0, weight=1)

        progress_frame = ttk.Frame(section4)
        progress_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))

        self.progress = ttk.Progressbar(progress_frame, length=250, mode='determinate')
        self.progress.grid(row=0, column=0, sticky=tk.W)

        self.progress_label = ttk.Label(progress_frame, text="0 / 0", font=('Microsoft YaHei', 10), width=8)
        self.progress_label.grid(row=0, column=1, padx=(10, 0))

        ttk.Button(
            section4, text="开始批量处理", command=self.start_processing,
            width=25, style='Accent.TButton'
        ).grid(row=1, column=0, sticky=tk.W, pady=(15, 0))

        style = ttk.Style()
        style.configure('Accent.TButton', font=('Microsoft YaHei', 10, 'bold'))

        # 状态栏
        status_frame = ttk.Frame(control_frame)
        status_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(20, 0))

        self.status_var = tk.StringVar(value="就绪 - 准备开始")
        status_bar = ttk.Label(
            status_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W,
            font=('Microsoft YaHei', 9), padding=(5, 3)
        )
        status_bar.pack(fill=tk.X)

        # ===== 右侧预览面板 =====
        preview_container = ttk.Frame(main_container)
        preview_container.grid(row=2, column=1, rowspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        preview_container.columnconfigure(0, weight=1)
        preview_container.rowconfigure(1, weight=1)

        preview_title = ttk.Label(
            preview_container, text="预览效果", font=('Microsoft YaHei', 14, 'bold')
        )
        preview_title.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))

        preview_frame = ttk.LabelFrame(preview_container, text="实时预览", padding="15")
        preview_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(preview_frame, bg='#f0f0f0', width=680, height=500, highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        hint_label = ttk.Label(
            preview_frame,
            text="提示：选择图片和水印后将在此显示预览",
            font=('Microsoft YaHei', 9, 'italic'),
            foreground='#666'
        )
        hint_label.grid(row=1, column=0, sticky=tk.W, pady=(10, 0))

    def select_files(self):
        files = filedialog.askopenfilenames(
            title="选择图片文件",
            filetypes=[("图片文件", "*.png *.jpg *.jpeg *.bmp *.gif"), ("所有文件", "*.*")]
        )
        if files:
            self.image_list = list(files)
            self.file_label.config(text=f"已选择 {len(self.image_list)} 张图片")
            self.load_preview()

    def select_folder(self):
        folder = filedialog.askdirectory(title="选择图片文件夹")
        if folder:
            image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.gif'}
            self.image_list = []
            for file in os.listdir(folder):
                if file.lower().endswith(tuple(image_extensions)):
                    self.image_list.append(os.path.join(folder, file))
            self.file_label.config(text=f"已选择 {len(self.image_list)} 张图片")
            if self.image_list:
                self.load_preview()

    def clear_files(self):
        self.image_list = []
        self.file_label.config(text="未选择任何文件")
        self.canvas.delete("all")
        self.progress['value'] = 0
        self.progress_label.config(text="0 / 0")
        self.status_var.set("就绪 - 准备开始")

    def select_watermark(self):
        file = filedialog.askopenfilename(
            title="选择水印图片",
            filetypes=[("图片文件", "*.png *.jpg *.jpeg"), ("所有文件", "*.*")]
        )
        if file:
            self.watermark_path = file
            self.watermark_label.config(text=f"{os.path.basename(file)}")
            self.load_watermark()
            self.load_preview()

    def load_watermark(self):
        if self.watermark_path and os.path.exists(self.watermark_path):
            self.watermark_image = Image.open(self.watermark_path).convert('RGBA')

    def load_preview(self):
        if not self.image_list or not self.watermark_image:
            return

        img = Image.open(self.image_list[0]).convert('RGBA')
        max_size = (680, 500)
        img.thumbnail(max_size, Image.Resampling.LANCZOS)

        self.preview_image = img
        self.update_preview()

    def update_position(self):
        self.watermark_position = self.position_var.get()
        self.update_preview()

    def update_watermark_params(self, event=None):
        self.watermark_size = self.size_scale.get()
        self.watermark_opacity = int(self.opacity_scale.get())

        size_percent = int(self.watermark_size * 100)
        self.size_value_label.config(text=f"{size_percent}%")

        opacity_percent = int((self.watermark_opacity / 255) * 100)
        self.opacity_value_label.config(text=f"{opacity_percent}%")

        self.update_preview()

    def update_preview(self):
        if not self.preview_image or not self.watermark_image:
            return

        preview = self.preview_image.copy()

        watermark_width = int(preview.width * self.watermark_size)
        watermark_height = int(
            self.watermark_image.height * (watermark_width / self.watermark_image.width)
        )
        watermark = self.watermark_image.resize(
            (watermark_width, watermark_height), Image.Resampling.LANCZOS
        )

        if self.watermark_opacity < 255:
            alpha = watermark.split()[3]
            alpha = alpha.point(lambda p: int(p * (self.watermark_opacity / 255)))
            watermark.putalpha(alpha)

        margin = int(preview.width * 0.02)

        if self.watermark_position == "top-left":
            x, y = margin, margin
        elif self.watermark_position == "top-right":
            x, y = preview.width - watermark_width - margin, margin
        elif self.watermark_position == "bottom-left":
            x, y = margin, preview.height - watermark_height - margin
        elif self.watermark_position == "bottom-right":
            x, y = preview.width - watermark_width - margin, preview.height - watermark_height - margin

        preview.paste(watermark, (x, y), watermark)

        self.preview_photo = ImageTk.PhotoImage(preview)
        self.canvas.delete("all")
        self.canvas.config(width=preview.width, height=preview.height)
        self.canvas.create_image(
            preview.width // 2,
            preview.height // 2,
            image=self.preview_photo,
            anchor=tk.CENTER
        )

    def calculate_position(self, img_width, img_height, watermark_width, watermark_height):
        margin = int(img_width * 0.02)

        if self.watermark_position == "top-left":
            return margin, margin
        elif self.watermark_position == "top-right":
            return img_width - watermark_width - margin, margin
        elif self.watermark_position == "bottom-left":
            return margin, img_height - watermark_height - margin
        elif self.watermark_position == "bottom-right":
            return img_width - watermark_width - margin, img_height - watermark_height - margin

    def start_processing(self):
        if not self.image_list:
            messagebox.showwarning("⚠️ 警告", "请先选择图片文件")
            return

        if not self.watermark_path:
            messagebox.showwarning("⚠️ 警告", "请先选择水印图片")
            return

        output_folder = filedialog.askdirectory(title="选择输出文件夹")
        if not output_folder:
            return

        self.status_var.set("正在批量处理图片...")
        self.root.update()

        thread = threading.Thread(target=self.process_images, args=(output_folder,))
        thread.start()

    def process_images(self, output_folder):
        total = len(self.image_list)
        watermark = Image.open(self.watermark_path).convert('RGBA')

        for i, image_path in enumerate(self.image_list):
            try:
                self.progress['value'] = (i + 1) / total * 100
                self.progress_label.config(text=f"{i + 1:3d} / {total}")
                self.status_var.set(f"正在处理: {os.path.basename(image_path)}")

                img = Image.open(image_path).convert('RGBA')

                watermark_width = int(img.width * self.watermark_size)
                watermark_height = int(watermark.height * (watermark_width / watermark.width))
                watermark_resized = watermark.resize((watermark_width, watermark_height), Image.Resampling.LANCZOS)

                if self.watermark_opacity < 255:
                    alpha = watermark_resized.split()[3]
                    alpha = alpha.point(lambda p: int(p * (self.watermark_opacity / 255)))
                    watermark_resized.putalpha(alpha)

                x, y = self.calculate_position(img.width, img.height, watermark_width, watermark_height)
                img.paste(watermark_resized, (x, y), watermark_resized)

                filename = os.path.basename(image_path)
                name, ext = os.path.splitext(filename)
                output_path = os.path.join(output_folder, f"{name}_watermarked{ext}")

                img = img.convert('RGB')
                img.save(output_path, quality=95)

            except Exception as e:
                print(f"❌ 处理失败 {image_path}: {e}")

        self.status_var.set("✅ 处理完成")
        messagebox.showinfo(
            "🎉 完成",
            f"成功处理 {total} 张图片\n\n输出文件夹:\n{output_folder}"
        )
        self.progress['value'] = 0
        self.progress_label.config(text="0 / 0")


def main():
    root = tk.Tk()

    try:
        style = ttk.Style()
        style.theme_use('clam')
    except:
        pass

    app = WatermarkApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
