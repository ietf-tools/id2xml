#!/usr/bin/env python
from django.conf import settings
from ietf.idtracker.models import InternetDraft, Area, Acronym, AreaGroup, IETFWG
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

def draft_title_text(draft):
  title = "\"" + draft.title + "\""
  return title + "\n"

def draft_abstract_text(draft, indent_str):
  # This function does indent, but does not perform rewrapping or
  # other cleanup on the abstract text yet. So it could certainly
  # be improved
  abstract_parts = draft.abstract.split("\n");
  join_str = "\n" + indent_str
  return indent_str + join_str.join(abstract_parts)

def print_abstracts_text(acronym, no_abstracts):
  # if you want to store everythinh in a string instead of printing,
  # remember not to use str + str, but make a list for it and use join()
  if acronym:    
    groups = IETFWG.objects.filter(areagroup__area__area_acronym__acronym=acronym)
  else:
    groups = IETFWG.objects.all();

  print get_intro(no_abstracts)
  
  for group in groups:
    drafts = group.active_drafts()
    if len(drafts) > 0:
      print group_text(group)
      for draft in drafts:
        print draft_title_text(draft)
        print ""
        if not no_abstracts:
          print draft_abstract_text(draft, "    ")
          print ""

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
