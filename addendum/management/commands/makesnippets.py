import os
import re
import codecs

from django.core.management.base import BaseCommand
from django.template import Template
from django.conf import settings

from addendum.models import Snippet
from addendum.templatetags.addendum_tags import SnippetNode


IS_ADDENDUM = r'\{\% load addendum_tags \%\}'


def _get_nodes(template):
    return template.nodelist.get_nodes_by_type(SnippetNode)


def search_snippet_nodes(template_string):
    """
    Given a valid django template string,
    compiles it and extracts all SnippetNode nodes
    """
    t = Template(template_string)
    return [node for node in _get_nodes(t)]


class Command(BaseCommand):
    help = 'Creates snippet instances from templates'

    def set_files(self):
        file_list = []
        for dr in settings.TEMPLATE_DIRS:
            for root, subFolders, files in os.walk(dr):
                for file in files:
                    file_list.append(os.path.join(root, file))
        self.files = file_list

    def search_files(self):
        for template in self.files:
            with codecs.open(template, 'r',
                             settings.DEFAULT_CHARSET) as template:
                data = template.read()

            # check if the template loads addendum
            is_addendum = re.search(IS_ADDENDUM, data)
            if is_addendum:
                snippets = search_snippet_nodes(data)
                self.parse_snippets(snippets)

    def parse_snippets(self, snippets):
        for s in snippets:
            self.founds.append({'name': s.key.literal, 'content': s.render({})})

    def handle_results(self):
        for snip in self.founds:
            snip, created = Snippet.objects.get_or_create(
                key=snip['name'],
                defaults={'text': snip['content']}
            )
            print("Snippet found: {}".format(snip.key))

    def handle(self, *args, **options):
        self.founds = []  # list for storing re.matches

        self.set_files()
        self.search_files()

        self.handle_results()
