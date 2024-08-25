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

def summarize_receipt(text):
    lines = text.split('\n')
    summary = {'Items': [], 'Total': None}
    for line in lines:
        if 'Total' in line:
            summary['Total'] = line.split()[-1]
        else:
            summary['Items'].append(line)
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