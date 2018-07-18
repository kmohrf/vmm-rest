from flask import request
from typing import Iterable, List, MutableMapping


def flatten(lists: Iterable[Iterable]) -> List:
    result = []
    for l in lists:
        result.extend(list(l))
    return result


def pick(_dict: MutableMapping, keys: Iterable, pop=True, default=None) -> List:
    result = []
    for key in keys:
        value = _dict.pop(key, default) if pop else _dict.get(key, default)
        result.append(value)
    return result


def drop(_dict: MutableMapping, keys: Iterable) -> MutableMapping:
    for key in keys:
        _dict.pop(key, None)
    return _dict


def validate(validator, type=None):
    def _valdidate(value):
        validator(value)
        return type(value) if type is not None else value
    return _valdidate


def create_body_parser(schema_class):
    @staticmethod
    def _parse():
        schema = schema_class()
        return schema.load(request.get_json())
    return _parse
