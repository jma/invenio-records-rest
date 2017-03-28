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

"""Marshmallow based JSON serializer for records."""

from __future__ import absolute_import, print_function

import json

from rdflib import Graph

from .jsonld import JSONLDSerializer


class RDFSerializer(JSONLDSerializer):
    """RDF serializer for records.

    Note: This serializer is not suitable for serializing large number of
    records.
    """

    def __init__(self, schema_class, context, output_format='xml',
                 expanded=True, replace_refs=False):
        """Initialize record.

        :param schema_class: marshmallow schema for record validation.
        :param context: JSON-LD context.
        :param output_format: rdflib suported format,
                              usually: xml, n3, nt, trix or rdfa
        :param expanded: expanded form, compacted else.
        :param replace_refs: replace the ``$ref`` keys within the JSON.
        """
        self.output_format = output_format
        super(RDFSerializer, self).__init__(schema_class=schema_class,
                                            context=context,
                                            expanded=expanded,
                                            replace_refs=replace_refs)

    def serialize(self, pid, record, links_factory=None):
        """Serialize a single record and persistent identifier.

        :param pid: Persistent identifier instance.
        :param record: Record instance.
        :param links_factory: Factory function for the link generation,
                              which are added to the response.
        """
        obj = self.transform_record(pid, record, links_factory)
        graph = Graph().parse(data=json.dumps(obj, indent=2),
                              format='json-ld')
        result = graph.serialize(format=self.output_format, encoding='utf8')
        return result.decode('utf8')

    def serialize_search(self, pid_fetcher, search_result, links=None,
                         item_links_factory=None):
        """Serialize a search result.

        :param pid_fetcher: Persistent identifier fetcher.
        :param search_result: Elasticsearch search result.
        :param links: Dictionary of links to add to response.
        """
        data = super(RDFSerializer, self).serialize_search(
            pid_fetcher=pid_fetcher,
            search_result=search_result,
            links=links,
            item_links_factory=item_links_factory)
        hits = json.loads(data).get('hits', {})
        total = hits.get('total', 0)
        graph = Graph().parse(data=json.dumps(hits.get('hits', [])),
                              format="json-ld")
        out = ''
        if self.output_format == 'xml':
            out = '<!--  Search-Engine-Total-Number-Of-Results: %s  -->\n' \
                  % total
        else:
            out = '# Search-Engine-Total-Number-Of-Results: %s\n' % total
        return out + graph.serialize(format=self.output_format,
                                     encoding='utf8').decode('utf8')
