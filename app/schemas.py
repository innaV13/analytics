from marshmallow import Schema, fields, validates_schema
from  marshmallow.validate import OneOf
from marshmallow import ValidationError
from marshmallow.utils import RAISE
from datetime import  datetime

import re

def isPositiveNumber(value):
    if value < 0:
        raise ValidationError("Value must be greater than 0")

def checkWordInString(value):
    if not re.search(r'\w', value):
        raise ValidationError("The value should contains at least one letter or digit")

def checkStringLength(value):
    if len(value) > 256:
        raise ValidationError("The string length cannot be more than 256 characters")

def validateStringFileds(value):
    checkWordInString(value)
    checkStringLength(value)

def validateName(value):
    if not value:
        raise ValidationError("The value should contains at least one letter or digit")
    checkStringLength(value)

def checkRelatives(values):
    rel_dict = {}
    for v in values:
        rel_dict[v['citizen_id']] = v['relatives']
    for k,v in rel_dict.items():
        for rel in v:
            if k not in rel_dict.get(rel,[]):
                raise ValidationError("Some relatives is missing.")

def isPastDate(date):
    if date >= datetime.now():
        raise ValidationError("Date must be in past")


class CitizenSchema(Schema):
    citizen_id = fields.Integer(strict=True, required=True, validate=isPositiveNumber)
    town = fields.Str(required=True, validate=validateStringFileds)
    street = fields.Str(required=True, validate=validateStringFileds)
    building = fields.Str(required=True, validate=validateStringFileds)
    apartment = fields.Integer(strict=True, required=True, validate=isPositiveNumber)
    name = fields.Str(required=True, validate=validateName)
    birth_date = fields.DateTime(strict=True, required=True, format='%d.%m.%Y', validate=isPastDate)
    gender = fields.Str(required=True, validate=OneOf(['male','female']))
    relatives = fields.List(fields.Integer(), required=True)

    class Meta:
        strict = True
        unknown = RAISE


class ImportSchema(Schema):
    id = fields.Integer()
    citizens = fields.Nested(CitizenSchema, many=True, required=True, validate=checkRelatives)
    class Meta:
        strict = True
        unknown = RAISE

class ChangeCitizenSchema(Schema):
    town = fields.Str(validate=validateStringFileds)
    street = fields.Str(validate=validateStringFileds)
    building = fields.Str(validate=validateStringFileds)
    apartment = fields.Number(strict=True, validate=isPositiveNumber)
    name=fields.Str(validate=validateName)
    gender=fields.Str(validate=OneOf(['male','female']))
    birth_date=fields.DateTime(strict=True, format='%d.%m.%Y',validate=isPastDate)
    relatives=fields.List(fields.Integer())

    class Meta:
        strict = True
        unknown = RAISE

    @validates_schema
    def validate_notnull(self, data, **kwargs):
        if data == {}:
            raise ValidationError('Data should contains more then 0 fields')

