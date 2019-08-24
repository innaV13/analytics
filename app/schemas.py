from marshmallow import Schema, fields, validates_schema
from  marshmallow.validate import OneOf
from marshmallow import ValidationError
from marshmallow.utils import RAISE

import re

def isPositiveNumber(value):
    if value < 0:
        raise ValidationError("Quantity must be greater than 0.")

def notEmptyString(value):
    if not re.search(r'\w', value):
        raise ValidationError("Should contains one letter or digit")

def checkRelatives(values):
    rel_dict = {}
    for v in values:
        rel_dict[v['citizen_id']] = v['relatives']
    for k,v in rel_dict.items():
        for rel in v:
            if k not in rel_dict[rel]:
                raise ValidationError("Some relatives is missing")



class CitizenSchema(Schema):
    citizen_id = fields.Integer(strict=True, required=True, validate=isPositiveNumber)
    town = fields.Str(required=True, validate=notEmptyString)
    street = fields.Str(required=True, validate=notEmptyString)
    building = fields.Str(required=True, validate=notEmptyString)
    apartment = fields.Integer(strict=True, required=True, validate=isPositiveNumber)
    name = fields.Str(required=True, validate=notEmptyString)
    birth_date = fields.DateTime(strict=True, required=True, format='%d.%m.%Y')
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
    name=fields.Str(validate=notEmptyString)
    gender=fields.Str(validate=OneOf(['male','female']))
    birth_date=fields.DateTime(strict=True, format='%d.%m.%Y')
    relatives=fields.List(fields.Integer())
    town=fields.Str(validate=notEmptyString)
    street=fields.Str(validate=notEmptyString)
    building=fields.Str(validate=notEmptyString)
    apartment=fields.Number(strict=True, validate=isPositiveNumber)

    class Meta:
        strict = True
        unknown = RAISE

    @validates_schema
    def validate_notnull(self, data, **kwargs):
        if data == {}:
            raise ValidationError('at least one parameter is necessary')

