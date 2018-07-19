from flask import request
from typing import Iterable, Generator, List, MutableMapping as MM, Mapping, Any


def is_not_none(value: Any) -> bool:
    return value is not None


def flatten(lists: Iterable[Iterable]) -> List:
    result = []
    for l in lists:
        result.extend(list(l))
    return result


def pick(_dict: MM, keys: Iterable, pop=True, default=None) -> Generator[Any, None, None]:
    for key in keys:
        yield _dict.pop(key, default) if pop else _dict.get(key, default)


def pick_first(_dict: MM, keys: Iterable, pop=True, predicate=is_not_none) -> Any:
    class _Undefined:
        pass
    for value in pick(_dict, keys, pop=pop, default=_Undefined):
        if value is _Undefined:
            continue
        elif callable(predicate) and predicate(value):
            return value
        elif value is predicate:
            return value
    return None


def drop(_dict: MM, keys: Iterable) -> MM:
    for key in keys:
        _dict.pop(key, None)
    return _dict


def assign(_dict: MM, *_dicts: Iterable[Mapping]) -> MM:
    for __dict in _dicts:
        _dict.update(__dict)
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
