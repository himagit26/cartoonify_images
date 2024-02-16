import cv2
import easygui
import matplotlib.pyplot as plt
import matplotlib.cbook as cbook
import os
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import ImageTk, Image
from datetime import datetime

class CartoonifyApp:
    def __init__(self, master):
        self.master = master
        self.master.geometry('600x600')
        self.master.title('Cartoonify Your Images!')
        self.master.configure(background='violet')

        self.processed_images = []  # List to store cartoonified images

        # Create UI elements
        self.label = tk.Label(self.master, background='#CDCDCD', font=('calibri', 20, 'bold'))
        self.label.config(text="Hello toonies!")
        self.label.pack()

        self.upload_button = tk.Button(self.master, text="Cartoonify an Image", command=self.upload_images, padx=10, pady=5)
        self.upload_button.configure(background='#364156', foreground='white', font=('arial', 18, 'bold'))
        self.upload_button.pack(side=tk.TOP, pady=10)

        self.save_button = tk.Button(self.master, text="Save All Cartoon Images", command=self.save_images, padx=10, pady=5)
        self.save_button.configure(background='#364156', foreground='white', font=('arial', 18, 'bold'))
        self.save_button.pack(side=tk.TOP, pady=10)

        self.progress_bar = ttk.Progressbar(self.master, orient="horizontal", length=400, mode="determinate")
        self.progress_bar.pack(pady=10)

        self.combo_label = tk.Label(self.master, text="Select Cartoonification Style:", font=('calibri', 14))
        self.combo_label.pack(pady=5)
        self.cartoon_style = tk.StringVar()
        self.cartoon_style.set("Default")
        self.cartoon_styles = ["Default", "Comic", "Watercolor", "Pencil Sketch"]
        self.style_combobox = ttk.Combobox(self.master, values=self.cartoon_styles, textvariable=self.cartoon_style)
        self.style_combobox.pack(pady=5)

        self.filter_label = tk.Label(self.master, text="Select Image Filter/Effect:", font=('calibri', 14))
        self.filter_label.pack(pady=5)
        self.selected_filters = []
        self.filter_var1 = tk.IntVar()
        self.filter_var2 = tk.IntVar()
        self.filter_var3 = tk.IntVar()
        self.filter_var4 = tk.IntVar()
        self.filter_checkboxes = [
            tk.Checkbutton(self.master, text="Brightness", variable=self.filter_var1),
            tk.Checkbutton(self.master, text="Contrast", variable=self.filter_var2),
            tk.Checkbutton(self.master, text="Saturation", variable=self.filter_var3),
            tk.Checkbutton(self.master, text="Blur", variable=self.filter_var4),
        ]
        for checkbox in self.filter_checkboxes:
            checkbox.pack(anchor=tk.W)

    def upload_images(self):
        image_paths = easygui.fileopenbox(multiple=True)
        if image_paths:
            for image_path in image_paths:
                self.cartoonify(image_path)

    def cartoonify(self, image_path):
        original_img = cv2.imread(image_path)
        original_img = cv2.cvtColor(original_img, cv2.COLOR_BGR2RGB)

        if original_img is None:
            messagebox.showerror("Error", f"Can not find any image. Choose an appropriate file: {image_path}")
            return self.update_progress(10)

        # Apply selected filters/effects
        modified_img = original_img.copy()
        for i, var in enumerate([self.filter_var1, self.filter_var2, self.filter_var3, self.filter_var4]):
            if var.get() == 1:
                if i == 0:  # Brightness
                    modified_img = self.adjust_brightness(modified_img)
                elif i == 1:  # Contrast
                    modified_img = self.adjust_contrast(modified_img)
                elif i == 2:  # Saturation
                    modified_img = self.adjust_saturation(modified_img)
                elif i == 3:  # Blur
                    modified_img = cv2.GaussianBlur(modified_img, (15, 15), 0)

                # Apply cartoonification style
                cartoon_img = self.cartoonify_image(modified_img)
                self.processed_images.append(cartoon_img)
                self.display_images([original_img, cartoon_img])


    def save_images(self):
        if not self.processed_images:
            messagebox.showwarning("No Images", "No cartoonified images to save.")
            return

        folder_selected = filedialog.askdirectory()
        if folder_selected:
            for i, cartoon_img in enumerate(self.processed_images):
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                filename = os.path.join(folder_selected, f"cartoonified_image_{timestamp}_{i + 1}.jpg")
                cv2.imwrite(filename, cv2.cvtColor(cartoon_img, cv2.COLOR_RGB2BGR))
                print(f"Image {i + 1} saved at {filename}")

    def update_progress(self, progress_value):
        self.progress_bar['value'] = progress_value
        self.master.update_idletasks()

    def display_images(self, images):
        fig, axes = plt.subplots(
            1, 2, figsize=(10, 5), subplot_kw={'xticks': [], 'yticks': []},
            gridspec_kw=dict(hspace=0.1, wspace=0.1)
        )
        for i, ax in enumerate(axes.flat):
            ax.imshow(images[i], cmap='gray')
        plt.show()

    def adjust_brightness(self, image):
        # Adjust brightness
        alpha = 1.5  # Increase or decrease to change brightness
        beta = 50    # Increase or decrease to change brightness
        adjusted = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
        return adjusted

    def adjust_contrast(self, image):
        # Adjust contrast
        alpha = 1.5  # Increase or decrease to change contrast
        adjusted = cv2.convertScaleAbs(image, alpha=alpha)
        return adjusted

    def adjust_saturation(self, image):
        # Adjust saturation
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        hsv[:, :, 1] = 1.5 * hsv[:, :, 1]  # Increase or decrease to change saturation
        adjusted = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
        return adjusted

    def cartoonify_image(self, image):
        # Convert image to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

        # Apply median blur to reduce noise
        gray = cv2.medianBlur(gray, 5)

        # Detect edges using adaptive thresholding
        edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)

        # Apply bilateral filter to smooth the image while preserving edges
        color = cv2.bilateralFilter(image, 9, 300, 300)

        # Combine color image with edges
        cartoon = cv2.bitwise_and(color, color, mask=edges)

        # Apply different cartoonification styles
        cartoon_styles = {
            "Default": cartoon,
            "Comic": cv2.stylization(image, sigma_s=150, sigma_r=0.25),
            "Watercolor": cv2.stylization(image, sigma_s=60, sigma_r=0.5),
            "Pencil Sketch": cv2.pencilSketch(image, sigma_s=60, sigma_r=0.07, shade_factor=0.05)
        }

        # Select the desired cartoonification style
        selected_style = self.cartoon_style.get()
        if selected_style in cartoon_styles:
            cartoon = cartoon_styles[selected_style]

        return cartoon



def main():
    root = tk.Tk()
    app = CartoonifyApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
