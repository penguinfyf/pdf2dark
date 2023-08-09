import json
import os

import fitz
import numpy as np
import PIL.ImageOps
from PIL import Image
from tqdm import tqdm


def dark(pdfPath, OutPath):
    """Convert pdf to dark mode page by page

    Args:
        pdfPath (str): path of input pdf 
        outPath (str): path of output pdf 
    """
    #   Convert pdf to dark mode page by page
    pdfDoc = fitz.open(pdfPath)
    OutDoc = fitz.open()
    #   RGB value for text and background
    TextColor = np.array([204, 204, 184])
    BackgroundColor = np.array([32, 31, 30])
    rgb2dark = (
        (TextColor[0]-BackgroundColor[0])/255, 0, 0, BackgroundColor[0],
        0, (TextColor[1]-BackgroundColor[1])/255, 0, BackgroundColor[1],
        0, 0, (TextColor[2]-BackgroundColor[2])/255, BackgroundColor[2])

    for Page in tqdm(pdfDoc, desc="Progress"):
        pix = Page.get_pixmap(dpi=300)
        #   Use pillow to get desired colored Image
        Img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        Img = PIL.ImageOps.invert(Img)
        Img = Img.convert("RGB", rgb2dark)
        Img = Img.convert("L")
        Img.save('temp.jpg', optimize=True)  # Save as jpeg to reduce file size
        OutDoc.new_page(pno=-1, width=Page.rect.x1, height=Page.rect.y1)
        OutPage = OutDoc[-1]
        OutPage.insert_image(OutPage.rect, filename='temp.jpg')
        os.remove('temp.jpg')

    if os.path.exists(OutPath):
        os.remove(OutPath)

    pdfDoc.close()
    OutDoc.save(OutPath)
    OutDoc.close()


if __name__ == "__main__":

    with open("./config.json", "r") as j:
        config = json.load(j)
    #   Convert every pdf in InputDir
    #   Save them in OutputDir
    InputDir = config["InputDir"]
    OutputDir = config["OutputDir"]

    if not os.path.exists(OutputDir):
        os.makedirs(OutputDir)

    for (Path, Dir, Files) in os.walk(InputDir):
        for File in Files:
            FileList = File.split(".")
            if len(FileList) != 2:
                continue
            FileName, ext = FileList
            if ext != "pdf":
                continue
            print("Converting", FileName)
            InputPath = os.path.join(Path, File)
            OutputPath = os.path.join(OutputDir, f"{FileName}.pdf")
            dark(InputPath, OutputPath)
