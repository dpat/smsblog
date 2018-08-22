"""A class for collecting blueprints, and can be registered at a later date."""
from collections import defaultdict


class BPHandler(object):
    """
    This class collects blueprints so they can be registered with flask later.

    Collecting the blueprints(and their args) felt much easier than importing
    all the blueprints and adding them to the flask app one at a time.
    Blueprints are collected in a dictionary with their args, and then when
    registered, are all added to the specific flask app.  It worked well for
    both testing the app, and standing up the live app.
    """

    bpdict = defaultdict(dict)

    @staticmethod
    def add_blueprint(blueprint, **kwargs):
        """
        Add a blueprint and its args to the blueprint dict.

        :param blueprint: Flask.Blueprint object
        :param kwargs: dict, args for that blueprint.
        :return: None
        """
        argdict = {}
        # argdict['url_prefix'] = '/smsblog/api'
        if kwargs:
            argdict.update(**kwargs)
        BPHandler.bpdict[blueprint] = argdict

    @staticmethod
    def register_blueprints(flask_app):
        """
        Add all the blueprints in bpdict to the flask app.

        :param flask_app: Flask object
        :return: None
        """
        for blueprint in BPHandler.bpdict.keys():
            flask_app.register_blueprint(blueprint,
                                         **BPHandler.bpdict[blueprint])
