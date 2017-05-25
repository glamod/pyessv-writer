    # -*- coding: utf-8 -*-

"""
.. module:: write_cv.py
   :license: GPL/CeCIL
   :platform: Unix, Windows
   :synopsis: Maps raw GLAMOD GLAMOD vocab files to normalized pyessv format.

.. moduleauthor:: Mark Conway-Greenslade <momipsl@ipsl.jussieu.fr>
.. updateauthor:: Ag Stephens <ag.stephens@stfc.ac.uk>

"""
import argparse
import json
import os

import arrow
import datetime
import pyessv



# Define command line options.
_ARGS = argparse.ArgumentParser("Maps raw GLAMOD vocab files to normalized pyessv CV format.")
_ARGS.add_argument(
    "--source",
    help="Path from which raw GLAMOD vocab files will be read.",
    dest="source",
    type=str
    )

_CREATE_DATE = datetime.datetime.now()

# CV authority = GLAMOD.
_AUTHORITY = pyessv.create_authority(
    name="GLAMOD-TEAM",
    description="GLAMOD project",
    url="http://glamod.website.no/treallink/",
    create_date=_CREATE_DATE
    )

# CV scope = GLAMOD.
_SCOPE_GLAMOD = pyessv.create_scope(
    authority=_AUTHORITY,
    name="GLAMOD",
    description="Controlled Vocabularies (CVs) for use in GLAMOD",
    url="https://github.com/glamod/GLAMOD_CVs",
    create_date=_CREATE_DATE
    )

# CV scope = GLOBAL.
_SCOPE_GLOBAL = pyessv.create_scope(
    authority=_AUTHORITY,
    name="GLOBAL",
    description="Global controlled Vocabularies (CVs)",
    url="https://github.com/glamod/GLAMOD_CVs",
    create_date=_CREATE_DATE
    )

# Map of GLAMOD collections to data factories.
_COLLECTIONS_GLAMOD = {
    'frequency': None,
    'institution_id': lambda obj, name: {'postal_address': obj[name]},
    'realm': None,
    'required_global_attributes': None,
    'source_id': lambda obj, name: obj[name]
}

# Map of global collections to data factories.
_COLLECTIONS_GLOBAL = {
}

def _main(args):
    """Main entry point.

    """
    if not os.path.isdir(args.source):
        raise ValueError("GLAMOD vocab directory does not exist")

    # Create GLAMOD collections.
    for typeof, data_factory in _COLLECTIONS_GLAMOD.items():
        _create_collection_glamod(args.source, typeof, data_factory)

    # Create GLOBAL collections.
    for typeof, data_factory in _COLLECTIONS_GLOBAL.items():
        _create_collection_global(args.source, typeof, data_factory)

    # Add to the archive.
    pyessv.add(_AUTHORITY)

    # Save (to file system).
    pyessv.save()


def _create_collection_glamod(source, collection_type, data_factory):
    """Creates GLAMOD collection from a GLAMOD JSON files.

    """
    # Load GLAMOD json data.
    glamod_cv_data = _get_glamod_cv(source, collection_type, "GLAMOD_")

    # Create collection.
    collection_name = collection_type.replace("_", "-")
    collection = pyessv.create_collection(
        scope=_SCOPE_GLAMOD,
        name=collection_name,
        description="GLAMOD CV collection: ".format(collection_name),
        create_date=_CREATE_DATE
        )

    # Create terms.
    for name in glamod_cv_data:
        pyessv.create_term(
            collection=collection,
            name=name,
            description=name,
            create_date=_CREATE_DATE,
            data=data_factory(glamod_cv_data, name) if data_factory else None
            )


def _create_collection_global(source, collection_type, data_factory):
    """Creates global collection from a GLAMOD JSON files.

    """
    # Load GLAMOD json data.
    glamod_cv_data = _get_glamod_cv(source, collection_type)

    # Create collection.
    collection_name = collection_type.replace("_", "-")
    collection = pyessv.create_collection(
        scope=_SCOPE_GLOBAL,
        name=collection_name,
        description="GLOBAL CV collection: ".format(collection_name),
        create_date=_CREATE_DATE
        )

    # Create terms.
    for name in glamod_cv_data:
        pyessv.create_term(
            collection=collection,
            name=name,
            description=name,
            create_date=_CREATE_DATE,
            data=data_factory(glamod_cv_data, name) if data_factory else None
            )


def _get_glamod_cv(source, collection_type, prefix=""):
    """Returns raw GLAMOD CV data.

    """
    fname = "{}{}.json".format(prefix, collection_type)
    fpath = os.path.join(source, fname)
    with open(fpath, 'r') as fstream:
        print fpath
        return json.loads(fstream.read())[collection_type]


# Entry point.
if __name__ == '__main__':
    _main(_ARGS.parse_args())
