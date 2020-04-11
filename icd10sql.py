import json
import xml.etree.ElementTree as ET
import csv
import sys
from peewee import *
import datetime

class BaseModel(Model):
    # id = IntegerField(unique=True)
    date_created = TimestampField(default=datetime.datetime.now)
    date_modified = TimestampField()

class ICD10Category(BaseModel):
    category_id = IntegerField(unique=True, primary_key=True)
    category_name = CharField(255, null=False)

class ICD10SubCategory(BaseModel):
    subcat_id = CharField(15, unique=True, primary_key=True)
    first = CharField(3, null=True)
    last = CharField(3, null=True)
    subcat = CharField(255, null=True)
    category_id = ForeignKeyField(ICD10Category, backref='category')
    # category = CharField(255, null=True)

class ICD10Code(BaseModel):
    diag_code = CharField(8, unique=True, primary_key=True)
    long_desc = CharField(255,null=True)
    short_desc = CharField(255,null=True)
    subcat_id = ForeignKeyField(ICD10SubCategory, backref='subcategory', null=True)
    ext_code = CharField(1, null=True)
    ext_desc = CharField(255, null=True)

class ICD10RelatedTerm(BaseModel):
    code_id = ForeignKeyField(ICD10Code, backref='code')
    include_term = IntegerField()
    term = CharField()

    # class Meta:
    #     database = db
