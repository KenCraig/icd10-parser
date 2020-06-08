#!/bin/bash
# Download and extract the two files needed for parsing
# Yes, it's ugly, but it only changes annually
#   and the paths may vary

mkdir tmp
pushd tmp

if [ $1 -eq 2017 ]; then
  CODEFILE="2017-ICD10-Code-Descriptions.zip"
  TABLEFILE="2017-ICD10-Code-Tables-Index.zip"
elif [ $1 -eq 2018 ]; then
  CODEFILE="2018-ICD-10-Code-Descriptions.zip"
  TABLEFILE="2018-ICD-10-Table-And-Index.zip"
elif [ $1 -eq 2019 ]; then
  CODEFILE="2019-ICD-10-CM-Code-Descriptions.zip"
  TABLEFILE="2019-ICD-10-CM-Tables-and-Index.zip"
elif [ $1 -eq 2020 ]; then
  CODEFILE="2020-ICD-10-CM-Codes.zip"
  TABLEFILE="2020-ICD-10-CM-Code-Tables.zip"
else
  print Usage: $0 [year]
fi

if [ ! -f $CODEFILE ]; then
  curl -O "https://www.cms.gov/Medicare/Coding/ICD10/Downloads/"${CODEFILE}
fi

if [ -f $CODEFILE ]; then
  unzip -oj ${CODEFILE} "*/icd10cm_order_????.txt" || unzip -oj ${CODEFILE} "icd10cm_order_????.txt"
fi

if [ ! -f $TABLEFILE ]; then
  curl -O "https://www.cms.gov/Medicare/Coding/ICD10/Downloads/"${TABLEFILE}
fi
if [ -f $TABLEFILE ]; then
  unzip -oj ${TABLEFILE} "*/icd10cm_tabular_????.xml" || unzip -oj ${TABLEFILE} "icd10cm_tabular_????.xml"
fi
popd
