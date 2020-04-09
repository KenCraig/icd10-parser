# icd10merge2csv.py

Download CMS ICD10 files from https://www.cms.gov/Medicare/Coding/ICD10/

The 2020 files are at https://www.cms.gov/Medicare/Coding/ICD10/2020-ICD-10-CM

* short/long descriptions https://www.cms.gov/Medicare/Coding/ICD10/Downloads/2020-ICD-10-CM-Codes.zip
    * unzip this into a directory named txt
* xml code tables https://www.cms.gov/Medicare/Coding/ICD10/Downloads/2020-ICD-10-CM-Code-Tables.zip
    * unzip into a directory named xml

then run the script with
```shell script
python icd10parse.py xml/icd10cm_tabular_2020.xml txt/icd10cm_order_2020.txt
```

you'll end up with two databases right now (migrating to peewee and doing smarter python things), but only one will have the data

## Exporting excel files with all the codes
This was written because there was a need to assign morbidity and severity to all codes, and the easiest way to do it was just distribute excel files to parse later.  Rather than make one huge file, I break up the codes by their main category, then split out individual worksheets by subcategory.
 
```shell script
mkdir codes-xlsx
python morbidity-list.py
```
