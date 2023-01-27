import urllib.request
import os
import pandas as pd
import requests
import numpy as np
from crossref.restful import Works
works = Works()

## To facilitate the download of the articles and the text processing,
## please find here automatic PDF and XML request functions using the Crossref API
## in combination with an optional Elsevier license.

# Functions
def tryCrossRefDoi (doi):
    """Tries whether Crossref has a the metadata and link information on the article
       and fetches that information when available."""
    try:
        r = works.doi(str(doi))
    except urllib.error.HTTPError or TimeoutError:
        print("cannot find: " + str(doi ))
        r = 0
    else:
        pass
    return r

def retrieveOpenSourcePdf(CrossrefOutputArray):
    """Retrieve the pdf link from the CrossRef information
       and download the document"""
    pdfLink = [x for s in CrossrefOutputArray for x in s if ("http" in x and "pdf" in x)]
    for link in pdfLink:
        try:
            pdf = requests.get(link)
        except TimeoutError:
            print("Needs license")
        else:
            pass
            paper_file = (paper.replace("/", "_") + '.pdf')
            with open(os.path.join(docfolder, 'pdf/', paper_file), 'wb') as f:
                f.write(pdf.content)
            return print("retrieved", link)

def retrieveElsevierXMLPDF(CrossrefOutputArray):
    """Retrieve the XML link and download the document and save it in a text file.
       Elsevier offers fulltext XML with an authentication key, which can be requested.
       With the same link but a different url ending one can also fetch the pdfs."""
    xmlLink = [x for s in CrossrefOutputArray for x in s if ("http" in x and "xml" in x)][0]
    if "elsevier" in xmlLink:
        xmlLink = (xmlLink + "&apiKey="+ElsAPIkey+ "&insttoken="+ InstitutToken+ "6ec21df6f452c6f1e466640cd0b51bfd")
        pdfLink = xmlLink.replace("text/xml", "application/pdf")
        pdf = requests.get(pdfLink)
        paper_file = (paper.replace("/", "_") + '.pdf')
        with open(os.path.join(docfolder, 'pdf/', paper_file), 'wb') as f:
            f.write(pdf.content)
            print("retrieved", pdfLink)
    try:
        xmldoc = requests.get(xmlLink)
    except TimeoutError:
        print("Needs license")
    else:
        pass
        paper_file = (paper.replace("/", "_") + '.txt')
        with open(os.path.join(docfolder, 'xml/', paper_file), 'wb') as f:
            f.write(xmldoc.content)
    return print("retrieved", xmlLink)


## Execution

# Read the list of DOIs
os.chdir(r"D:\PhD EXPANSE\Literature\WOS_ModalChoice_Ref")
paper_DOIs = pd.read_csv("exampleDois.csv")
print(paper_DOIs.iloc[:,0])

# Set the folder where the documents should be safed
# Make sure to create a pdf and xml subfolder for the respective files
docfolder = "D:/PhD EXPANSE/Literature/WOS_ModalChoice_Ref/newCrossRef"

# Set Elsevier API and Institution keys
ElsAPIkey = ""
InstitutToken = ""

paperLinks = []
for paper in paper_DOIs.iloc[:,0]:
    r = tryCrossRefDoi(paper)
    if r and r != 0:
        if 'URL' in r:
            paperLinks.append(r['URL'])
        if 'link' in r:
            array = np.char.split(np.array(r['link'], dtype=str), sep="'").tolist()
            print(array)
            if any("text/xml" in s for s in array):
                print("has xml")
                retrieveElsevierXMLPDF(array)
            if any(x in s for s in array for x in ["application/pdf", "unspecified"]):
                print("has pdf")
                retrieveOpenSourcePdf(array)

csv = os.path.join(docfolder,"paperlinks.csv")
pd.DataFrame(paperLinks).to_csv(csv)

