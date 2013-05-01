import os
import re

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from addendum.models import Snippet



IS_ADDENDUM = r'\{\% load addendum_tags \%\}'
SNIPPET_PATTERNS= (
    re.compile(r"""\{\% snippet \'(?P<name>\w*:\w*)\' \%\}(?P<content>.*)\{\% endsnippet \%\}""", re.UNICODE),
    re.compile(r"""\{\%snippet \'(?P<name>\w*:\w*)\' \%\}(?P<content>.*)\{\% endsnippet\%\}""", re.UNICODE),
    re.compile(r"""\{\% snippet (?P<name>\w*) \%\}(?P<content>.*)\{\% endsnippet \%\}""", re.UNICODE),
    re.compile(r"""\{\%snippet (?P<name>\w*) \%\}(?P<content>.*)\{\% endsnippet\%\}""", re.UNICODE),
    )


class Command(BaseCommand):
    help = 'Creates snippet instances from templates'

    def set_files(self):
        file_list = []
        for dr in settings.TEMPLATE_DIRS:
            for root, subFolders, files in os.walk(dr):
                for file in files:
                    file_list.append(os.path.join(root,file))
        self.files = file_list


    def search_files(self):
        for template in  self.files:
            with open(template, 'r') as template:
                data = template.read()

            is_addendum = re.search(IS_ADDENDUM, data) # check if the template loads addendum
            if is_addendum:
                for pattern in SNIPPET_PATTERNS:
                    snips = [m.groupdict() for m in pattern.finditer(data)]
                    if snips:
                        self.founds += snips 

    def handle_results(self):
        for snip in self.founds:
            snip, c = Snippet.objects.get_or_create(
                key = snip['name'],
                defaults={'text':snip['content']}
                )



    def handle(self, *args, **options):
        self.founds = [] # list for storing re.matches
        
        self.set_files()
        self.search_files()

        self.handle_results()



