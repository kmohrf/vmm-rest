from flask import g
from flask_restful import Resource, fields, marshal, reqparse
from vmmrest.util import flatten, validate
import validators


class ServiceList(fields.Raw):
    def format(self, value):
        return value.split(' ')

Quota = dict(
    num_messages=fields.Integer(attribute='messages'),
    num_bytes=fields.Integer(attribute='bytes')
)

Domain = dict(
    name=fields.String(attribute='domain name'),
    gid=fields.Integer(),
    services=ServiceList(attribute='active services'),
    transport=fields.String(),
    quota=fields.Nested(Quota),
    note=fields.String(),
    num_accounts=fields.Integer(attribute='accounts'),
    num_aliases=fields.Integer(attribute='aliases'),
    num_relocated=fields.Integer(attribute='relocated'),
    num_domain_catchalls=fields.Integer(attribute='catch-all dests'),
    num_domain_aliases=fields.Integer(attribute='alias domains')
)


def create_domain_object(name):
    return marshal(g.handler.domain_info(name), Domain)


class DomainCollectionResource(Resource):
    post_parser = reqparse.RequestParser()
    post_parser.add_argument('name', type=validate(validators.domain), required=True)
    post_parser.add_argument('transport', type=str, default=None, required=False)
    post_parser.add_argument('note', type=str, default=None, required=False)

    def get(self):
        gids, gid_domains = g.handler.domain_list()

        def _map(domains):
            return map(create_domain_object, domains)
        return flatten(map(_map, gid_domains.values()))

    def post(self):
        args = self.post_parser.parse_args()
        g.handler.domain_add(args.name, args.transport, args.note)
        return create_domain_object(args.name)


class DomainResource(Resource):
    def get(self, name):
        return create_domain_object(name)


def register(app, api):
    api.add_resource(DomainCollectionResource, '/domains')
    api.add_resource(DomainResource, '/domains/<name>')
