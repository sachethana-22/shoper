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