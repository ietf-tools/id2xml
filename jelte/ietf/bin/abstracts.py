#!/usr/bin/env python
from django.conf import settings
from ietf.idtracker.models import InternetDraft, Area, Acronym, AreaGroup, IETFWG, IDAuthor
import sys

def get_intro(id_index=False):
  if id_index:
    return """              Current Internet-Drafts
    This summary sheet provides an index of each Internet-Draft.
    These drafts are listed alphabetically by Working Group acronym and
    initial post date."""
  else:
    return """              Current Internet-Drafts
    This summary sheet provides a short synopsis of each Internet-Draft
    available within the \"internet-drafts\" directory at the shadow
    sites directory.  These drafts are listed alphabetically by working
    group acronym and start date."""

def group_text(group):
  text =  group.group_acronym.name + " (" + group.group_acronym.acronym + ")"
  lines = "-" * len(text)
  return text + "\n" + lines + "\n"

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

def print_abstracts_text(acronym, no_abstracts):
  # if you want to store everythinh in a string instead of printing,
  # remember not to use str + str, but make a list for it and use join()
  if acronym:    
    groups = IETFWG.objects.filter(areagroup__area__area_acronym__acronym=acronym).order_by('group_acronym')
  else:
    groups = IETFWG.objects.all();

  print get_intro(no_abstracts)
  print ""
  print ""
  for group in groups:
    drafts = group.active_drafts()
    if len(drafts) > 0:
      print group_text(group)
      for draft in drafts:
        title_parts = []
        title_parts.append(draft_title_text(draft))
        title_parts.append(draft_authors(draft))
        title_parts.append(str(draft.revision_date))
        title_parts.append("<" + draft.filename + draft.file_type + ">")
        print wrap_and_indent(", ".join(title_parts), 80, 2)
        #print len(", ".join(title_parts))
        print ""
        if not no_abstracts:
          print wrap_and_indent(draft_abstract_text(draft), 80, 4)
          print ""
        sys.exit()
        

def usage():
  print "Usage: abstracts [OPTIONS]"
  print ""
  print "Options:"
  print "-noabstracts\t\tDo not print abstracts"
  print "-h or --help:\t\tPrint this text"
  print "-area <area acronym>\tOnly print abstracts for specific area"

# when called from command line
if __name__ == "__main__":
  no_abstracts = False
  if len(sys.argv) == 1:
    usage()
    sys.exit(1)
  for arg in sys.argv[1:]:
    if arg == "-h" or arg == "--help":
      usage()
      sys.exit(0)
    if arg == "-noabstracts":
      no_abstracts = True
    elif arg == "-all":
      area_acronym = None
    else:
      area_acronym = arg
  print_abstracts_text(area_acronym, no_abstracts)
