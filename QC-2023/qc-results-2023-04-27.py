qc-results-2023-04-27.py 
"""

exec(open("/homes/3/sdp21/Desktop/alta1/users/QC.2023/qc-results-2023-04-27.py").read())

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

import glob
import json
import os

qcPath = "/autofs/space/alta_001/users/QC.2023"
oldSeriesPaths = [
    ["nii-2023-02-13-SynthSeg2", "selectedSeries.json"],
    ["nii-2023-02-27-SynthSeg2", "selectedSeries.json"],
]
seriesPaths = [
    ["nii-2023-03-30-SynthSeg2", "selectedSeries-Peter.json"],
    ["nii-2023-03-30-SynthSeg2", "selectedSeries-Randy.json"],
    ["nii-2023-04-26-SynthSeg2", "selectedSeries-Randy+Peter.json"],
]



niiDirs = ["/space/alta/1/users/QC.2023/nii-2023-02-13", "/space/alta/1/users/QC.2023/nii-2023-02-27"]
resultPath = "/space/alta/1/users/QC.2023/vol+qc-2023-04-27.csv"

volCount = 101
qcCount = 8

headers = ""

mrnByAccession = {}
db = slicer.dicomDatabase
for patient in db.patients():
    for study in db.studiesForPatient(patient):
        accessionNumber = db.fieldForStudy("AccessionNumber", study)
        mrn = db.fieldForPatient("PatientID", patient)
        if accessionNumber in mrnByAccession.keys():
            raise f"study already found for {accessionNumber}"
        mrnByAccession[accessionNumber] = mrn

resultFP = open(resultPath, "w")

for seriesPath,jsonName in seriesPaths:
    ssDir = f"{qcPath}/{seriesPath}"
    selectedSeriesPath = f"{ssDir}/{jsonName}"
    selectedSeries = json.loads(open(selectedSeriesPath).read())
    for selectionKey in selectedSeries.keys():
        if selectionKey.find(",") != -1:
            continue
        selection = selectedSeries[selectionKey]
        if selection in [None, "Reject"]:
            continue
        volContents = open(f"{ssDir}/vol-{selection}.nii.gz.csv").read().split("\n")
        qcContents = open(f"{ssDir}/qc-{selection}.nii.gz.csv").read().split("\n")
        if headers == "":
            headers = "MRN,Accession,SeriesTag,"
            vols = volContents[0].split(",")[-volCount:]
            vols = ["vol-"+e for e in vols]
            headers += ",".join(vols)
            headers += ","
            qcs = qcContents[0].split(",")[-qcCount:]
            qcs = ["qc-"+e for e in qcs]
            headers += ",".join(qcs)
            resultFP.write(headers+"\n")
        accession = selection.split("_")[0] 
        seriesTag = selection[selection.find("_")+1:]
        row = f'{mrnByAccession[accession]},{accession},"{seriesTag}",'
        row += ",".join(volContents[1].split(",")[-volCount:])
        row += ","
        row += ",".join(qcContents[1].split(",")[-qcCount:])
        resultFP.write(row+"\n")
resultFP.close()

print("done")
