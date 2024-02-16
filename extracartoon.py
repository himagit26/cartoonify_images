import cv2
import easygui
import sys
import matplotlib.pyplot as plt
import os
import tkinter as tk
from tkinter import simpledialog, ttk
from tkinter import filedialog
from tkinter import *
from PIL import ImageTk, Image
from datetime import datetime
from tqdm import tqdm  # For progress bar

top = tk.Tk()
top.geometry('400x400')
top.title('Cartoonify Your Image!')
top.configure(background='violet')
label = Label(top, background='#CDCDCD', font=('calibri', 20, 'bold'))
label.config(text="Hello toonies !")
label.pack()
processed_images = []  # List to store cartoonified images

def upload():
    ImagePaths = easygui.fileopenbox(multiple=True)
    for ImagePath in ImagePaths:
        try:
            cartoonify(ImagePath)
        except Exception as e:
            print(f"Error processing {ImagePath}: {e}")

def resize_image(img, width, height):
    return cv2.resize(img, (width, height))

def convert_to_gray(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

def apply_median_blur(img, kernel_size):
    return cv2.medianBlur(img, kernel_size)

def edge_detection(img, threshold_type=cv2.ADAPTIVE_THRESH_MEAN_C, block_size=9, constant=9):
    return cv2.adaptiveThreshold(img, 255, threshold_type, cv2.THRESH_BINARY, block_size, constant)

def apply_bilateral_filter(img, d, sigma_color, sigma_space):
    return cv2.bilateralFilter(img, d, sigma_color, sigma_space)

def display_images(images):
    fig, axes = plt.subplots(
        3, 2, figsize=(8, 8), subplot_kw={'xticks': [], 'yticks': []},
        gridspec_kw=dict(hspace=0.1, wspace=0.1)
    )
    for i, ax in enumerate(axes.flat):
        ax.imshow(images[i], cmap='gray')
    plt.show()

def cartoonify(ImagePath):
    original_img = cv2.imread(ImagePath)
    original_img = cv2.cvtColor(original_img, cv2.COLOR_BGR2RGB)

    if original_img is None:
        raise ValueError("Can not find any image. Choose an appropriate file.")

    update_progress(10)
    resized_img = resize_image(original_img, 960, 540)
    update_progress(30)

    gray_img = convert_to_gray(original_img)
    resized_gray_img = resize_image(gray_img, 960, 540)
    update_progress(50)

    smooth_gray_img = apply_median_blur(gray_img, 5)
    resized_smooth_gray_img = resize_image(smooth_gray_img, 960, 540)
    update_progress(70)

    edge_img = edge_detection(smooth_gray_img)
    resized_edge_img = resize_image(edge_img, 960,540)
    update_progress(90)

    color_img = apply_bilateral_filter(original_img, 9, 300, 300)
    resized_color_img = resize_image(color_img, 960, 540)
    update_progress(100)

    cartoon_img = cv2.bitwise_and(color_img, color_img, mask=edge_img)
    resized_cartoon_img = resize_image(cartoon_img, 960, 540)

    processed_images.append(cartoon_img)
    display_images([resized_img, resized_gray_img, resized_smooth_gray_img, resized_edge_img, resized_color_img,
                    resized_cartoon_img])

def save():
    for i, cartoon_img in enumerate(processed_images):
        custom_name = simpledialog.askstring("Input",
                                             f"Enter your custom name for cartoon image {i + 1} (or leave blank for auto-generated name):")

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        if custom_name:
            filename = f"{custom_name}.jpg"
        else:
            filename = f"cartoonified_image_{timestamp}_{i + 1}.jpg"

        path = os.path.join(os.getcwd(), filename)
        cv2.imwrite(path, cv2.cvtColor(cartoon_img, cv2.COLOR_RGB2BGR))
        print(f"Image {i + 1} saved at {path}")

def update_progress(progress_value):
    progress_bar['value'] = progress_value
    top.update_idletasks()

upload_button = Button(top, text="Cartoonify an Image", command=upload, padx=10, pady=5)
upload_button.configure(background='#364156', foreground='white', font=('arial', 18, 'bold'))
upload_button.pack(side=TOP, pady=50)

save_button = Button(top, text="Save All Cartoon Images", command=save, padx=10, pady=5)
save_button.configure(background='#364156', foreground='white', font=('arial', 18, 'bold'))
save_button.pack(side=TOP, pady=10)

progress_bar = ttk.Progressbar(top, orient="horizontal", length=200, mode="determinate")
progress_bar.pack(pady=10)

top.mainloop()
