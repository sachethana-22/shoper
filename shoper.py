import cv2
import numpy as np
from matplotlib import pyplot as plt
import pytesseract
import os
from PIL import Image, ImageEnhance, ImageFilter

def load_image(filepath):
    image = cv2.imread(filepath)
    return image


def preprocess_image(image):
    # Resize image to a larger size for better OCR detection
    height, width = image.shape[:2]
    image = cv2.resize(image, (width * 2, height * 2), interpolation=cv2.INTER_LINEAR)
    
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Denoise the image
    denoised = cv2.fastNlMeansDenoising(gray, None, 30, 7, 21)
    
    # Sharpen the image
    sharpen_kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    sharpened = cv2.filter2D(denoised, -1, sharpen_kernel)
    
    return sharpened

def extract_text(image):
    pil_img = Image.fromarray(image)
    
    # Enhance the image quality
    enhancer = ImageEnhance.Contrast(pil_img)
    pil_img = enhancer.enhance(2)
    
    enhancer = ImageEnhance.Sharpness(pil_img)
    pil_img = enhancer.enhance(2)
    
    # Convert the enhanced image back to OpenCV format
    enhanced_image = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    
    # Use Tesseract to extract text
    custom_config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(enhanced_image, config=custom_config)
    return text

def summarize_receipt(text, output_file='summary.txt'):
    lines = text.split('\n')
    summary = {'Items': [], 'Total': None}
    
    with open(output_file, 'a') as file:  # Open the file in append mode
        for line in lines:
            if 'Total' in line:
                summary['Total'] = line.split()[-1]
                file.write(f"Total: {summary['Total']}\n")
            else:
                summary['Items'].append(line)
                file.write(f"Item: {line}\n")
        
        file.write("\n")  # Add a newline after each receipt summary
    
    print("Summary:")
    print(summary)
    return summary

def accumulate_sales_data(summaries):
    sales_data = {}
    for summary in summaries:
        for item in summary['Items']:
            parts = item.split()
            
            # Ensure there are at least two parts (item name and price)
            if len(parts) < 2:
                continue
            
            item_name = " ".join(parts[:-1])  # Item name could be more than one word
            item_price_str = parts[-1]

            try:
                # Attempt to convert the last part to a float
                item_price = float(item_price_str)
                
                if item_name in sales_data:
                    sales_data[item_name] += item_price
                else:
                    sales_data[item_name] = item_price

            except ValueError:
                # If conversion fails, print an error or skip
                print(f"Skipping line: {item} - Invalid price format")

    return sales_data

def visualize_sales(sales_data):
    items = list(sales_data.keys())
    prices = list(sales_data.values())

    plt.bar(items, prices, color='blue')
    plt.xlabel('Items')
    plt.ylabel('Sales ($)')
    plt.title('Sales Summary')
    plt.show()

def save_summary_to_text_file(summary, filename="C:/Users/hp/Documents/University/Year 04 Sem 02/CGV/GroupAssignment/FinalCourseWork/summary.txt"):
    try:
        # Get the absolute path of the directory where the script is running
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Join the script directory with the filename to ensure it's saved in the correct location
        file_path = os.path.join(script_dir, filename)
        
        # Write the summary to the text file
        with open(file_path, 'w') as file:
            for item in summary['Items']:
                file.write(f"{item}\n")
            if summary['Total']:
                file.write(f"\nTotal: {summary['Total']}\n")
        
        print(f"Summary saved to {file_path}")
    
    except Exception as e:
        print(f"An error occurred while saving the file: {e}")

def main():
    image_paths = ['images/Recept1.png', 'images/Recept2.png', 'images/Recept3.png', 'images/Recept4.png']  # Example image files
    summaries = []

    # Clear the summary file before starting (optional)
    open('summary.txt', 'w').close()

    for path in image_paths:
        image = load_image(path)
        processed_image = preprocess_image(image)
        text = extract_text(processed_image)
        summary = summarize_receipt(text, output_file='summary.txt')
        summaries.append(summary)

    sales_data = accumulate_sales_data(summaries)
    visualize_sales(sales_data)

if __name__ == '__main__':
    main()