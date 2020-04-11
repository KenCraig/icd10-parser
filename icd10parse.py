import xml.etree.ElementTree as ET
import sys
from itertools import zip_longest as izip_longest  # name change in Py 3.x
from itertools import accumulate  # added in Py 3.2
from peewee import *
from icd10sql import ICD10Category, ICD10SubCategory, ICD10Code, ICD10RelatedTerm

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


def do_diags(node, sectionID, exts):
    diag_code = node.find('name').text
    diag_desc = node.find('desc').text
    if diag_code in icdcodes:
        rec = ICD10Code.create(diag_code=icdcodes[diag_code]['code'], short_desc=icdcodes[diag_code]['short_desc'],
                               long_desc=icdcodes[diag_code]['long_desc'], subcat_id=sectionID)
        # rec.save()

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
                ext_code = diag_code + '.XXX' + ext[0]
            ext_desc = diag_desc + ', ' + ext[1]
            if ext_code in icdcodes:
                rec = ICD10Code.create(diag_code=icdcodes[ext_code]['code'],
                                       short_desc=icdcodes[ext_code]['short_desc'],
                                       long_desc=icdcodes[ext_code]['long_desc'], subcat_id=sectionID,
                                       ext_code=ext[0], ext_desc=ext[1])
                # rec.save()

    else:
        # not a leaf, check for 7th char extensions
        for diag in node.findall('diag'):
            do_diags(diag, sectionID, extensions)


def do_chapter(chap):
    category_id = chap.find('name').text
    category = chap.find('desc').text
    rec = ICD10Category.create(category_name=category, category_id=category_id)
    # rec.save()

    print(f"CATEGORY {category_id}: {category}")
    for section in chap.iter('sectionRef'):
        section_id = section.get('id')
        first_code = section.get('first')
        last_code = section.get('last')
        section_name = trim_newlines(section.text)
        if section_id not in subCategories:
            # subCategories[section_id] = {"name": section_name, "first": first_code, "last": last_code, "category": category}
            subCategories[section_id] = True
            rec = ICD10SubCategory.create(subcat_id=section_id, first=first_code, last=last_code, subcat=section_name,
                                          category=category, category_id=category_id)
            # rec.save()

        # print(section_id + ': ' +section_name)
    for section in chap.findall('section'):
        section_id = section.get('id')
        for diag in section.findall('diag'):
            do_diags(diag, section_id, [])


##### main #####
if __name__ == '__main__':
    if (len(sys.argv) > 2):
        inputFile = sys.argv[1]
        txtInput = sys.argv[2]
    else:
        print("Usage: " + sys.argv[0] + " icd10cm_tabular_YYYY.xml icd10cm_codes_YYYY.txt")
        exit(0)

    # migrating to pewee, but changing how I want to do any of this
    db = SqliteDatabase('icd10codes.db')
    db.bind([ICD10Code, ICD10Category, ICD10SubCategory, ICD10RelatedTerm])
    db.connect()
    db.drop_tables([ICD10Code, ICD10Category, ICD10SubCategory, ICD10RelatedTerm])
    db.create_tables([ICD10Category, ICD10SubCategory, ICD10Code, ICD10RelatedTerm])

    # first parse the fixed-with text file of short/long descriptions
    # creating the large dict of icdcodes with code, long_desc, short_desc values
    fixed = open(txtInput, 'r')
    fieldwidths = (-5, -1, 7, -1, 1, -1, 60, -1, 255)  # negative widths represent ignored padding fields
    parse = make_parser(fieldwidths)

    icdcodes = dict()
    print('Text Parser: {!r}, rec size: {} chars'.format(parse.fmtstring, parse.size))
    for line in fixed:
        fields = parse(line.rstrip('\n '))
        code = fields[0].rstrip(' ')
        if len(code) > 3:
            code = code[0:3] + '.' + code[3:7]

        is_header = 'True' if fields[1] == '0' else 'False'
        short_desc = fields[2].rstrip(' ')
        long_desc = fields[3].rstrip(' ')
        icdcodes[code] = {'code': code, 'is_header': is_header, 'short_desc': short_desc, 'long_desc': long_desc}

    # then parse the xml file, to associate the subcategory/category with each of the icdcodes[*] items
    # writing into the database as we go
    subCategories = dict()
    tree = ET.parse(inputFile)  # 'icd10cm_tabular_2020.xml'
    root = tree.getroot()

    for chap in root.iter('chapter'):
        do_chapter(chap)
        db.commit() # commit db after every chapter just because
        # print(chap.find('desc').text)

    db.commit()
    db.close()
