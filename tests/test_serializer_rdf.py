# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Invenio serializer tests."""

from __future__ import absolute_import, print_function

from invenio_pidstore.models import PersistentIdentifier
from invenio_records import Record
from marshmallow import Schema, fields

from invenio_records_rest.serializers.rdf import RDFSerializer


def test_serialize():
    """Test JSON serialize."""
    context = {
        '@context': {
            'dct': 'http://purl.org/dc/terms/',
            '@base': 'http://localhost/record/',
            'recid': '@id',
            'title': 'dct:title'
        }
    }

    class TestSchema(Schema):
        title = fields.Str(attribute='metadata.title')
        recid = fields.Str(attribute='metadata.recid')
        id = fields.Str(attribute='pid.pid_value')

    data = RDFSerializer(TestSchema, context, output_format='nt').serialize(
        PersistentIdentifier(pid_type='recid', pid_value='2'),
        Record({'title': 'title', 'recid': '2'})
    )
    assert data == '<http://localhost/record/2> ' \
                   '<http://purl.org/dc/terms/title> "title" .\n\n'


def test_serialize_search():
    """Test JSON serialize."""
    context = {
        '@context': {
            'dct': 'http://purl.org/dc/terms/',
            '@base': 'http://localhost/record/',
            'recid': '@id',
            'title': 'dct:title'
        }
    }

    class TestSchema(Schema):
        title = fields.Str(attribute='metadata.title')
        recid = fields.Str(attribute='metadata.recid')
        id = fields.Str(attribute='pid.pid_value')

    def fetcher(obj_uuid, data):
        assert obj_uuid in ['a', 'b']
        return PersistentIdentifier(pid_type='recid',
                                    pid_value=data['recid'])

    data = RDFSerializer(TestSchema, context,
                         output_format='nt').serialize_search(
        fetcher,
        dict(
            hits=dict(
                hits=[
                    {'_source': dict(title='test1', recid='1'), '_id': 'a',
                     '_version': 1},
                    {'_source': dict(title='test2', recid='2'), '_id': 'b',
                     '_version': 1},
                ],
                total=2,
            ),
            aggregations={},
        )
    )
    assert data.startswith('# Search-Engine-Total-Number-Of-Results: 2')
    assert '<http://localhost/record/2> '\
           '<http://purl.org/dc/terms/title> "test2"' in data
    assert '<http://localhost/record/1> '\
           '<http://purl.org/dc/terms/title> "test1"' in data
