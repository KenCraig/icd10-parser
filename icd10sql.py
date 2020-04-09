import json
import xml.etree.ElementTree as ET
import csv
import sys
from peewee import *

class ICD10SubCategory(Model):
    subcat_id = CharField(15, unique=True)
    first = CharField(3)
    last = CharField(3)
    subcat = CharField()
    category = CharField()

    # class Meta:
    #     database = db


class ICD10Code(Model):
    diag_code = CharField(8, unique=True)
    long_name = TextField(null=True)
    short_name = TextField(null=True)
    subcat_id = ForeignKeyField(ICD10SubCategory, backref='subcategory')
    ext_char = CharField(1, null=True)
    ext_desc = CharField(null=True)

    # class Meta:
    #     database = db


class ICD10RelatedTerm(Model):
    code_id = ForeignKeyField(ICD10Code, backref='code')
    include_term = IntegerField()
    term = CharField()

    # class Meta:
    #     database = db
