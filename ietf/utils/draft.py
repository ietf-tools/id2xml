#!/usr/bin/python
# -*- python -*-

"""
NAME
	%(program)s - Extract meta-information from an IETF draft.

SYNOPSIS
	%(program)s [OPTIONS] DRAFTLIST_FILE

DESCRIPTION
        Extract information about authors' names and email addresses,
        intended status and number of pages from Internet Drafts.
        The information is emitted in the form of a line containing
        xml-style attributes, prefixed with the name of the draft.

%(options)s

AUTHOR
	Written by Henrik Levkowetz, <henrik@levkowetz.com>

COPYRIGHT
	Copyright 2008 Henrik Levkowetz

	This program is free software; you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation; either version 2 of the License, or (at
	your option) any later version. There is NO WARRANTY; not even the
	implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
	PURPOSE. See the GNU General Public License for more details.

"""

import getopt
import os
import os.path
import re
import stat
import sys
import time

version = "v0.10"
program = os.path.basename(sys.argv[0])
progdir = os.path.dirname(sys.argv[0])

# ----------------------------------------------------------------------
# Data
# ----------------------------------------------------------------------


opt_debug = False

# ----------------------------------------------------------------------
# Functions
# ----------------------------------------------------------------------
def _debug(string):
    if opt_debug:
        sys.stderr.write("%s\n" % (string))

# ----------------------------------------------------------------------
def _note(string):
    sys.stdout.write("%s: %s\n" % (program, string))
    
# ----------------------------------------------------------------------
def _warn(string):
    sys.stderr.write("%s: Warning: %s\n" % (program, string))
    
# ----------------------------------------------------------------------
def _err(string):
    sys.stderr.write("%s: Error: %s\n" % (program, string))
    sys.exit(1)

# ----------------------------------------------------------------------
def _gettext(draft):
    file = os.path.join("/www/tools.ietf.org/id", draft)
    file = open(file)
    text = file.read()
    file.close()

    text = re.sub(".\x08", "", text)    # Get rid of inkribbon backspace-emphasis
    text = text.replace("\r\n", "\n")   # Convert DOS to unix
    text = text.replace("\r", "\n")     # Convert MAC to unix
    text = text.strip()

    return text

# ----------------------------------------------------------------------
def _stripheaders(lines):
    stripped = []
    debug = False
    newpage = False
    sentence = False
    haveblank = False
    for line in lines:
#         if re.search("^ *Curtis King", line):
#             debug = True
#         if re.search("^Intellectual", line):
#             debug = False
#         if debug:
#             _debug( "* newpage: %s; sentence: %s; haveblank: %s" % (newpage, sentence, haveblank))
#             _debug( "    " + line)
        line = line.rstrip()
        if re.search("\[?[Pp]age [0-9ivx]+\]?[ \t\f]*$", line, re.I):
            newpage = True
            continue
        if re.search("\f", line, re.I):
            newpage = True
            continue
        if re.search("^ *Internet.Draft.+[12][0-9][0-9][0-9] *$", line, re.I):
            newpage = True
            continue
#        if re.search("^ *Internet.Draft  +", line, re.I):
#            newpage = True
#            continue
        if re.search("^ *Draft.+[12][0-9][0-9][0-9] *$", line, re.I):
            newpage = True
            continue
        if re.search("^RFC[ -]?[0-9]+.*(  +)[12][0-9][0-9][0-9]$", line, re.I):
            newpage = True
            continue
        if re.search("^draft-[-a-z0-9_.]+.*[0-9][0-9][0-9][0-9]$", line, re.I):
            newpage = True
            continue
        if re.search("(Jan|Feb|Mar|March|Apr|April|May|Jun|June|Jul|July|Aug|Sep|Oct|Nov|Dec) (19[89][0-9]|20[0-9][0-9]) *$", line, re.I):
            newpage = True
            continue
        if newpage and re.search("^ *draft-[-a-z0-9_.]+ *$", line, re.I):
            newpage = True
            continue
        if re.search("^[^ \t]+", line):
            sentence = True
        if re.search("[^ \t]", line):
            if newpage:
                if sentence:
                    stripped += [""]
            else:
                if haveblank:
                    stripped += [""]
            haveblank = False
            sentence = False
            newpage = False
        if re.search("[.:]$", line):
            sentence = True
        if re.search("^[ \t]*$", line):
            haveblank = True
            continue
        stripped += [line]

    return stripped

# ----------------------------------------------------------------------
def getauthors(lines):
    """Extract author information from draft text.

    """
    aux = {
        "prefix": r"([Dd]e|Hadi|van|van de|van der|Ver|von)",
        "suffix": r"(jr|II|2nd|III|3rd|IV|4th)",
        "first" : r"([A-Z][-A-Za-z]*)((\.?[- ]+[A-Za-z]+)*)",
        "last"  : r"([-A-Za-z']{2,})",
        }
    authformats = [
        r" {6}(%(first)s[ \.]+((%(prefix)s )?%(last)s)( %(suffix)s)?)([, ]?(.+\.?|\(.+\.?|\)))?$" % aux,
        r" {6}(((%(prefix)s )?%(last)s)( %(suffix)s)?, %(first)s)([, ]([Ee]d\.?|\([Ee]d\.?\)))?$" % aux,
        r" {6}(%(last)s)$" % aux,
        ]
        
    ignore = [
        "Standards Track", "Current Practice", "Internet Draft", "Working Group",
        "No Affiliation", 
        ]
    # group       12                   34            5            6
    authors = []
    companies = []

    lines = _stripheaders(lines)
    
    # Collect first-page author information first
    have_blankline = False
    have_draftline = False
    for line in lines[:15]:
        #_debug( "**" + line)
        leading_space = len(re.findall("^ *", line)[0])
        line_len = len(line.rstrip())
        trailing_space = line_len <= 72 and 72 - line_len or 0
        if line_len > 60:
            # Look for centered title, break if found:
            if (leading_space > 5 and abs(leading_space - trailing_space) < 5):
                break
            for authformat in authformats:
                match = re.search(authformat, line)
                if match:
                    author = match.group(1)
                    authors += [ author ]
                    #_debug( "Line:   " + line)
                    #_debug( "Format: " + authformat)
                    _debug("Author: " + author)
        if line.strip() == "":
            if prev_blankline:
                break
            have_blankline = True
            prev_blankline = True
        else:
            prev_blankline = False
        if "draft-" in line:
            have_draftline = True
        if have_blankline and have_draftline:
            break

    found_pos = []
    for i in range(len(authors)):
        author = authors[i]
        if author == None:
            continue
        if "," in author:
            last, first = author.split(",",1)
            author = "%s %s" % (first.strip(), last.strip())
        if not " " in author:
            if "." in author:
                first, last = author.rsplit(".", 1)
                first += "."
            else:
                author = "[A-Z].+ " + author
                first, last = author.rsplit(" ", 1)
        else:
            first, last = author.rsplit(" ", 1)
        _debug("First, Last: '%s' '%s'" % (first, last))
        for author in [ "%s %s"%(first,last), "%s %s"%(last,first), ]:
            # Pattern for full author information search, based on first page author name:
            authpat = author
            # Permit expansion of first name
            authpat = re.sub("\. ", ".* ", authpat)
            authpat = re.sub("\.$", ".*", authpat)
            # Permit insertsion of middle name or initial
            authpat = re.sub(" ", "\S*( +[^ ]+)* +", authpat)
            # Permit expansion of double-name initials
            authpat = re.sub("-", ".*?-", authpat)
            # Some chinese names are shown with double-letter(latin) abbreviated given names, rather than
            # a single-letter(latin) abbreviation:
            authpat = re.sub("^([A-Z])[A-Z]+\.\*", r"\1[-\w]+", authpat) 
            authpat = "^(%s)( *\(.*\)|,( [A-Z][-A-Za-z0-9]*)?)?" % authpat
            _debug("Authpat: " + authpat)
            start = 0
            col = None
            # Find start of author info for this author (if any).
            # Scan forward from the end of the file, looking for a match to  authpath
            for j in range(len(lines)-1, 15, -1):
                # _debug( "**" + j)
                if re.search(authpat, lines[j].strip()):
                    start = j
                    line = lines[j]
                    _debug( " ==>   " + line.strip())
                    # The author info could be formatted in multiple columns...
                    columns = re.split("(    +)", line)
                    # _debug( "Columns:" + columns; sys.stdout.flush())
                    # Find which column:
                    #_debug( "Col range:" + range(len(columns)); sys.stdout.flush())

                    cols = [ c for c in range(len(columns)) if re.search(authpat+r"$", columns[c].strip()) ]
                    if cols:
                        col = cols[0]
                        if not (start, col) in found_pos:
                            found_pos += [ (start, col) ]
                            _debug( "Col:   %d" % col)
                            beg = len("".join(columns[:col]))
                            _debug( "Beg:   %d '%s'" % (beg, "".join(columns[:col])))
                            _debug( "Len:   %d" % len(columns))
                            if col == len(columns) or col == len(columns)-1:
                                end = None
                                _debug( "End1:  %s" % end)
                            else:
                                end = beg + len("".join(columns[col:col+2]))
                                _debug( "End2:  %d '%s'" % (end, "".join(columns[col:col+2])))
                            _debug( "Cut:   '%s'" % line[beg:end])
                            author = re.search(authpat, columns[col].strip()).group(1)
                            if author in companies:
                                authors[i] = None
                            else:
                                authors[i] = author
                            #_debug( "Author: %s: %s" % (author, authors[author]))
                            break
            if start and col != None:
                break
        if not authors[i]:
            continue
        if start and col != None:
            _debug("\n *" + authors[i])
            done = False
            count = 0
            keyword = False
            blanklines = 0
            for line in lines[start+1:]:
                _debug( "       " + line.strip())
                # Break on the second blank line
                if not line:
                    blanklines += 1
                    if blanklines >= 3:
                        _debug( " - Break on blanklines")
                        break
                    else:
                        continue
                else:
                    count += 1                    

                # Maybe break on author name
#                 _debug("Line: %s"%line.strip())
#                 for a in authors:
#                     if a and a not in companies:
#                         _debug("Search for: %s"%(r"(^|\W)"+re.sub("\.? ", ".* ", a)+"(\W|$)"))
                authmatch = [ a for a in authors if a and not a in companies and re.search((r"(^|\W)"+re.sub("\.? ", ".* ", a)+"(\W|$)"), line.strip()) ]
                if authmatch:
                    #_debug("     ? Other author or company ?  : %s" % authmatch)
                    if count == 1 or (count == 2 and not blanklines):
                        # First line after an author -- this is a company
                        companies += authmatch
                        companies += [ line.strip() ] # XXX fix this for columnized author list
                        _debug("       -- Companies: " + ", ".join(companies))
                        for k in range(len(authors)):
                            if authors[k] in companies:
                                authors[k] = None
                    elif not "@" in line:
                        # Break on an author name
                        _debug( " - Break on other author name")
                        break
                    else:
                        pass

                try:
                    column = line[beg:end].strip()
                except:
                    column = line

#                 if re.search("^\w+: \w+", column):
#                     keyword = True
#                 else:
#                     if keyword:
#                         # Break on transition from keyword line to something else
#                         _debug( " - Break on end of keywords")
#                         break
                        
                #_debug( "  Column text :: " + column)

                emailmatch = re.search("[-A-Za-z0-9_.+]+(@| *\(at\) *)[-A-Za-z0-9_.]+", column)
                if emailmatch and not "@" in authors[i]:
                    email = emailmatch.group(0).lower()
                    email = re.sub(" *\(at\) *", "@", email)
                    authors[i] = "%s <%s>" % (authors[i], email)
        else:
            authors[i] = None
            if not author in ignore:
                _debug("Not an author? '%s'" % (author))

    authors = [ re.sub(r" +"," ", a) for a in authors if a != None ]
    authors.sort()
    _debug(" * Final author list: " + ", ".join(authors))
    _debug("-"*72)
    return ", ".join(authors)

# ----------------------------------------------------------------------
def getpages(text, lines):
    return str(len(re.findall("\[[Pp]age [0-9ixldv]+\]", text)) or len(lines)/58)

# ----------------------------------------------------------------------
def getstatus(lines):
    for line in lines[:10]:
        status_match = re.search("^\s*Intended [Ss]tatus:\s*(.*?)   ", line)
        if status_match:
            return status_match.group(1)
    return None

# ----------------------------------------------------------------------
def _output(fields):
    sys.stdout.write("%s" % (fields["doctag"].strip()))

    def outputkey(key, fields):
        sys.stdout.write(" %s='%s'" % ( key.lower(), fields[key].strip().replace("\\", "\\\\" ).replace("'", "\\x27" ).replace("\n", "\\n")))

    keys = fields.keys()
    keys.sort()
    for key in keys:
        if fields[key] and not key in ["doctag", "eventdate"]:
            outputkey(key, fields)
    sys.stdout.write("\n")

# ----------------------------------------------------------------------
def _printmeta(timestamp, draft):
    # Initial values
    fields = {}
    fields["eventdate"] = timestamp
    fields["eventsource"] = "draft"

    if " " in draft:
        _warn("Skipping unexpected draft name: '%s'" % (program, draft))
        return

    fields["doctag"] = os.path.splitext(os.path.basename(draft))[0][:-3]
    fields["docrev"] = os.path.splitext(os.path.basename(draft))[0][-2:]

    text = _gettext(draft)
    lines = text.split("\n")

    fields["docpages"] = getpages(text, lines)
    fields["docauthors"] = getauthors(lines)
    deststatus = getstatus(lines)
    if deststatus:
        fields["docdeststatus"] = deststatus

    _output(fields)


# ----------------------------------------------------------------------
# Option processing
# ----------------------------------------------------------------------
options = ""
for line in re.findall("\n +(if|elif) +opt in \[(.+)\]:\s+#(.+)\n", open(sys.argv[0]).read()):
    if not options:
        options += "OPTIONS\n"
    options += "        %-16s %s\n" % (line[1].replace('"', ''), line[2])
options = options.strip()

# with ' < 1:' on the next line, this is a no-op:
if len(sys.argv) < 1:
    print __doc__ % globals()
    sys.exit(1)

try:
    opts, files = getopt.gnu_getopt(sys.argv[1:], "dhv", ["debug", "help", "version",])
except Exception, e:
    print "%s: %s" % (program, e)
    sys.exit(1)

# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------

def _main():
    global opt_debug, files
    # set default values, if any
    # parse options
    for opt, value in opts:
        if   opt in ["-d", "--debug"]:  # Emit debug information
            opt_debug = True;
        elif opt in ["-h", "--help"]:   # Output this help text, then exit
            print __doc__ % globals()
            sys.exit(1)
        elif opt in ["-v", "--version"]: # Output version information, then exit
            print program, version
            sys.exit(0)

    if not files:
        files = [ "-" ]

    for file in files:
        _debug( "Reading drafts from '%s'" % file)
        if file == "-":
            file = sys.stdin
        elif file.endswith(".gz"):
            file = gzip.open(file)
        else:
            file = open(file)

        if os.path.exists(file.name):
            timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(os.stat(file.name)[stat.ST_MTIME]))
        else:
            timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        for line in file:
            draft = line.strip()
            if draft.startswith("#"):
                continue
            _debug( "** Processing '%s'" % draft)
            _printmeta(timestamp, draft)

if __name__ == "__main__":
    try:
        _main()
    except KeyboardInterrupt:
        pass
