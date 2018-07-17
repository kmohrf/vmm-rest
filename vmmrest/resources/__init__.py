from . import domain

__RESOURCES = [domain]


def register(app, api):
    for resource in __RESOURCES:
        resource.register(app, api)
