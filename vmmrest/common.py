from flask_restful import fields as json_fields, marshal
from marshmallow import fields, Schema, validate
from VirtualMailManager.serviceset import SERVICES

from vmmrest.util import pick_first


class QuotaSchema(Schema):
    num_messages = fields.Integer(default=0)
    num_bytes = fields.Integer(default=0)


class ServicesField(fields.List):
    def __init__(self, **kwargs):
        super().__init__(fields.String(), validate=validate.ContainsOnly(SERVICES), **kwargs)


class ServiceList(json_fields.Raw):
    def format(self, value):
        return value.split(' ')


class FlatNested(json_fields.Nested):
    def output(self, key, obj):
        return marshal(obj, self.nested)


Quota = dict(
    num_messages=json_fields.Integer(
        attribute=lambda obj: pick_first(obj, ['messages', 'ql_messages'])),
    num_bytes=json_fields.Integer(
        attribute=lambda obj: pick_first(obj, ['bytes', 'ql_bytes'])),
)
