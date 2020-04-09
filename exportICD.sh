
docker run -it --rm -v "$PWD":/usr/src/myapp -w /usr/src/myapp python:3.8-slim python icd10parse.py xml/icd10cm_tabular_2020.xml txt/icd10cm_order_2020.txt

sqlite3 -csv -header icd10merge.db 'select txtcodes.code as code, txtcodes.short_desc, txtcodes.long_desc, lower(txtcodes.long_desc) as long_desc_search, xmlsubcats.category, xmlsubcats.subcat
from txtcodes left join xmlcodes x on x.code = txtcodes.code left join xmlsubcats on xmlsubcats.id = x.subcatid order by code;' > final_icd10.csv
