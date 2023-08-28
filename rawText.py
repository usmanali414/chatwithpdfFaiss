import docx
from typing_extensions import Concatenate
from PyPDF2 import PdfReader
from striprtf.striprtf import rtf_to_text

def getDocxText(filename):
    doc = docx.Document(filename)
    fullText = []
    for para in doc.paragraphs:
        fullText.append(para.text)
    return '\n'.join(fullText)

def getPDFText(filename):
  pdfreader = PdfReader(filename)
  raw_text = ''
  for i, page in enumerate(pdfreader.pages):
      content = page.extract_text()
      if content:
          raw_text += content
  return raw_text

def getTxtText(filename):
  with open(filename) as f:
    contents = f.read()
  return contents

def getRtfText(filename):
  f = open(filename,'r')
  text = rtf_to_text(f.read())
  return text