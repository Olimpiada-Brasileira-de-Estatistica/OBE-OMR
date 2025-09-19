import os

from pdf2image import convert_from_path

input_dir = "./ProvasPDF"
output_dir = "./Provas"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

for filename in os.listdir(input_dir):
    if filename.endswith(".pdf"):
        pdf_path = os.path.join(input_dir, filename)
        images = convert_from_path(pdf_path)
        for i, image in enumerate(images):
            image.save(
                os.path.join(output_dir, f"{filename[:-4]}_page_{i + 1}.png"), "PNG"
            )
