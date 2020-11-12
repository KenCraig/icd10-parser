# icd10parse.py


Download CMS ICD10 files from https://www.cms.gov/Medicare/Coding/ICD10/

The 20201 files are at https://www.cms.gov/Medicare/Coding/ICD10/2021-ICD-10-CM

There's a shell script to download and unzip the files for 2017 through 2021
```shell script
./fetch-files.sh YYYY
```

* short/long descriptions https://www.cms.gov/Medicare/Coding/ICD10/Downloads/2020-ICD-10-CM-Codes.zip
    * only icd10cm_order_2020.txt is required
    * unzip this into ./tmp directory
* xml code tables https://www.cms.gov/Medicare/Coding/ICD10/Downloads/2020-ICD-10-CM-Code-Tables.zip
    * only icd10cm_tabular_2020.xml is required
    * unzip this into ./tmp directory

Now set up your python virtual environment and install requirements
```shell script
# Set up python virtualenv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

then run the script with
```shell script
python icd10parse.py tmp/icd10cm_tabular_2020.xml tmp/icd10cm_order_2020.txt
```

you'll end up with a sqlite3 database icd10codes.db

## Docker
If for some reason you don't want to run with your local python, you can run this in a docker container.  Note that it will be slower because it's writing to a locally  mounted directory for the database.

First build the image
```
docker build -t icdparse .
```

Then run the parser inside the docker container.  Yeah, it's a little messy, but it basically works
```shell script
# Fetch the files if you haven't done so already
./fetch-files.sh 2020

# parse the files and create icd10codes.db
docker run -it --rm --name icd10parse -v ${PWD}/tmp:/app/tmp ${PWD}/icd10codes.db:/app/icd10codes.db icdparse python icd10parse.py tmp/icd10cm_tabular_2020.xml tmp/icd10cm_order_2020.txt

```

Or, better yet, loop through all the years you want to do - it's not fast, but it will create a separate sqlite database for each year
```shell script
for x in 2016 2017 2018 2019 2020 2021; do
  ./fetch-files.sh ${x}
  touch ${PWD}/${x}_icd10codes.db  #don't think this is necessary, but just in case
  docker run -it --rm --name icd10parse -v ${PWD}/tmp:/app/tmp -v ${PWD}/${x}_icd10codes.db:/app/icd10codes.db icdparse python icd10parse.py tmp/icd10cm_tabular_${x}.xml tmp/icd10cm_order_${x}.txt
done

```

All of the above is kind of messy, but it's really only necessary to do once a year, so it's tolerable at this point.

## Exporting excel files with all the codes
This was written because there was a need to assign morbidity and severity to all codes, and the easiest way to do it was just distribute excel files to parse later.  Rather than make one huge file, I break up the codes by their main category, then split out individual worksheets by subcategory.
 
```shell script
# these can be run inside the docker container as well
mkdir codes-xlsx
python make-icd10-excel.py
```

## exportICD.sh
I want to import these into a database from csv files, with a flatter structure.  The easiest way to do so is to just run the query using sqlite3 utility and export as csv.  See exportICD.sh as the example

NOTE: if you want to run this within the docker container, you'll need to install sqlite3.  Inside the docker container run
```shell script
apt update
apt install -y sqlite3
```

Now you can export like this
```shell script
sqlite3 -header -csv icd10codes.db "select category_id, category_name from icd10category;" > final_icd10category.csv
```

```shell script
sqlite3 -header -csv icd10codes.db "select diag_code, long_desc, short_desc, subcat, category_name from icd10code left join icd10subcategory i10s on icd10code.subcat_id = i10s.subcat_id left join icd10category i10c on i10s.category_id = i10c.category_id;" > final_icd10category.csv

```

# Running multiple years
```
for x in 2017 2018 2019 2020 2021; do python icd10parse.py tmp/icd10cm_tabular_${x}.xml tmp/icd10cm_order_${x}.txt; mv icd10codes.db ${x}icd10codes.db; done
```
         
# Acknowledgements
I'm new to python and long out of the development game at this point, so steep learning curve, so I want to at least give some credit to 

* http://happytechnologist.com/?p=340 was a model I initally started from which also pointed me at the xml library
* https://znasibov.info/posts/2017/01/22/the_ultimate_guide_to_python_decorators does a good job of helping me to understand decorators
 