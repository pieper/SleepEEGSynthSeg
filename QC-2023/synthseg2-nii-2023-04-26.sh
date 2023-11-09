synthseg2-nii-2023-04-26.sh 
#!/bin/bash

source /usr/local/freesurfer/fs-dev-env-autoselect

NII_DIR=/homes/3/sdp21/Desktop/alta1/users/QC.2023/nii-2023-04-26
SYNTHSEG_DIR=/homes/3/sdp21/Desktop/alta1/users/QC.2023/nii-2023-04-26-SynthSeg2

mkdir ${SYNTHSEG_DIR}

cat << EOF > ${SYNTHSEG_DIR}/synthseg_cmd.sh

echo processing \$1

TARGET=${SYNTHSEG_DIR}/seg-\$1

if test -f \${TARGET}; then
  echo skipping \${TARGET}
else
  echo segmenting \${TARGET}
  mri_synthseg --i ${NII_DIR}/\$1 --o \${TARGET} --vol ${SYNTHSEG_DIR}/vol-\$1 --parc --robust --qc ${SYNTHSEG_DIR}/qc-\$1 2>&1 | tee ${SYNTHSEG_DIR}/\$1-log.txt
fi

EOF


time find ${NII_DIR}/ -iname \*.nii.gz  -printf "%f\n" | xargs -n 1 -P 15 -I % /bin/bash ${SYNTHSEG_DIR}/synthseg_cmd.sh % 
