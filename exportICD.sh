#docker run -it --rm -v "$PWD":/app -w /app python:3.7-slim bash

#dump some csv versions of our data
sqlite3 -header -csv icd10codes.db "select diag_code  as code,short_desc,long_desc,lower(long_desc) as long_desc_search,cats.category_name as category,subcats.subcat     as subcat from icd10code left join icd10subcategory subcats on icd10code.subcat_id = subcats.subcat_id left join icd10category cats on subcats.category_id = cats.category_id;" > final_icd10.csv
sqlite3 -header -csv icd10codes.db "select category_id, category_name from icd10category;" > final_icd10category.csv
sqlite3 -header -csv icd10codes.db "select subcat_id, subcat, category_name from icd10subcategory left join icd10category cats on icd10subcategory.category_id = cats.category_id;" > final_icd10subcats.csv

