"""

exec(open("/homes/3/sdp21/Desktop/alta1/users/QC.2023/qc-prep-2023-04-26.py").read())

/autofs/cluster/pubsw/arch/CentOS8-x86_64/packages/slicer/Slicer-5.2.2-linux-amd64/slicer522 

Slicer with customizecd loader:

export LD_LIBRARY_PATH=/space/alta/1/users/pieper/slicer/openssl:/space/alta/1/users/pieper/slicer/krb5/src/lib
/space/alta/1/users/pieper/download/Slicer-5.2.1-linux-amd64/Slicer --python-script /homes/3/sdp21/Desktop/alta1/users/QC.2023/qc-prep-2023-04-26.py |& tee qc-prep-2023-04-26.log

"""

try:
    import pandas
except ModuleNotFoundError:
    pip_install("pandas")
    import pandas

from DICOMLib import DICOMUtils


studyCSV = "/space/alta/1/users/QC.2023/ToSteve-2023.04.25.csv"
niiDir = "/space/alta/1/users/QC.2023/nii-2023-04-26"

accessions = []

studyData = pandas.read_csv(studyCSV)
for row in studyData['Accession']:
    accessions.append(row)

db = slicer.dicomDatabase
patientCount = 0
studiesForPatient = {}
accessionStudies = []
for patient in db.patients():
    patientCount += 1
    # print(f"\n\n{patientCount} of {len(db.patients())}")
    for study in db.studiesForPatient(patient):
        accessionNumber = db.fieldForStudy("AccessionNumber", study)
        if accessionNumber not in accessions:
            #print(f"skipping {accessionNumber}")
            continue
        if patient not in studiesForPatient:
            studiesForPatient[patient] = []
        studiesForPatient[patient].append(study)
        print(f"Found study for accession {accessionNumber}")
        accessionStudies.append(accessionNumber)
        for series in db.seriesForStudy(study):
            slicer.mrmlScene.Clear()
            loadedNodeIDs = DICOMUtils.loadSeriesByUID([series], pluginClassNames=['DICOMScalarVolumePlugin'])
            print(loadedNodeIDs)
            slicer.util.delayDisplay(loadedNodeIDs)
            if len(loadedNodeIDs) == 0:
                print(f"Skipping {series} because it generated {len(loadedNodeIDs)} nodes")
                continue
            volumeNode = slicer.util.getNode(loadedNodeIDs[0])
            if len(loadedNodeIDs) == 2 and loadedNodeIDs[1].find("GridTransform") != -1:
                volumeNode.HardenTransform()
            elif len(loadedNodeIDs) != 1:
                print(f"Skipping {series} because it generated {len(loadedNodeIDs)} nodes")
                continue
            seriesDescription = db.fieldForSeries("SeriesDescription", series)
            seriesDescription = seriesDescription.replace(" ", "_").replace("/","-")
            seriesNumber = int(db.fieldForSeries("SeriesNumber", series))
            niiPath = f"{niiDir}/{accessionNumber}_{seriesNumber}_{seriesDescription}.nii.gz"
            pngPath = f"{niiDir}/{accessionNumber}_{seriesNumber}_{seriesDescription}.png"
            slicer.util.delayDisplay(niiPath, 100)
            print(niiPath)
            slicer.util.saveNode(volumeNode, niiPath)
            slicer.util.mainWindow().centralWidget().grab().toImage().save(pngPath)

"""
ssDirs = ["/homes/3/sdp21/Desktop/alta1/users/QC.2023/nii-2023-02-08-SynthSeg2", "/homes/3/sdp21/Desktop/alta1/users/QC.2023/nii-2023-02-09-SynthSeg2"]

ssByAccesssion = {}
for ssDir in ssDirs:
    for ssPath in glob.glob(f"{ssDir}/*.nii.gz"):
        accession = os.path.basename(ssPath).split("_")[0].replace("seg-", "")
        if accession not in ssByAccesssion.keys():
            ssByAccesssion[accession] = []
        ssByAccesssion[accession].append(ssPath)
ssByAccesssion

missingAccessions = []
for accession in accessions:
    if accession not in ssByAccesssion.keys():
        missingAccessions.append(accession)


studiesByAccession = {}
db = slicer.dicomDatabase
for patient in db.patients():
    for study in db.studiesForPatient(patient):
        accessionNumber = db.fieldForStudy("AccessionNumber", study)
        if accessionNumber in studiesByAccession.keys():
            raise f"study already found for {accessionNumber}"
        studiesByAccession[accessionNumber] = study

missingDBAccessions = []
for accession in accessions:
    if accession not in studiesByAccession.keys():
        missingDBAccessions.append(accession)
"""

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

"""
niiDir = "/homes/3/sdp21/Desktop/alta1/users/QC.2023/nii-2023-02-13"

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

"""

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
