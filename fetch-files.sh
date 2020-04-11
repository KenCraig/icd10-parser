#!/bin/bash
# Download and extract the two files needed for parsing
# Yes, it's ugly, but it only changes annually
#   and the paths may vary

mkdir tmp
pushd tmp

CODEFILE="2020-ICD-10-CM-Codes.zip"
if [ ! -f $CODEFILE ]; then
  curl -O "https://www.cms.gov/Medicare/Coding/ICD10/Downloads/"${CODEFILE}
fi

if [ -f $CODEFILE ]; then
  unzip -oj ${CODEFILE} "*/icd10cm_order_????.txt"
fi

TABLEFILE="2020-ICD-10-CM-Code-Tables.zip"
if [ ! -f $TABLEFILE ]; then
  curl -O "https://www.cms.gov/Medicare/Coding/ICD10/Downloads/"${TABLEFILE}
fi
if [ -f $TABLEFILE ]; then
  unzip -oj ${TABLEFILE} "*/icd10cm_tabular_????.xml"
fi
popd
