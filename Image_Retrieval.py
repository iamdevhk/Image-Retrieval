import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import cv2
import numpy as np

#Use resampling to avoid antialias depreciation
ANTIALIAS = Image.Resampling.LANCZOS if hasattr(Image, "Resampling") else Image.ANTIALIAS

#Function to load and display the next set of 20 images
def load_next_set():
    global current_page
    print(current_page)
    setButtonState(current_page + 2, 'next')
    current_page += 1
    display_images()

#Function to set state of pagination buttons
def setButtonState(current_page, event):
    if current_page == 0:
        prev_page_button.state(["disabled"])
        next_page_button.state(["!disabled"])
    elif current_page == 1 and event == 'prev':
        prev_page_button.state(["disabled"])
    elif current_page == 5 and event == 'next':
        next_page_button.state(["disabled"])
    else:
        next_page_button.state(["!disabled"])
        prev_page_button.state(["!disabled"])

#Function to load previous set of images
def load_prev_set():
    global current_page
    setButtonState(current_page, 'prev')
    current_page -= 1
    display_images()


#Function to select an image
def select_image(index):
    selected_image.set(index)
    display_selected_image()

#Function to set the state of previous button for initial load
def setState():
    prev_page_button.state(["disabled"])

#Function to display the selected image
def display_selected_image():
    selected_index = selected_image.get()
    if 0 <= selected_index < len(image_paths):
        img = Image.open(image_paths[selected_index])
        img = img.resize((400, 400), ANTIALIAS)  # Adjust the size as needed
        img = ImageTk.PhotoImage(img)
        selected_image_label.configure(image=img)
        selected_image_label.image = img
        selected_image_name_label.configure(text=os.path.basename(image_paths[selected_index]))

#Function to display all the images in the thumbnail grid with its names       
def display_images():
    for i in range(current_page * per_page, min(len(image_paths), (current_page + 1) * per_page)):
        img = Image.open(image_paths[i])
        img.thumbnail((80, 80), ANTIALIAS)  # Adjust the size as needed
        img = ImageTk.PhotoImage(img)

        # Update the thumbnail button and label with the image and name
        thumbnail_buttons[i % per_page].configure(image=img, command=lambda i=i: select_image(i))
        thumbnail_buttons[i % per_page].image = img
        thumbnail_labels[i % per_page]['text'] = os.path.basename(image_paths[i])


#Function to sort images by intensity 
def sort_images_by_intensity():

    # Sort images based on intensity histogram similarity to the selected image
    global image_paths
    selected_index = selected_image.get()
    file_path=image_paths[selected_index]

    if 0 <= selected_index < len(image_paths):
        #calculate intensity histogram for selecetd image
        selected_hist = calculate_intensity(selected_index)

        # Create a list of image paths and their corresponding Manhattan distances
        image_distances = [(i, calculate_manhattan_distance(selected_hist, i)) for i in range(len(image_paths))]

        # Sort the images based on Manhattan distances
        image_distances.sort(key=lambda x: x[1])

        # Update the image_paths list with the sorted order
        image_paths = [image_paths[i] for i, _ in image_distances]
        selected_index=image_paths.index(file_path)
        selected_image.set(selected_index)
        # Reset the current page and display the images
        global current_page
        current_page = 0
        setButtonState(current_page, 'next')
        display_images()

#Function to calculate the intenisty hsitogram
def calculate_intensity(index):
    #read the image
    image = cv2.imread(image_paths[index])

    # Convert the image to grayscale using opencv
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Calculate the intensity for each pixel in the iamge
    intensity_image = 0.299 * gray_image + 0.587 * gray_image + 0.114 * gray_image

    # Define the histogram bins
    hist_bins = [0, 10, 20, 30, 40, 50, 60,70,80,90,100,110,120,130,140,150,160,170,180,190,200,210,220,230, 240, 255]

    # Calculate the histogram using numpy
    hist, _ = np.histogram(intensity_image, bins=hist_bins)

    #alculate the total pixels in image
    total_pixels = intensity_image.size

    #find the normalised histogram by dividing it with total_pixels
    normalized_histogram = hist / total_pixels

    return normalized_histogram

def calculate_manhattan_distance(hist1, index2):
    # Calculate the Manhattan distance between two histograms
    hist2 = calculate_intensity(index2)
    return np.sum(np.abs(hist1 - hist2))

def calculate_manhattan_distance_CC(hist1, index2):
    # Calculate the Manhattan distance between two histograms
    hist2 =calculate_color_code(index2)
    return np.sum(np.abs(hist1[0] - hist2[0] ))

#Function to sort images based on color code
def sort_images_by_color_Code():
    # Sort images based on color code histogram similarity to the selected image
    global image_paths
    
    selected_index = selected_image.get()
    file_path=image_paths[selected_index]
    if 0 <= selected_index < len(image_paths):
        selected_hist = calculate_color_code(selected_index)
        
        # Create a list of image paths and their corresponding Manhattan distances
        image_distances = [(i, calculate_manhattan_distance_CC(selected_hist, i)) for i in range(len(image_paths))]

        # Sort the images based on Manhattan distances
        image_distances.sort(key=lambda x: x[1])

        # Update the image_paths list with the sorted order
        image_paths = [image_paths[i] for i, _ in image_distances]
        selected_index=image_paths.index(file_path)
        selected_image.set(selected_index)
        # Reset the current page and display the images
        global current_page
        current_page = 0
        setButtonState(current_page, 'next')
        display_images()

#Function to calculate the color code histogram using numpy
def calculate_color_code(index):
    img = Image.open(image_paths[index])
    img_np_array = np.array(img)
    # below line extracts most most significant 2 bits of each color code
    color_code = ((img_np_array[:, :, 0] & 0xC0) >> 6) << 4 | ((img_np_array[:, :, 1] & 0xC0) >> 6) << 2 | ((img_np_array[:, :, 2] & 0xC0) >> 6)

    return np.histogram(color_code.flatten(), bins=np.arange(65))

#function to reset to initial viewing state
def reset_images():
    global image_paths, current_page
    image_paths = original_image_paths[:]
    current_page = 0
    select_page(1)
    setButtonState(current_page, 'next')
    selected_image.set(0)
    display_selected_image()
    display_images()
    
    

# Create the main window
root = tk.Tk()
root.title("Image Analysis Viewer")
root.state('zoomed')

# Create a frame to display the current page
text_frame = tk.Frame(root, bg="#A9A9A9")
text_frame.pack(fill="x")

# Create a label with the header text and background color
top_label = tk.Label(text_frame, text="Image Analysis - Assignment1", bg="#A9A9A9", fg="white", font=("Arial", 16))
top_label.pack(fill="x")

# Create a list of image paths from a folder uses relative path
image_folder = r".\\images" 
image_paths = [os.path.join(image_folder, filename) for filename in os.listdir(image_folder) if filename.endswith((".jpg", ".png"))]
image_paths = sorted(image_paths, key=lambda path: int(path.split('\\')[-1].replace('.jpg', '')))

original_image_paths=image_paths[:]
# Initialize variables for the page
per_page = 20
current_page = 0



selected_image = tk.IntVar(value=0)
selected_image_frame = ttk.Frame(root, borderwidth=2, relief="solid")

selected_image_frame.pack(padx=(100, 5))
selected_image_name_label = ttk.Label(selected_image_frame, text="")
selected_image_name_label.pack()
selected_image_label = ttk.Label(selected_image_frame)
selected_image_label.pack()

# Create a frame to hold the buttons
button_frame = selected_image_frame
button_frame.pack(side=tk.LEFT, pady=5)

# Create three buttons and pack them to display horizontally next to each other
button2 = tk.Button(button_frame, text="Reset", command=reset_images)
button2.pack(side=tk.RIGHT, padx=5, pady=5)

button2 = tk.Button(button_frame, text="Sort by Intensity", command=sort_images_by_intensity)
button2.pack(side=tk.RIGHT, padx=5, pady=5)

button3 = tk.Button(button_frame, text="Sort by Color Code", command=sort_images_by_color_Code)
button3.pack(side=tk.RIGHT, padx=5, pady=5)

# Create and display the thumbnail grid
thumbnail_frame = ttk.Frame(root)
thumbnail_frame.pack(padx=(20, 10), pady=(40, 5), fill="none")

thumbnail_buttons = []
thumbnail_labels = []

for i in range(per_page):
    thumbnail_frame_row = i // 4
    thumbnail_frame_col = i % 4
    
    thumbnail_button = ttk.Button(thumbnail_frame, image='', command=lambda i=i: select_image(i))
    thumbnail_buttons.append(thumbnail_button)
    thumbnail_button.grid(row=thumbnail_frame_row * 2, column=thumbnail_frame_col, padx=5, pady=2)
    
    # Create labels for image names and display them below the thumbnails
    image_name = os.path.basename(image_paths[i])
    thumbnail_label = ttk.Label(thumbnail_frame, text=image_name)
    thumbnail_labels.append(thumbnail_label)
    thumbnail_label.grid(row=thumbnail_frame_row * 2 + 1, column=thumbnail_frame_col, padx=5,pady=2)

# Create and display the pagination control
pagination_frame = ttk.Frame(root)
pagination_frame.pack()

prev_page_button = ttk.Button(pagination_frame, text="Prev Page", command=load_prev_set)
prev_page_button.grid(row=0, column=0)

next_page_button = ttk.Button(pagination_frame, text="Next Page", command=load_next_set)
next_page_button.grid(row=0, column=1)

pagination_buttons = []

# create pagination buttons 5 in this case
for page_num in range(1, 6):
    button = ttk.Button(pagination_frame, text=str(page_num), command=lambda page=page_num: select_page(page))
    pagination_buttons.append(button)
    button.grid(row=0, column=page_num + 1)
    
    
# Function to select a specific page in the pagination, it also handles the prev and next button states
def select_page(page):
    global current_page
    current_page = page - 1
    setButtonState(current_page, 'next')
    if(page==5):
        setButtonState(page, 'next')
    
    display_images()

#set button state and call display images
setState()
display_images()

# Initialize the GUI
display_selected_image()
#set the background color for the GUI
root.configure(background='#D3D3D3')
root.mainloop()