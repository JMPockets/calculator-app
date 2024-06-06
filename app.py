from flask import Flask, request, send_file
import PyPDF2
from fpdf import FPDF
import io

app = Flask(__name__)

# Sample list of items with their sqft per piece and per box
items = [
    {"name": "Aloft", "sqftPerPiece": 2, "sqftPerBox": 36},
    {"name": "Arrington Gotham Grey", "sqftPerPiece": 1.5, "sqftPerBox": 36},
    {"name": "Broadstreet Cognac Oak", "sqftPerPiece": 2.33, "sqftPerBox": 51.39},
    {"name": "Cameron(Merbau)", "sqftPerPiece": 2.33, "sqftPerBox": 34.98},
    {"name": "Coretec Pro Plus", "sqftPerPiece": 2.4, "sqftPerBox": 28.84},
    {"name": "Dealer Solution", "sqftPerPiece": 2.00, "sqftPerBox": 54.00},
    {"name": "Downtown (Bourbon 12 mil)", "sqftPerPiece": 1.98, "sqftPerBox": 41.72},
    {"name": "Downtown (bourbon 8 mil)", "sqftPerPiece": 1.98, "sqftPerBox": 53.63},
    {"name": "DruidStone", "sqftPerPiece": 2.36, "sqftPerBox": 23.64},
    {"name": "Expo And Market Square", "sqftPerPiece": 1.99, "sqftPerBox": 53.93},
    {"name": "Firm Fit", "sqftPerPiece": 1.88, "sqftPerBox": 33.84},
    {"name": "Foundation 51.33", "sqftPerPiece": 2.33, "sqftPerBox": 51.33},
    {"name": "Freelay 4.7", "sqftPerPiece": 3, "sqftPerBox": 36},
    {"name": "Gluedown 2/8 Mil", "sqftPerPiece": 3, "sqftPerBox": 60},
    {"name": "GRANDE (Denali)", "sqftPerPiece": 2.33, "sqftPerBox": 32.7},
    {"name": "Homegrain", "sqftPerPiece": 1.93, "sqftPerBox": 52.3},
    {"name": "K-Trade pvp neutral", "sqftPerPiece": 2.33, "sqftPerBox": 51.34},
    {"name": "Katanga 2mm glue down", "sqftPerPiece": 2.33, "sqftPerBox": 51.39},
    {"name": "Katanga 4/12", "sqftPerPiece": 2.33, "sqftPerBox": 28.03},
    {"name": "Katanga 5/20", "sqftPerPiece": 2.4, "sqftPerBox": 28.83},
    {"name": "Lakeshore", "sqftPerPiece": 2, "sqftPerBox": 36},
    {"name": "Life Style (Caico, Playa, Aruba)", "sqftPerPiece": 1.96, "sqftPerBox": 23.64},
    {"name": "Limitless", "sqftPerPiece": 2.33, "sqftPerBox": 34.98},
    {"name": "Living Local", "sqftPerPiece": 2, "sqftPerBox": 36},
    {"name": "Lookout Mount (Signal & Lookout point)", "sqftPerPiece": 1.97, "sqftPerBox": 27.58},
    {"name": "Looselay (Stamford, Linosa, Hartford)", "sqftPerPiece": 2.82, "sqftPerBox": 33.9},
    {"name": "Looselay Longboard", "sqftPerPiece": 4, "sqftPerBox": 32.29},
    {"name": "Mainstreet", "sqftPerPiece": 2.33, "sqftPerBox": 51.39},
    {"name": "Marathon", "sqftPerPiece": 2.11, "sqftPerBox": 42.36},
    {"name": "marscarpone", "sqftPerPiece": 2.41, "sqftPerBox": 58},
    {"name": "Merbau Vangogh", "sqftPerPiece": 2.33, "sqftPerBox": 34.98},
    {"name": "Modernality Skyline", "sqftPerPiece": 1.98, "sqftPerBox": 41.72},
    {"name": "native origins", "sqftPerPiece": 1.99, "sqftPerBox": 35.95},
    {"name": "Natural Personality Heart Oak", "sqftPerPiece": 1.5, "sqftPerBox": 54},
    {"name": "Neutral Oak Looselay", "sqftPerPiece": 4.03, "sqftPerBox": 32.29},
    {"name": "Oyster Tile", "sqftPerPiece": 1.97, "sqftPerBox": 15.83},
    {"name": "Ozark 2 (Sugar Maple, Cumberland, Key Largo)", "sqftPerPiece": 2.32, "sqftPerBox": 51.24},
    {"name": "Rexford", "sqftPerPiece": 2.66, "sqftPerBox": 45.33},
    {"name": "Runner Up Copano Oak", "sqftPerPiece": 2.4, "sqftPerBox": 28.84},
    {"name": "Sherburn", "sqftPerPiece": 1.88, "sqftPerBox": 52.68},
    {"name": "Soundtec", "sqftPerPiece": 2.39, "sqftPerBox": 23.9},
    {"name": "surpass muse", "sqftPerPiece": 1.99, "sqftPerBox": 53.93},
    {"name": "Suspension Chassis", "sqftPerPiece": 2.33, "sqftPerBox": 32.72},
    {"name": "Tenacious Grey Ice", "sqftPerPiece": 2.33, "sqftPerBox": 51.39},
    {"name": "Terrain 12 Mil (nest)", "sqftPerPiece": 1.98, "sqftPerBox": 41.72},
    {"name": "Town and Country", "sqftPerPiece": 1.49, "sqftPerBox": 35.94},
    {"name": "VCT (Tarkett, Imperial Textures)", "sqftPerPiece": 1, "sqftPerBox": 45}
]

@app.route('/upload', methods=['POST'])
def upload():
    if 'pdf' not in request.files:
        return {'error': 'No file part'}, 400

    file = request.files['pdf']
    if file.filename == '':
        return {'error': 'No selected file'}, 400

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

    # Create a new PDF with the calculations
    pdf_output = create_pdf_with_calculations(calculations, pdf_reader)
    pdf_output.seek(0)
    
    return send_file(pdf_output, attachment_filename='calculated_output.pdf', as_attachment=True)

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

def create_pdf_with_calculations(calculations, original_pdf):
    output_stream = io.BytesIO()
    
    # Create a new PDF with the same content as the original PDF
    pdf_writer = PyPDF2.PdfFileWriter()
    for page_num in range(original_pdf.numPages):
        page = original_pdf.getPage(page_num)
        pdf_writer.addPage(page)
    pdf_writer.write(output_stream)
    
    # Create a new PDF with calculations using FPDF
    fpdf = FPDF()
    fpdf.add_page()
    fpdf.set_font("Arial", size=12)
    
    fpdf.cell(200, 10, txt="Calculation Results", ln=True, align='C')
    for item, calc in calculations.items():
        fpdf.cell(200, 10, txt=f"{item}: Boxes: {calc['boxes']}, Pieces: {calc['pieces']}, Actual SqFt: {calc['actualSqFt']}", ln=True, align='L')
    
    calc_output = io.BytesIO()
    fpdf.output(calc_output)
    calc_output.seek(0)
    
    # Combine both PDFs
    merged_pdf = PyPDF2.PdfFileMerger()
    merged_pdf.append(output_stream)
    merged_pdf.append(calc_output)
    final_output = io.BytesIO()
    merged_pdf.write(final_output)
    final_output.seek(0)
    
    return final_output

if __name__ == '__main__':
    app.run(debug=True)
