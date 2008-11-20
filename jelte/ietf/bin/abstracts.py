#!/usr/bin/env python
from django.conf import settings
from django.template.loader import render_to_string
from ietf.idtracker.models import InternetDraft, Area, Acronym, AreaGroup, IETFWG, IDAuthor
import sys, os

def group_string(group):
  text =  group.group_acronym.name + " (" + group.group_acronym.acronym + ")"
  return text

def dashes_for_string(string):
  return len(string) * "-"

def draft_authors(draft):
  authors = IDAuthor.objects.filter(document=draft).order_by('author_order')
  author_names = []
  for author in authors:
    author_names.append(author.person.first_name + " " + author.person.last_name)
  return ", ".join(author_names)

def draft_title_text(draft):
  title = "\"" + draft.title + "\""
  return title

def draft_abstract_text(draft):
  # this function does nothing at the moment,
  # but cleanup functionality on the abstract
  # text should go here (like removing ^M etc)
  return draft.abstract

def wrap_and_indent(text, width=74, indent=0):
  result = []
  cur_line_words = []
  words = text.split()
  cur_len = 0
  for word in words:
    if cur_len + len(word) + indent < width:
      cur_line_words.append(word)
      cur_len = cur_len + len(word) + 1
    else:
      result.append(indent*" " + " ".join(cur_line_words))
      cur_line_words = [word]
      cur_len = len(word) + 1
  if len(cur_line_words) > 0:
    result.append(indent*" " + " ".join(cur_line_words))
  return "\n".join(result)

# if txt_file is not None, .txt output will be writte to
# that file
# if html_file is not None (eg. 1id_abstracts.html), an overview
# will be written to this file
# if html_directory is not None, html files per group will
# be created in this directory, and an overview will be
def create_abstracts_text(acronym, idlist_file, txt_file, html_file, html_directory, silent=False):
  # if you want to store everythinh in a string instead of printing,
  # remember not to use str + str, but make a list for it and use join()
  if acronym:
    groups = IETFWG.objects.filter(areagroup__area__area_acronym__acronym=acronym).order_by('group_acronym')
  else:
    groups = IETFWG.objects.all();

  group_elements = []

  for group in groups:
    if not silent:
      print group.group_acronym.acronym

    drafts = group.active_drafts()

    if len(drafts) > 0:
      group_text = group_string(group)
      
      if html_directory:
        group_html_file = open(html_directory + os.sep + group.group_acronym.acronym + ".html", "w")
      
      draft_elements = []

      for draft in drafts:
        title_text = draft_title_text(draft)
        authors_text = draft_authors(draft)
        abstract_text = draft_abstract_text(draft)
        if txt_file:
          title_parts = []
          title_parts.append(title_text)
          title_parts.append(authors_text)
          title_parts.append(str(draft.revision_date))
          title_parts.append("<" + draft.filename + draft.file_type + ">")
          
          # if wrap_and_indent is implemented as a template function
          # we wouldn't need the title_all here
          draft_elements.append({'title': title_text,
                                 'authors': authors_text,
                                 'rev_date': draft.revision_date,
                                 'filename': draft.filename + draft.file_type,
                                 'title_all': wrap_and_indent(", ".join(title_parts), 80, 2),
                                 'abstract': wrap_and_indent(abstract_text, 80, 4)
                                 })
          
      group_elements.append({'name': group_text,
           'dashes': dashes_for_string(group_text),
           'rel_url': html_directory + "/" + group.group_acronym.acronym + ".html",
           'drafts': draft_elements,
           'active_draft_count': len(drafts)
           })

      if html_directory:
        group_html_file.write(render_to_string("idtracker/idtracker_abstracts_group.html", {'drafts': draft_elements}))
        group_html_file.close()

  if txt_file:
    txt_file.write(render_to_string("idtracker/idtracker_abstracts.txt", {'groups': group_elements}))

  if idlist_file:
    idlist_file.write(render_to_string("idtracker/idtracker_idlist.txt", {'groups': group_elements}))

  if html_file:
    html_file.write(render_to_string("idtracker/idtracker_abstracts.html", {'groups': group_elements}))

def usage():
  print "Usage: abstracts [OPTIONS]"
  print ""
  print "Options:"
  print "-idindex\t\tDo not print abstracts"
  print "-h or --help:\t\tPrint this text"
  print "-area <area acronym>\tOnly print abstracts for specific area"

# when called from command line
if __name__ == "__main__":
  idlist_file = None
  txt_file = None
  html_file = None
  html_directory = None
  if len(sys.argv) == 1:
    usage()
    sys.exit(1)
  for arg in sys.argv[1:]:
    if arg == "-h" or arg == "--help":
      usage()
      sys.exit(0)
    if arg == "-idindex":
      no_abstracts = True
    elif arg == "-all":
      area_acronym = None
    elif arg == "-txt-output":
      txt_file = open("/tmp/abstr.txt", "w")
    elif arg == "-html-output":
      html_file = open("/tmp/abstr.html", "w")
    else:
      area_acronym = arg
  if html_directory and not os.path.exists(html_directory):
    os.mkdir(html_directory)
  if not os.path.isdir(html_directory):
    print "Error: ", html_directory, "exists, but is not a directory"
  create_abstracts_text(area_acronym, idlist_file, txt_file, html_file, html_directory, False)
  if (txt_file):
    txt_file.close()
  if html_file:
    html_file.close()

