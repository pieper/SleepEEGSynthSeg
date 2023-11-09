3$ cat qc-review-2023-04-26.py 
"""

/usr/pubsw/packages/slicer/Slicer-5.2.2-linux-amd64/slicer522

exec(open("/space/alta/1/users/QC.2023/qc-review-2023-04-26.py").read())

"""

reviewer = "Randy+Peter"

try:
    print(f"Reviewer is {reviewer}")
except NameError:
    reviewer = None


reviewers = ["Randy", "Peter", "Randy+Peter"]

if reviewer not in reviewers:
    slicer.util.errorDisplay(f"Set the variable 'reviewer' to one of {reviewers}")

import functools
import glob
import json
import os

niiDir = "/space/alta/1/users/QC.2023/nii-2023-04-26"
ssDir = f"{niiDir}-SynthSeg2"

#selectedSeriesBackupPath = f"{niiDir}-SynthSeg2/selectedSeriesBackup.json"
#selectedSeriesPath = f"{niiDir}-SynthSeg2/selectedSeries.json"
selectedSeriesBackupPath = f"{niiDir}-SynthSeg2/selectedSeriesBackup-{reviewer}.json"
selectedSeriesPath = f"{niiDir}-SynthSeg2/selectedSeries-{reviewer}.json"

todoNextIndex = 0

seriesIDs = []
ssByAccesssion = {}
for ssPath in glob.glob(f"{ssDir}/*.nii.gz"):
    seriesID = os.path.basename(ssPath).replace("seg-", "").replace(".nii.gz", "")
    seriesIDs.append(seriesID)
    accession = seriesID.split("_")[0]
    if accession not in ssByAccesssion.keys():
        ssByAccesssion[accession] = []
    ssByAccesssion[accession].append(ssPath)
ssByAccesssion

keys = list(ssByAccesssion.keys())
splitIndex = int(len(keys) / 2) # in case len is odd

if reviewer == "Randy+Peter":
    reviewKeys = keys
else:
    if reviewer == reviewers[0]:
        reviewKeys = keys[:splitIndex]
    elif reviewer == reviewers[1]:
        reviewKeys = keys[splitIndex:]

ssByAccesssion = {key: ssByAccesssion[key] for key in reviewKeys}


studiesByAccession = {}
db = slicer.dicomDatabase
for patient in db.patients():
    for study in db.studiesForPatient(patient):
        accessionNumber = db.fieldForStudy("AccessionNumber", study)
        if accessionNumber in studiesByAccession.keys():
            raise f"study already found for {accessionNumber}"
        studiesByAccession[accessionNumber] = study

def loadSeries(seriesID):
    slicer.mrmlScene.Clear()
    slicer.util.loadVolume(f"{niiDir}/{seriesID}.nii.gz")
    segmentation = slicer.util.loadSegmentation(f"{ssDir}/seg-{seriesID}.nii.gz")
    segmentation.GetDisplayNode().SetVisibility2DFill(False)

def saveSelectedSeries():
    open(selectedSeriesPath,"w").write(json.dumps(selectedSeries))

def selectSeries(accessionIndex, seriesID):
    selectedSeries[str(accessionIndex)] = seriesID
    selectedSeries[str(accessionIndex)+",Reviewer"] = reviewer
    saveSelectedSeries()
    qt.QTimer.singleShot(0, lambda accessionIndex=accessionIndex: showAccession(accessionIndex))

def updateTODO():
    global todoNextIndex
    todoNextIndex = None
    todoCount = 0
    for accessionIndex in range(accessionCount):
        if selectedSeries[str(accessionIndex)] == None:
            todoCount += 1
            if todoNextIndex is None:
                todoNextIndex = accessionIndex
    todoLabel.text = f"{todoCount} to do of {accessionCount}"
    todoNextButton.enabled = todoNextIndex is not None
    if todoNextIndex is None:
        todoNextIndex = 0

def showNext():
    showAccession(todoNextIndex)

def setStudyComments(accessionIndex, text):
    commentsKey = str(accessionIndex)+",Comments"
    selectedSeries[commentsKey] = text

def showAccession(accessionIndex):
    saveSelectedSeries()
    updateTODO()
    accessionIndex = int(accessionIndex)
    accessionSlider.value = accessionIndex
    for rowIndex in range(seriesLayout.rowCount()):
        seriesLayout.removeRow(0)
    accession = list(ssByAccesssion.keys())[accessionIndex] 
    seriesRecords = []
    for ssPath in ssByAccesssion[accession]:
        seriesID = os.path.basename(ssPath).replace("seg-", "").replace(".nii.gz", "")
        qcPath = f"{ssDir}/qc-{seriesID}.nii.gz.csv"
        qcs = open(qcPath).read().split("\n")[1].split(",")[-8:]
        meanQC = functools.reduce(lambda a,b: float(a)+float(b), qcs) / len(qcs)
        volPath = f"{ssDir}/vol-{seriesID}.nii.gz.csv"
        totalVol = open(volPath).read().split("\n")[1].split(",")[1]
        seriesRecords.append({'seriesID':seriesID, 'meanQC':meanQC, 'totalVol':totalVol})
    studyUID = studiesByAccession[accession]
    patientsUID = slicer.dicomDatabase.fieldForStudy("PatientsUID", studyUID)
    patientID = slicer.dicomDatabase.fieldForPatient("PatientID", patientsUID)
    patientIDLabel = qt.QLabel(f"Patient ID {patientID}")
    seriesLayout.addRow(patientIDLabel)
    studyComments = qt.QLineEdit()
    commentsKey = str(accessionIndex)+",Comments"
    if commentsKey in selectedSeries:
        studyComments.text = selectedSeries[commentsKey]
    seriesLayout.addRow("Comments", studyComments)
    studyComments.connect("textChanged(QString)", lambda text, accessionIndex=accessionIndex: setStudyComments(accessionIndex, text))
    clearButton = qt.QPushButton("Clear selection")
    clearButton.connect("clicked()", lambda accessionIndex=accessionIndex: selectSeries(accessionIndex, None))
    seriesLayout.addRow(clearButton)
    rejectButton = qt.QPushButton("Reject study")
    rejectButton.connect("clicked()", lambda accessionIndex=accessionIndex: selectSeries(accessionIndex, "Reject"))
    seriesLayout.addRow(rejectButton)
    if selectedSeries[str(accessionIndex)] == "Reject":
        rejectLabel = qt.QLabel("Study Rejected")
        rejectLabel.setStyleSheet("color: red; border:3px solid red")
        seriesLayout.addRow(rejectLabel)
    for seriesRecord in sorted(seriesRecords, key=lambda record: record['meanQC'], reverse=True):
        seriesID = seriesRecord['seriesID']
        meanQC = seriesRecord['meanQC']
        totalVol = seriesRecord['totalVol']
        selectButton = qt.QPushButton(f"{seriesID}\nQC: {round(meanQC,3)}\nVol: {round(float(totalVol)/10/10/10/1000,2)} liters")
        pngPath = f"{niiDir}/{seriesID}.png"
        selectButton.setIcon(qt.QIcon(pngPath))
        iconSize = qt.QSize(150,150) if selectedSeries[str(accessionIndex)] == seriesID else qt.QSize(100,100)
        selectButton.setIconSize(iconSize)
        buttonStyle = "text-align:left;"
        buttonStyle += "border:3px solid navy;" if selectedSeries[str(accessionIndex)] == seriesID else ""
        selectButton.setStyleSheet(buttonStyle)
        sizePolicy = qt.QSizePolicy()
        sizePolicy.setHorizontalPolicy(qt.QSizePolicy.Expanding)
        selectButton.setSizePolicy(sizePolicy)
        selectButton.connect("clicked()", lambda accessionIndex=accessionIndex,seriesID=seriesID: selectSeries(accessionIndex,seriesID))
        loadButton = qt.QPushButton("Load")
        loadButton.connect("clicked()", lambda seriesID=seriesID: loadSeries(seriesID))
        seriesLayout.addRow(loadButton, selectButton)

accessionCount = len(ssByAccesssion.keys())
selectedSeries = {}
for accessionIndex in range(accessionCount):
    selectedSeries[str(accessionIndex)] = None
if os.path.exists(selectedSeriesPath):
    selectedSeries = json.loads(open(selectedSeriesPath).read())
open(selectedSeriesBackupPath,"w").write(json.dumps(selectedSeries))

try:
    del(reviewWidget)
except NameError:
    pass
reviewWidget = qt.QWidget()
reviewWidget.size = qt.QSize(500,1000)
reviewLayout = qt.QFormLayout()
reviewWidget.setLayout(reviewLayout)
accessionSlider = ctk.ctkSliderWidget()
accessionSlider.maximum = accessionCount-1
accessionSlider.pageStep = 1
accessionSlider.decimals = 0
if not accessionSlider.connect("valueChanged(double)", showAccession):
    print("connection failed")
reviewLayout.addRow("Study", accessionSlider)
todoLabel = qt.QLabel()
todoNextButton = qt.QPushButton("Next")
reviewLayout.addRow(todoLabel, todoNextButton)
todoNextButton.connect("clicked()", lambda : showAccession(todoNextIndex))
seriesWidget = qt.QWidget()
seriesLayout = qt.QFormLayout()
seriesWidget.setLayout(seriesLayout)
updateTODO()
showAccession(todoNextIndex)
seriesWidget.show()
seriesArea = qt.QScrollArea(reviewWidget)
seriesArea.setWidget(seriesWidget)
seriesArea.widgetResizable = True
reviewLayout.addRow(seriesArea)
if reviewer is not None:
    reviewWidget.show()

""" # load missing studies by accession number:

for accession in missingDBAccessions:
    os.system(f"grep {accession} /space/alta/1/users/QC.2023/studyPaths.txt >> /tmp/paths")

paths = open("/tmp/paths").read().strip().split('\n')
dicomBrowser = slicer.modules.DICOMWidget.browserWidget.dicomBrowser
for path in paths:
    print(path)
    dicomBrowser.importDirectory(path, dicomBrowser.ImportDirectoryAddLink)
    dicomBrowser.waitForImportFinished()
"""


""" # convert each series in accessions to nii with screenshot
db = slicer.dicomDatabase
patientCount = 0
for patient in db.patients():
    patientCount += 1
    print(f"\n\n{patientCount} of {len(db.patients())}")
    for study in db.studiesForPatient(patient):
        accessionNumber = db.fieldForStudy("AccessionNumber", study)
        if accessionNumber not in accessions:
            print(f"skipping {accessionNumber}")
            continue
        for series in db.seriesForStudy(study):
            slicer.mrmlScene.Clear()
            loadedNodeIDs = DICOMUtils.loadSeriesByUID([series])
            if len(loadedNodeIDs) != 1:
                print(f"Skipping {series} because it generated {len(loadedNodeIDs)} nodes")
                continue
            seriesDescription = db.fieldForSeries("SeriesDescription", series)
            seriesDescription = seriesDescription.replace(" ", "_").replace("/","-")
            seriesNumber = int(db.fieldForSeries("SeriesNumber", series))
            niiPath = f"{niiDir}/{accessionNumber}_{seriesNumber}_{seriesDescription}.nii.gz"
            pngPath = f"{niiDir}/{accessionNumber}_{seriesNumber}_{seriesDescription}.png"
            slicer.util.delayDisplay(niiPath, 100)
            print(niiPath)
            slicer.util.saveNode(slicer.util.getNode(loadedNodeIDs[0]), niiPath)
            slicer.util.mainWindow().centralWidget().grab().toImage().save(pngPath)
"""

""" # From series replacement process based on Randy's review

col0 = dataset.columns[0]
col1 = dataset.columns[1]
replaceCount = 0
for niiName,replacement in zip(dataset[col0],dataset[col1]):
    if niiName.__class__() == '' and replacement.__class__() == '' and replacement.startswith("replace"):
        eriesIndex = replacement.find('eries')
        if eriesIndex != -1:
            numberString = replacement[eriesIndex:].split()[1]
            while not numberString[-1].isdigit():
                numberString = numberString[:-1]
            seriesNumber = int(numberString)
            if seriesNumber != '':
                accession = niiName.split("_")[0]
                print(f"process study {studiesByAccession[accession]}, series {seriesNumber}")
                for series in db.seriesForStudy(studiesByAccession[accession]):
                    if seriesNumber == int(db.fieldForSeries("SeriesNumber", series)):
                        slicer.mrmlScene.Clear()
                        loadedNodeIDs = DICOMUtils.loadSeriesByUID([series])
                        volumeID = None
                        for nodeID in loadedNodeIDs:
                            if nodeID.startswith("vtkMRMLScalarVolumeNode"):
                                volumeID = nodeID
                                break
                        if volumeID is None:
                            raise("Error finding volume!")
                        seriesDescription = db.fieldForSeries("SeriesDescription", series)
                        seriesDescription = seriesDescription.replace(" ", "_").replace("/","-")
                        replacementPath = f"{replacementDir}/{accession}_{seriesNumber}_{seriesDescription}.nii.gz"
                        slicer.util.delayDisplay(replacementPath)
                        slicer.util.saveNode(slicer.util.getNode(volumeID), replacementPath)
                    replaceCount += 1
print(f"{replaceCount} replacements")
"""
