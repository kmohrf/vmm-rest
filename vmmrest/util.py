def flatten(lists):
    result = []
    for l in lists:
        result.extend(list(l))
    return result


def validate(validator, type=None):
    def _valdidate(value):
        validator(value)
        return type(value) if type is not None else value
    return _valdidate

