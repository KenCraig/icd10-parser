#!/bin/bash
# Download and extract the two files needed for parsing
# Yes, it's ugly, but it only changes annually
#   and the paths may vary

mkdir tmp
pushd tmp

if [ $1 -lt 2021 ]; then
  CODEROOT="https://www.cms.gov/Medicare/Coding/ICD10/Downloads/"
  TABLEROOT="https://www.cms.gov/Medicare/Coding/ICD10/Downloads/"
else
    # they changed the root location for the files - grrr
  CODEROOT="https://www.cms.gov/files/zip/"
  TABLEROOT="https://www.cms.gov/files/zip/"
fi

if [ $1 -eq 2014 ]; then
  CODEFILE="2014-ICD10-Code-Descriptions.zip"
  TABLEFILE="2014-ICD10-Code-Tables-and-Index.zip"
elif [ $1 -eq 2015 ]; then
  CODEFILE="2015-code-descriptions.zip"
  TABLEFILE="2015-tables-index.zip"
elif [ $1 -eq 2016 ]; then
  CODEFILE="2016-Code-Descriptions-in-Tabular-Order.zip"
  TABLEFILE="2016-CM-Code-Tables-and-Index.zip"
elif [ $1 -eq 2017 ]; then
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
elif [ $1 -eq 2021 ]; then
  CODEFILE="2021-code-descriptions-tabular-order.zip"
  TABLEFILE="2021-code-tables-and-index.zip"
else
  echo Usage: $0 [year]
  exit
fi

if [ ! -f $CODEFILE ]; then
  curl -O ${CODEROOT}${CODEFILE}
fi

if [ -f $CODEFILE ]; then
  unzip -oj ${CODEFILE} "*/icd10cm_order_????.txt" || unzip -oj ${CODEFILE} "icd10cm_order_????.txt"
fi

if [ ! -f $TABLEFILE ]; then
  curl -O ${TABLEROOT}${TABLEFILE}
fi

if [ -f $TABLEFILE ]; then
  if [ $1 -lt 2017 ]; then
    echo 'Old naming convention, forcing to new style'
    unzip -ojp ${TABLEFILE} "Tabular.xml" > icd10cm_tabular_${1}.xml
  else
    unzip -oj ${TABLEFILE} "*/icd10cm_tabular_????.xml" || unzip -oj ${TABLEFILE} "icd10cm_tabular_????.xml"
  fi
fi
popd
exit


