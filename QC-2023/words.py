words.py 
import os
import pydicom

from os import path
from wordcloud import WordCloud

# get data directory (using getcwd() is needed to support running example in generated IPython notebook)
d = path.dirname(__file__) if "__file__" in locals() else os.getcwd()

# Read the whole text.
text = open(path.join(d, 'reasons.txt')).read()
text = open(path.join(d, 'studyDescriptions.txt')).read()

"""
text = ""
studyDescriptions = ""
db = slicer.dicomDatabase
for patient in db.patients():
    for study in db.studiesForPatient(patient):
        series = db.seriesForStudy(study)[0]
        instance = db.instancesForSeries(series)[0]
        dataset = pydicom.read_file(db.fileForInstance(instance))
        try:
            text += dataset.ReasonForStudy
            studyDescriptions += dataset.StudyDescription
        except AttributeError:
            continue
        except TypeError:
            continue
"""


# Generate a word cloud image
wordcloud = WordCloud().generate(text)

# Display the generated image:
# the matplotlib way:
import matplotlib.pyplot as plt
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")

# lower max_font_size
wordcloud = WordCloud(width=1024, height=768, max_words=1000, max_font_size=60).generate(text)
plt.figure()
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.show()

# The pil way (if you don't have matplotlib)
# image = wordcloud.to_image()
# image.show()
