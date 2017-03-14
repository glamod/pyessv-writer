    # -*- coding: utf-8 -*-

"""
.. module:: write_cv.py.py
   :license: GPL/CeCIL
   :platform: Unix, Windows
   :synopsis: Maps raw WCRP CMIP6 vocab files to normalized pyessv format.

.. moduleauthor:: Mark Conway-Greenslade <momipsl@ipsl.jussieu.fr>

"""
import argparse
import json
import os

import arrow

import pyessv



# Define command line options.
_ARGS = argparse.ArgumentParser("Maps raw WCRP CMIP6 vocab files to normalized pyessv CV format.")
_ARGS.add_argument(
    "--source",
    help="Path from which raw WCRP CMIP6 vocab files will be read.",
    dest="source",
    type=str
    )
_ARGS.add_argument(
    "--dest",
    help="Path to which pyessv formatted vocab files will be written.",
    dest="dest",
    type=str
    )

# Ensure we use fixed creation date.
_CREATE_DATE = arrow.get("20167-03-21 00:00:00.000000+0000").datetime

# CV authority = WCRP.
_AUTHORITY = pyessv.create_authority(
    name=u"WCRP",
    description=u"World Climate Research Program",
    url=u"https://www.wcrp-climate.org/wgcm-overview",
    create_date=_CREATE_DATE
    )

# CV scope = CMIP6.
_SCOPE_CMIP6 = pyessv.create_scope(
    authority=_AUTHORITY,
    name=u"CMIP6",
    description=u"Controlled Vocabularies (CVs) for use in CMIP6",
    url=u"https://github.com/WCRP-CMIP/CMIP6_CVs",
    create_date=_CREATE_DATE
    )

# CV scope = GLOBAL.
_SCOPE_GLOBAL = pyessv.create_scope(
    authority=_AUTHORITY,
    name=u"GLOBAL",
    description=u"Global controlled Vocabularies (CVs)",
    url=u"https://github.com/WCRP-CMIP/CMIP6_CVs",
    create_date=_CREATE_DATE
    )

# Map of CMIP6 collections to data factories.
_COLLECTIONS_CMIP6 = {
    'activity_id': None,
    'experiment_id': lambda obj, name: obj[name],
    'frequency': None,
    'grid_label': None,
    'institution_id': lambda obj, name: {'postal_address': obj[name]},
    'nominal_resolution': None,
    'realm': None,
    'required_global_attributes': None,
    'source_id': lambda obj, name: obj[name],
    'source_type': None,
    'table_id': None
}

# Map of global collections to data factories.
_COLLECTIONS_GLOBAL = {
    'mip_era': None
}

def _main(args):
    """Main entry point.

    """
    if not os.path.isdir(args.dest):
        raise ValueError("Archive directory does not exist")
    if not os.path.isdir(args.source):
        raise ValueError("WCRP vocab directory does not exist")

    # Create CMIP6 collections.
    for typeof, data_factory in _COLLECTIONS_CMIP6.items():
        _create_collection_cmip6(args.source, typeof, data_factory)

    # Create GLOBAL collections.
    for typeof, data_factory in _COLLECTIONS_GLOBAL.items():
        _create_collection_global(args.source, typeof, data_factory)

    # Write to file system.
    pyessv.write_authority(args.dest, _AUTHORITY)


def _create_collection_cmip6(source, collection_type, data_factory):
    """Creates cmip6 collection from a WCRP JSON files.

    """
    # Load WCRP json data.
    wcrp_cv_data = _get_wcrp_cv(source, collection_type, "CMIP6_")

    # Create collection.
    collection_name = unicode(collection_type.replace("_", "-"))
    collection = pyessv.create_collection(
        scope=_SCOPE_CMIP6,
        name=collection_name,
        description=u"WCRP CMIP6 CV collection: ".format(collection_name),
        create_date=_CREATE_DATE
        )

    # Create terms.
    for name in wcrp_cv_data:
        pyessv.create_term(
            collection=collection,
            name=name,
            data=data_factory(wcrp_cv_data, name) if data_factory else None,
            create_date=_CREATE_DATE
            )


def _create_collection_global(source, collection_type, data_factory):
    """Creates global collection from a WCRP JSON files.

    """
    # Load WCRP json data.
    wcrp_cv_data = _get_wcrp_cv(source, collection_type)

    # Create collection.
    collection_name = unicode(collection_type.replace("_", "-"))
    collection = pyessv.create_collection(
        scope=_SCOPE_GLOBAL,
        name=collection_name,
        description=u"WCRP GLOBAL CV collection: ".format(collection_name),
        create_date=_CREATE_DATE
        )

    # Create terms.
    for name in wcrp_cv_data:
        pyessv.create_term(
            collection=collection,
            name=name,
            data=data_factory(wcrp_cv_data, name) if data_factory else None,
            create_date=_CREATE_DATE
            )


def _get_wcrp_cv(source, collection_type, prefix=""):
    """Returns raw WCRP CV data.

    """
    fname = "{}{}.json".format(prefix, collection_type)
    fpath = os.path.join(source, fname)
    with open(fpath, 'r') as fstream:
        return json.loads(fstream.read())[collection_type]


# Entry point.
if __name__ == '__main__':
    _main(_ARGS.parse_args())
