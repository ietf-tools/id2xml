import subprocess

from django.conf import settings

from redesign.doc.models import Document


def search_files(files, text):
    p = subprocess.Popen(['grep', "-l", text] + files, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    paths = stdout.strip().split('\n')
    return paths


def get_drafts_with(text):
    draft_dir = settings.INTERNET_DRAFT_PATH
    last_files = ['%s%s-%s.txt' % (draft_dir, i.name, i.rev) for i in Document.objects.filter(type='draft')]
    paths = search_files(last_files, text)
    result = []
    for i in paths:
        result.append(i.replace(draft_dir, '')[:-7])
    return Document.objects.filter(type='draft', name__in=result)
