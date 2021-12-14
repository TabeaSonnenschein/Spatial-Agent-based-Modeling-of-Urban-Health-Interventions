import urllib.request
import os
import pandas as pd
import requests
import numpy as np
import itertools
import elsapy

os.chdir(r"C:\Users\Tabea\Documents\PhD EXPANSE\Literature\WOS_ModalChoice_Ref")
paper_DOIs = pd.read_csv("WOS_references_search3_reviews_DOIs.csv")
print(paper_DOIs.iloc[:,0])


# ## Load configuration
# con_file = open("config.json")
# config = json.load(con_file)
# con_file.close()
#
# ## Initialize client
# client = ElsClient(config['b4392aff9fe5150839817eb72bc2b70b'])
# client.inst_token = config['insttoken']
#
# ## ScienceDirect (full-text) document example using DOI
# doi_doc = FullDoc(doi = '10.1016/S1525-1578(10)60571-5')
# if doi_doc.read(client):
#     print ("doi_doc.title: ", doi_doc.title)
#     doi_doc.write()
# else:
#     print ("Read document failed.")
#
# doi=10.1016/S0014-5793(01)03313-0&httpAccept=text/html&apiKey=b4392aff9fe5150839817eb72bc2b70b
# token=760D92F8EE4F3B8D114DC8BF760C9EC781A25C0739D519AE653F97CE8BED11B9C65401E6212228C7E0C62989491C07CE

paperLinks = []
requiredlicenses = []
for paper in paper_DOIs.iloc[:,0]:
    opener = urllib.request.build_opener()
    opener.addheaders = [('Accept', 'application/vnd.crossref.unixsd+xml')]
    try:
        r = opener.open('http://dx.doi.org/' + str(paper))
    except urllib.error.HTTPError or TimeoutError:
        print("cannot find: " + str(paper ))
    else:
        pass
        paperLinks.append(r.info()['Link'])
        array = np.char.split(np.array(r.info()['Link'], dtype=str), sep = ";").tolist()
        print(array)
        if any("xml" in s for s in array):
            print("has xml")
            xmlLink = np.char.split(np.array([s for s in array if "xml" in s][0]), sep = ",").tolist()[1]
            xmlLink = xmlLink.replace("<", "").replace(">", "")
            if any("elsevier" in s for s in array):
                xmlLink= (xmlLink+"&apiKey=b4392aff9fe5150839817eb72bc2b70b")
            print(xmlLink)
            xmldoc = requests.get(xmlLink)
            paper_file = (paper.replace("/", "_") + '.txt')
            with open(os.path.join(os.getcwd(),'CrossrefResults/xml/', paper_file), 'wb') as f:
                f.write(xmldoc.content)
        if any("pdf" in s for s in array):
            print("has pdf")
            if any("creativecommons" in s for s in array):
                pdfLink = np.char.split(np.array([s for s in [s for s in array if "pdf" in s] if "http" in s]), sep=",").tolist()[0][1]
                pdfLink = pdfLink.replace("<", "").replace(">", "")
                print(pdfLink)
                pdf = requests.get(pdfLink)
                paper_file = (paper.replace("/", "_") + '.pdf')
                with open(os.path.join(os.getcwd(),'CrossrefResults/pdf/', paper_file), 'wb') as f:
                    f.write(pdf.content)
            else:
                license = np.array([s for s in np.array([s for s in array if "license" in s]) if "http" in s])
                requiredlicenses.append(license)
                print("required lincese: " + str(license))
        if any("elsevier" in s for s in array):
            pdfLink= xmlLink.replace("text/xml", "application/pdf")
            pdf = requests.get(pdfLink)
            paper_file = (paper.replace("/", "_") + '.pdf')
            with open(os.path.join(os.getcwd(), 'CrossrefResults/pdf/', paper_file), 'wb') as f:
                f.write(pdf.content)

# csv = os.path.join(os.getcwd(),"paperlinks.csv")
# pd.DataFrame(paperLinks).to_csv(csv)

