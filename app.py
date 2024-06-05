# backend/app.py
from flask import Flask, request, jsonify
import PyPDF2

app = Flask(__name__)

# Sample list of items with their sqft per piece and per box
items = [
    {"name": "Aloft", "sqftPerPiece": 2, "sqftPerBox": 36},
    {"name": "Arrington Gotham Grey", "sqftPerPiece": 1.5, "sqftPerBox": 36},
    # Add all other items here
]

@app.route('/upload', methods=['POST'])
def upload():
    if 'pdf' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['pdf']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    pdf_reader = PyPDF2.PdfFileReader(file)
    text = ""
    for page in range(pdf_reader.numPages):
        text += pdf_reader.getPage(page).extract_text()

    # Process the text to extract relevant information
    calculations = {}
    for item in items:
        qty = extract_qty(text, item['name'])
        if qty > 0:
            calculations[item['name']] = calculate(qty, item)

    return jsonify(calculations)

def extract_qty(text, item_name):
    lines = text.split('\n')
    for line in lines:
        if item_name in line:
            parts = line.split()
            for part in parts:
                if part.replace('.', '', 1).isdigit():
                    return float(part)
    return 0

def calculate(requested, item):
    sqftPerBox = item['sqftPerBox']
    sqftPerPiece = item['sqftPerPiece']

    maxBoxes = int(requested / sqftPerBox)
    boxes = 0
    pieces = 0
    actualSqFt = 0

    for b in range(maxBoxes, -1, -1):
        remainingSqFt = requested - (b * sqftPerBox)
        p = int(remainingSqFt / sqftPerPiece)
        totalSqFt = (b * sqftPerBox) + (p * sqftPerPiece)

        if totalSqFt <= requested:
            boxes = b
            pieces = p
            actualSqFt = totalSqFt
            break

    return {
        "boxes": boxes,
        "pieces": pieces,
        "actualSqFt": actualSqFt
    }

if __name__ == '__main__':
    app.run(debug=True)
