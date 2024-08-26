import cv2
from matplotlib import pyplot as plt
import pytesseract
import os

def load_image(filepath):
    image = cv2.imread(filepath)
    return image


def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Binarization
    _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
    return binary

def extract_text(image):
    text = pytesseract.image_to_string(image)
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
            item_name = item.split()[0]
            item_price = float(item.split()[-1])
            if item_name in sales_data:
                sales_data[item_name] += item_price
            else:
                sales_data[item_name] = item_price
    return sales_data

def visualize_sales(sales_data):
    items = list(sales_data.keys())
    prices = list(sales_data.values())

    plt.bar(items, prices, color='blue')
    plt.xlabel('Items')
    plt.ylabel('Sales ($)')
    plt.title('Sales Summary')
    plt.show()

def main():
    image_paths = ['receipt1.jpg', 'receipt2.jpg']  # Example image files
    summaries = []

    for path in image_paths:
        image = load_image(path)
        processed_image = preprocess_image(image)
        text = extract_text(processed_image)
        summary = summarize_receipt(text)
        summaries.append(summary)

    sales_data = accumulate_sales_data(summaries)
    visualize_sales(sales_data)

if _name_ == '_main_':
    main()