import xml.etree.ElementTree as ET
import csv
import sys
import sqlite3
from itertools import zip_longest as izip_longest  # name change in Py 3.x
from itertools import accumulate  # added in Py 3.2
from icd10sql import *

def trim_newlines(data):
    data3 = []
    data2 = data.split('\n')
    for x in data2:
        y = x.strip()
        if y: data3.append(y)
    return ''.join(data3)


def make_parser(fieldwidths):
    cuts = tuple(cut for cut in accumulate(abs(fw) for fw in fieldwidths))
    pads = tuple(fw < 0 for fw in fieldwidths)  # bool values for padding fields
    flds = tuple(izip_longest(pads, (0,) + cuts, cuts))[:-1]  # ignore final one
    parse = lambda line: tuple(line[i:j] for pad, i, j in flds if not pad)
    # optional informational function attributes
    parse.size = sum(abs(fw) for fw in fieldwidths)
    parse.fmtstring = ' '.join('{}{}'.format(abs(fw), 'x' if fw < 0 else 's')
                               for fw in fieldwidths)
    return parse


def do_diags(node, category, sectionID, exts):
    diag_code = node.find('name').text
    diag_desc = node.find('desc').text
    icd10CSV.writerow((diag_code, diag_desc, category, sectionID, subCategories[sectionID]))  # write to a .csv file
    db.execute('INSERT into xmlcodes (code, diag_name, subcatid) VALUES (?, ?, ?)', (diag_code, diag_desc, sectionID))

    seventh_char = node.find('sevenChrDef')
    if seventh_char is None:
        extensions = exts
    else:
        extensions = []
        for ext in seventh_char.findall('extension'):
            extensions.append([ext.get('char'), ext.text])

    has_diags = node.find('diag')
    if has_diags is None:
        # this is a leaf node
        for ext in extensions:
            if len(diag_code) > 3:
                ext_code = (diag_code + 'XXXXXX')[0:7] + ext[0]
            else:
                ext_code = diag_code+ '.XXX' + ext[0]
            ext_desc = diag_desc + ', ' + ext[1]
            icd10CSV.writerow(
                (ext_code, ext_desc, category, sectionID, subCategories[sectionID]))  # write to a .csv file
            db.execute('INSERT into xmlcodes (code, diag_name, subcatid, ext_char, ext_desc) VALUES (?, ?, ?, ?, ?)',
                       (ext_code, ext_desc, sectionID, ext[0], ext[1]))

    else:
        # not a leaf, check for 7th char extensions
        for diag in node.findall('diag'):
            do_diags(diag, category, sectionID, extensions)


def do_chapter(chap):
    category = chap.find('desc').text
    print('CATEGORY: ' + category)
    for section in chap.iter('sectionRef'):
        section_id = section.get('id')
        first_code = section.get('first')
        last_code = section.get('last')
        section_name = trim_newlines(section.text)
        subCategories[section_id] = {"name": section_name, "first": first_code, "last":last_code, "category": category}
        # print(section_id + ': ' +section_name)
    for section in chap.findall('section'):
        section_id = section.get('id')
        for diag in section.findall('diag'):
            do_diags(diag, category, section_id, [])


##### main #####
if __name__ == '__main__':
    # migrating to pewee, but changing how I want to do any of this
    db = SqliteDatabase('icd10codes.db')
    db.bind([ICD10Code, ICD10SubCategory, ICD10RelatedTerm])
    db.connect()
    db.drop_tables([ICD10Code, ICD10SubCategory, ICD10RelatedTerm])
    db.create_tables([ICD10SubCategory, ICD10Code, ICD10RelatedTerm])

    if (len(sys.argv) > 2):
        inputFile = sys.argv[1]
        txtInput = sys.argv[2]
    else:
        print("Usage: " + sys.argv[0] + " icd10cm_tabular_YYYY.xml icd10cm_codes_YYYY.txt")
        exit(0)

    icd10CSV = csv.writer(open('icd10codes.csv', 'w', encoding='utf-8'), quoting=csv.QUOTE_NONNUMERIC)
    icd10CSV.writerow(["code", "name", "category", "subcatid", "subcat"])

    db = sqlite3.connect('icd10merge.db')
    db.execute('''DROP TABLE IF EXISTS xmlcodes''')
    db.execute('''CREATE TABLE xmlcodes
                 (code text, diag_name text, subcatid text, ext_char text, ext_desc text )''')
    db.execute('''DROP TABLE IF EXISTS txtcodes''')
    db.execute('''CREATE TABLE txtcodes
                 (code text, short_desc text, long_desc text)''')
    db.execute('''DROP TABLE IF EXISTS xmlsubcats''')
    db.execute('''CREATE TABLE xmlsubcats
                 (id text, first text, last text, category text, subcat text)''')

    subCategories = dict()

    tree = ET.parse(inputFile)  # 'icd10cm_tabular_2020.xml'
    root = tree.getroot()

    for chap in root.iter('chapter'):
        do_chapter(chap)
        # print(chap.find('desc').text)

    subcatCSV = csv.writer(open('subcats.csv', 'w', encoding='utf-8'), quoting=csv.QUOTE_NONNUMERIC)
    subcatCSV.writerow(("id", "subcat"))
    for id, rec in subCategories.items():
        subcatCSV.writerow((id, rec['name']))
        db.execute('INSERT into xmlsubcats (id, first, last, category, subcat) VALUES (?, ?, ?, ?, ?)',
                   (id, rec['first'], rec['last'], rec['category'], rec['name'] ))

    # Now open the fixed-with text file of short/long descriptions
    fixed = open(txtInput, 'r')
    descCSV = csv.writer(open('icd10cm_order.csv', 'w', encoding='utf-8'), quoting=csv.QUOTE_NONNUMERIC)
    descCSV.writerow(["code", "is_header", "short_desc", "long_desc"])

    fieldwidths = (-5, -1, 7, -1, 1, -1, 60, -1, 255)  # negative widths represent ignored padding fields
    parse = make_parser(fieldwidths)

    print('format: {!r}, rec size: {} chars'.format(parse.fmtstring, parse.size))
    for line in fixed:
        fields = parse(line.rstrip('\n '))
        code = fields[0].rstrip(' ')
        if len(code) > 3:
            code = code[0:3] + '.' + code[3:7]

        is_header = 'True' if fields[1] == '0' else 'False'
        short_desc = fields[2].rstrip(' ')
        long_desc = fields[3].rstrip(' ')
        # print('fields: {}'.format([code, is_header, short_desc, long_desc]))
        descCSV.writerow([code, is_header, short_desc, long_desc])
        db.execute('INSERT into txtcodes (code, short_desc, long_desc) VALUES (?, ?, ?)',
                   (code, short_desc, long_desc ))

    db.commit()
    db.close()
