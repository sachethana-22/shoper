import cv2
import numpy as np
from matplotlib import pyplot as plt
import pytesseract
import os
from PIL import Image, ImageEnhance, ImageFilter

#path to tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'


def display_image(title, image):
    #Display an image with a title.
    plt.figure(figsize=(10, 10))
    plt.title(title)
    if len(image.shape) == 3:
        # Color image
        plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    else:
        # Grayscale image
        plt.imshow(image, cmap='gray')
    plt.axis('off')
    plt.show()

def resize_image(image, scale_percent, interpolation_method):
    #Resize the image 
    width = int(image.shape[1] * scale_percent / 100)
    height = int(image.shape[0] * scale_percent / 100)
    dim = (width, height)
    
    resized_image = cv2.resize(image, dim, interpolation=interpolation_method)
    return resized_image

def preprocess_image(image_paths):
    image = cv2.imread(image_paths)

    if image is None:
        print("Error: Image not found.")
        return None

    # Display original image
    display_image("Original Image", image)

    # interpolation methods
    interpolation_methods = {
        'Nearest': cv2.INTER_NEAREST,
        'Linear': cv2.INTER_LINEAR,
        'Cubic': cv2.INTER_CUBIC,
        'Lanczos4': cv2.INTER_LANCZOS4
    }

    scale_percent = 200  # Scale image to 200% of original size
    
    for name, method in interpolation_methods.items():
        resized_image = resize_image(image, scale_percent, method)
        display_image(f"Resized Image-Using {name} interpolation.", resized_image)

    # Convert to grayscale
    gray = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY)
    display_image("Converted to grayscale.", gray)

    # Apply Gaussian
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    display_image("Blurred Image-Applied Gaussian blur to reduce noise", blurred)

    # Apply adaptive thresholding
    adaptive_thresh = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    display_image("Adaptive Thresholding-Applied adaptive Gaussian thresholding", adaptive_thresh)

    # morphological transformations to improve text visibility
    kernel = np.ones((3, 3), np.uint8)
    morph = cv2.morphologyEx(adaptive_thresh, cv2.MORPH_CLOSE, kernel)
    display_image("Morphological Transformations-Applied morphological transformations", morph)

    # erosion and dilation to enhance text
    eroded = cv2.erode(morph, kernel, iterations=1)
    dilated = cv2.dilate(eroded, kernel, iterations=1)
    display_image("Eroded Image-Applied erosion", eroded)
    display_image("Dilated Image-Applied dilation", dilated)

    # Extract text using Tesseract 
    custom_config = r'--oem 3 --psm 6'  
    extracted_text = pytesseract.image_to_string(dilated, config=custom_config)

    return extracted_text

def format_number(text):
    try:
        # Replace commas with periods and remove spaces
        text = text.replace(',', '.').replace(' ', '')
        # Convert text to a float
        number = float(text)
        # Format with two decimal places
        formatted_number = f"{number:.2f}"
        return formatted_number
    except ValueError:
        return text.strip()

def summarize_receipt(text, output_file='summary.txt'):
    lines = text.split('\n')
    summary = {'Header': [],'Items': [], 'Footer': []}
    
    item_section = False

    for line in lines:
        if "Cashier" in line or "Bill" in line:
            summary["Header"].append(line.strip())
        elif "Sub Total" in line or "Cash" in line or "Change" in line:
            parts = line.split()
            formatted_parts = [format_number(part) if part.replace('.', '', 1).isdigit() else part for part in parts]
            summary["Footer"].append(" ".join(formatted_parts))
        elif line.strip() and not item_section:
            summary["Header"].append(line.strip())
        elif line.startswith("#"):
            item_section = True
            summary["Items"].append(line.strip())
        elif item_section:
            parts = line.split()
            formatted_parts = []
            for part in parts:
                if part.replace('.', ',', 1).isdigit():
                    if '.' in part:
                        formatted_parts.append(format_number(part))  # Price should have two decimal places
                    else:
                        formatted_parts.append(f"{int(part):.0f}")  # Quantity should not have decimals
                else:
                    formatted_parts.append(part)
            summary["Items"].append(" ".join(formatted_parts))
    
    return summary

def accumulate_sales_data(summary):
    print("\n" + "=" * 35)
    for Header in summary["Header"]:
        print(f"{Header:^35}")
    
    print("\n" + "-" * 35)
    for Items in summary["Items"]:
        print(f"{Items}")
    
    print("-" * 35)
    for Footer in summary["Footer"]:
        print(f"{Footer:<35}")
    print("=" * 35 + "\n")


def save_summary_to_text_file(summary, filename="C:/Users/hp/Documents/University/Year 04 Sem 02/CGV/GroupAssignment/FinalCourseWork/summary.txt"):
    try:
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        
        #get the text to the center of the text file
        line_width = 80
        def center_text(text,width):
            return text.center(width)
        
        # Write the summary to the text file
        with open(file_path, 'w') as file:
            if 'Header' in summary:
                for Header in summary['Header']:
                    file.write(f"{center_text(Header, line_width)}\n")
          
            if 'Items' in summary:
                for Items in summary['Items']:
                    file.write(f"{center_text(Items, line_width)}\n")
             
            if 'Footer' in summary:
                for Footer in summary['Footer']:
                    file.write(f"{center_text(Footer, line_width)}\n")
    
    except Exception as e:
        print(f"An error occurred while saving the file: {e}")

def main():
    image_paths = ['images/Recept1.png']  #image files
    summary = []

    # Clear the summary file before starting
    open('summary.txt', 'w').close()

    for image_path in image_paths:
        receipt_details = preprocess_image(image_path)
        if receipt_details:
            summary_details = summarize_receipt(receipt_details)
            accumulate_sales_data(summary_details)
            save_summary_to_text_file(summary_details, filename='summary.txt')
            summary.append(summary_details)

    if summary:
        save_summary_to_text_file(summary[0])  # Save the first summary as a sample


if __name__ == '__main__':
    main()