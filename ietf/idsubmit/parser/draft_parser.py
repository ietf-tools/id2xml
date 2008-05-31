#!/usr/bin/env python

import re, os
from datetime import date
from datetime import timedelta

from ietf.idtracker.models import Acronym, InternetDraft, EmailAddress, IETFWG
from ietf.idsubmit.models import IdSubmissionDetail, STATUS_CODE, SubmissionEnv


from django.conf import settings
#import subprocess

# This is used in validation in the AdjustForm, so cannot be part of the
# parser class.
def check_creation_date(chk_date):
    if chk_date is None:
        return False
    today = date.today()
    three_days = timedelta(days=3)
    if today - three_days < chk_date < today + three_days:
        return True
    else:
        return False

class DraftParser(object):

    meta_data_errors = {}
    meta_data_errors_msg = []
    filesize = 0
    filename = ""
    revision = "00"
    page_num = 0
    pages = []
    idnits_message = None
    remote_ip = None
    status_id = 0
    invalid_version = 0 
    idnits_failed = True
    content = ""
    
    def __init__(self, content):
        self.set_content(content)
        self.filesize = len(self.content)
        self.pages = self._get_content_by_pages(self.content)
        self.page_num = len(self.pages)
        self.content = ''.join(self.pages)
        #self.title = self.get_title()
        self.meta_data_errors_msg = []
        self.meta_data_errors = {}
        self.set_filename_revision()
        self.status_id = 1

    #def delete_extra_ld_blank(self,cont,heading):
    #    extra_ld_blank_m = re.search('\n( +)%s' % heading,cont)
    #    try:
    #        extra_ld_blank = extra_ld_blank_m.group(1)
    #        extra_ld_blank_re = re.compile('\n%s' % extra_ld_blank)
    #        cont = extra_ld_blank_re.sub('\n',cont)
    #    except AttributeError:
    #        pass
    #    return cont
 
    def set_content(self, content):
        self.content = content.replace('\r\n', '\n')

    def set_remote_ip(self, ip):
        self.remote_ip = ip

    def add_meta_data_error(self, key, err_msg):
        self.meta_data_errors[key] = True
        self.meta_data_errors_msg.append(err_msg)

    def set_filename_revision(self):
        filename_form1 = re.search('^ {3,}<?(draft-.+)-(\d\d).*$',self.pages[0], re.M)
        filename_form2 = re.search('(draft-.+)-(\d\d)\.txt',self.pages[0])
        for m in [filename_form1, filename_form2]:
            if m:
                (self.filename, self.revision) = m.groups()
                return
        self.filename = None
        self.add_meta_data_error('filename', 'Could not find filename')
        self.revision = None
        self.add_meta_data_error('revision', 'Could not find version')

    def check_idnits(self, file_path):
        #Check IDNITS
        path_idnits = os.path.join(settings.BASE_DIR, "idsubmit", "idnits")
        child = os.popen("%s --submitcheck %s" % (path_idnits, file_path))
        idnits_message = child.read()
        err = child.close()
        #command = "%s --checklistwarn %s" % (path_idnits, file_path)
        #p = subprocess.Popen([command], shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #err = p.stderr.readlines()
        #idnits_message = ''.join(p.stdout.readlines())
        if err:
            self.idnits_failed = True
            return "Checking idnits failed:"
        self.idnits_message = idnits_message
        # if no error
        result = re.search('[Ss]ummary: (\d+) error.+\(\*\*\).+(\d+) [Ww]arning.+\(==\)', idnits_message)
        try:
            return {'error':int(result.group(1).strip()), 'warning':int(result.group(2).strip()), 'message': idnits_message}
        except AttributeError: #No Nits Found
            self.idnits_failed = False 
            return {'error':0, 'message':idnits_message}
        except ValueError:
            self.idnits_failed = True
            return "Checking idnits failed: Cannot locate idnits script"
        
    def get_expected_revision(self):
        try:
            id = InternetDraft.objects.get(filename=self.filename)
        except InternetDraft.DoesNotExist:
            expected_revision = '00'
        else:
	    expected_revision = '%02d' % ( id.current_revision() + 1 )
        return expected_revision

    def _get_content_by_pages(self, content):
        # page_re = re.compile('\n.+\[?[Pp]age [0-9ivx]+\]?[ \t\f]*\n.+\n{1,}.+\n')
        # window version \n.+\[?[Pp]age [0-9ivx]+\]?[ \t\f]*\r\n.+\r\n{1,}(Internet-Draft.+\r\n)* v0.1
        # window version \n.+\[?[Pp]age [0-9ivx]+\]?[\s\t\f]*\r\n.+(\r\n){1,}Internet-Draft.+\s(\d\d\d\d)\r\n v0.2
        page_res = ['\n.+\[?[Pp]age [0-9ivx]+\]\s*\n+\s*\f\s*\n*.+\n+',
                    '\n.+\[?[Pp]age [0-9ivx]+\]?[\s\t\f]*\n.*\n*[Ii]{1}\w+[-\s]?[Dd]{1}\w+.+\s[0-9]{4}\n',
                    '\n.+\[?[Pp]age [0-9ivx]+\]?[\s\t\f]*\n.*\n*.+\s[0-9]{4}\n',
                    ]

        for regexp in page_res:
            pages = re.split(regexp, content)
            if len(pages) > 4:
                return pages

        # one page is better than no pages
        return [ content ]

    #def _get_header(self):
    #    headers_re = re.compile('\n\s{3,}<{0,1}draft-.+\n')
    #    return headers_re.sub('', self.content)

    def get_title(self):
        page = self.pages[0]
        # Strip all leading spaces
        lws = re.compile('^ +', re.M)
        page = re.sub(lws,'',page)
        title = None
        #
        # Possible title locations:
        # 1. between a date in the header and a status of this memo section
        # 2. after 2 or more blank lines, followed by the draft filename
        title_res = [ '\s*[0-9]{4}\)*\s*\n{2,}((\s*.+\n){2,5})\n+\s*Status of',
                      '\n{2,}((.+\n)+<{0,1}draft-.+\n)',
                      ]
        
        for regexp in title_res:
            m = re.search( regexp, page )
            if m:
                title = m.group(1)
                break 

        if title is None:
            self.add_meta_data_error('title', 'Could not find title')
            return title
        subs = [('\n*<?draft-.+\n', ''), # I-D filename
                ('\s*\n\s*', ' '), # line split -> single space
                ('\s\s+', ' '), # multiple spaces -> single space
                ('(http|https|ftp)://.*', ''), # strip URLs
                ]
        for sub in subs:
            title = re.sub(sub[0], sub[1], title)
        title = title.strip()
        # this routine is added because the max length is 255
        if (len(title.strip()) > 255):
            self.add_meta_data_error('title', 'Title has more than 255 characters')
            return None
        else:
            return title

    def _get_page_without_separator(self):
        headers_re = re.compile('\n.+expires.+[a-zA-Z]+.+[1920]+\d\d\s*[\[]page.+[\]]\n.+\nInternet[-| ]Draft.+[a-zA-Z]+ \d\d\d\d\n',re.I)
        return headers_re.sub('', self.content)

    def get_abstract(self):
        temp_content = '\n'.join(self.pages[0:4])
        #temp_content = self.delete_extra_ld_blank(temp_content,'Abstract')
        #deleting blank spaces from blank lines
        temp_content = re.sub('\n *\n','\n\n',temp_content)
        #
        # This assumes that the body of the abstract is indented.
        m = re.search('\n\s*Abstract\s*\n+((\s{2,}.+\n+)+)',temp_content)
        if m:
            abstract = m.group(1)
            # Delete anything that's not indented.
            # I don't think this could match anything because the initial
            # re only matches indented content.
            orig = abstract
            abstract = re.sub('\n\w.+\n(.*\n)+', '',abstract)
            assert( orig == abstract )
            #
            # Delete a trailing table of contents.
            abstract = re.sub('\n.*Table of Contents\s*\n+(.*\n)+','',abstract)
            #
            # (Don't) delete form feeds
            #abstract = abstract.replace('\f','')
            #
            # ???
            #abstract = re.sub('\n{2,}(?![A-Z])','\n', abstract)
            #
            # Turn 3 or more blank lines into one.
            abstract = re.sub('(\n *){3,}','\n\n',abstract)
            abstract = abstract.strip()
            #
            # Assume that there aren't any diagrams or other need to
            # retain spacing in abstracts.
            lws = re.compile('^ *', re.M)
            abstract = re.sub(lws, '', abstract)
        else:
            self.add_meta_data_error('abstract', 'Could not find abstract')
            abstract = None
        return abstract

    def get_creation_date(self):
        if hasattr(self, 'creation_date'):
            return self.creation_date
        _MONTH_NAMES = [ 'jan', 'feb', 'mar', 'apr', 'may',
                         'jun', 'jul', 'aug', 'sep', 'oct',
                         'nov', 'dec' ]
	date_res = [ r'\s{3,}(?P<month>\w+)\s+(?P<day>\d{1,2}),?\s+(?P<year>\d{4})',
		     r'\s{3,}(?P<day>\d{1,2}),?\s+(?P<month>\w+)\s+(?P<year>\d{4})',
		     r'\s{3,}(?P<day>\d{1,2})-(?P<month>\w+)-(?P<year>\d{4})',
		     # 'October 2008' - default day to today's.
		     r'\s{3,}(?P<month>\w+)\s+(?P<year>\d{4})', ]

        for regexp in date_res:
            match = re.search(regexp, self.pages[0])
            if match:
		md = match.groupdict()
		mon = md['month'][0:3].lower()
		day = int( md.get( 'day', date.today().day ) )
		year = int( md['year'] )
		try:
		    month = _MONTH_NAMES.index( mon ) + 1
		    self.creation_date = date(year, month, day)
                    return self.creation_date
		except ValueError:
		    # mon abbreviation not in _MONTH_NAMES
		    # or month or day out of range
		    pass
        self.add_meta_data_error('creation_date', 'Creation Date field is empty or the creation date is not in a proper format.')
	self.creation_date = None
        return self.creation_date

    def get_authors_info(self):
        authors_section1 = re.compile('\n {,5}[0-9]{0,2} {0,1}[\.-]?\s{0,10}([Aa]uthor|[Ee]ditor)+\'?\s?s?\'?\s?s?\s?(Address[es]{0,2})?\s?:?\s*\n+((\s{2,}.+\n+)+)\w+')
        authors_section2 = re.compile('\n {,5}[0-9]{0,2} {0,1}[\.-]?\s{0,10}([Aa]uthor|[Ee]ditor)+\'?\s?s?\'?\s?s?\s?(Address[es]{0,2})?\s?:?\s*\n+((\s*.+\n+)+)\w+')
        if self.page_num > 7:
            # get last 7 pages
            temp_content = '\n'.join(self.pages[-7:len(self.pages)])
        else:
            temp_content = self.content        
        lead_blank_re = re.compile('\n {1,}\n')
        temp_content = lead_blank_re.sub('\n\n',temp_content)
        address_not_found = True 
        for authors_re in [authors_section1, authors_section2]:
            searched_author = authors_re.search(temp_content) #looking last 7 pages
            if not searched_author: #looking entire document
                searched_author = authors_re.search(self.content)
            if searched_author:
                try:
                    authors_info = '\n\n' + searched_author.group(3).strip()
                    authors_info = authors_info.replace('ipr@ietf.org','')
                    mail_srch = re.compile(r'[\w\-][\w\-\.]+@[\w\-][\w\-\.]+[a-zA-Z]{1,4}')
                    mail_rst = mail_srch.findall(authors_info)
                    if address_not_found and mail_rst:
                        address_not_found = False
                except AttributeError:
                    authors_info = None
                    self.add_meta_data_error('authors', "Could not find the authors' information")
                if not address_not_found:
                    return authors_info
            else:
                authors_info = None
        if authors_info is None or address_not_found:
            self.add_meta_data_error('authors', "Could not find the authors' information")
        return authors_info

    #XXX This should be factored out into a utility function, since
    #XXX it's needed for submitter too, and is needed in other parts
    #XXX of the system.  In an ideal world, there should only be
    #XXX one; unfortunately, the tools tend to create multiple people
    #XXX for the same person, and manual adjustment can result in
    #XXX multiple people with the same email address.
    def _get_person_by_email(self, email):
        person_or_org = EmailAddress.objects.filter(address__exact=email)
        if person_or_org: 
            return person_or_org[0].person_or_org
        else:
            return None

    def get_author_list(self, authors_info):
        authors_list = []
        if authors_info is None:
            return authors_list
        # It's unclear what this does.
        one_word_re = re.compile(r'\n\s*[a-zA-Z]+\s*\n')
        authors_info = one_word_re.sub('\n',authors_info)
        # This appears to not accomplish anything.
        lead_blank_re = re.compile('\n {1,}\n')
        authors_info = lead_blank_re.sub('\n\n',authors_info)
        # Delete Contributors section
        #XXX test: what exactly does this delete?  Looks like it could
        #          delete the whole section if the string "ontributor"
        #          appears at the beginning
        contributor_re = re.compile('ontributor.*\n(.*\n*)+')
        authors_info = contributor_re.sub('',authors_info)
        # Delete Extra Emails, e.g.,
        # Foo Bar
        # Email: foo@one.example.com, foo_bar@two.example.net
        ex_email_re = re.compile('[;,] *[\w\-][\w\-\.]+@[\w\-][\w\-\.]+[a-zA-Z]{1,4}')
        authors_info = ex_email_re.sub('',authors_info)
        mail_srch = re.compile(r'[\w\-][\w\-\.]+@[\w\-][\w\-\.]+[a-zA-Z]{1,4}')
        name_srch = re.compile(r'\n{2,} *\w.+\n')
        #name_srch = re.compile(r'\n\s*\n\s*.+[\w|\)]\n')
        mail_rst = mail_srch.findall(authors_info)
        name_rst = name_srch.findall(authors_info)
        name_rst = filter(lambda x: not (re.search('([Pp]hone|[Ee]mail|URI)\s?:\s?', x.strip())), name_rst)
        name_rst = map(self._filter_author_name, name_rst)
        author_order = 0
        mail_list = []
        for mail in mail_rst:
            if mail in mail_list:
                # XXX This assumes that there is no corresponding entry in
                #     name_rst, since author_order does not go up.
                continue
            mail_list.append(mail)
            author_detailInfo = {'first_name':'','last_name':'','email_address':'','author_order':''}

            author_info = self._get_person_by_email(mail)
            if author_info:
                author_detailInfo['first_name'] = author_info.first_name
                author_detailInfo['last_name']  = author_info.last_name
            else:
                try: 
                    name = name_rst[author_order].split(' ')
                    author_detailInfo['first_name'] = name[0]
                    author_detailInfo['last_name']  = name[-1]
                except IndexError:
                    # Perhaps the name_rst list is out of sync with the
                    # mail_rst one, and we ran out.
                    pass
            author_detailInfo['email_address'] = mail
            author_order += 1
            author_detailInfo['author_order']  = author_order
            authors_list.append(author_detailInfo)

        return authors_list

    def _filter_author_name(self, name_line):
        filtering_words = ['[ \(]?[Ee]ditor[ \)]?', '[Pp]?h[\.]?d[\.]?']
        for word in filtering_words:
            name_line = re.sub(word, "", name_line.strip())
        return name_line

    def get_wg_id(self):
        wg_bits = self.filename.split('-')
        try:
            if wg_bits[1] == 'ietf':
                if wg_bits[2] == 'krb' and wg_bits[3] == 'wg':
                    wg_id = wg_bits[2] + '-' + wg_bits[3]
                else:
                    wg_id = wg_bits[2]
            else:
                wg_id = None
        except IndexError:
            wg_id = None
        return wg_id
    
    def get_first_two_pages(self):
        try:
            two_pages = self.pages[0] + self.pages[1]
        except IndexError:
            self.add_meta_data_error('two_pages', 'Can not find first two pages')
            two_pages = None
        return two_pages

    def get_group_id(self):
        wg_id = self.get_wg_id()
        if wg_id is None:
            group_id = Acronym.objects.get(acronym_id=Acronym.NONE)
        else:
            try:
                ac = Acronym.objects.get(acronym=wg_id)
                if IETFWG.objects.filter(group_acronym=ac,status__status_id=1,group_type__group_type_id=1).count():
                    return ac, None
                else:
                    return None, wg_id
            except Acronym.DoesNotExist:
                return None, wg_id
        return group_id, None

    def get_meta_data_fields(self):
        # meta data check routine
        self.get_authors_info()
        if self.get_creation_date():
            if not check_creation_date(self.get_creation_date()):
                self.add_meta_data_error('creation_date', STATUS_CODE[204] )
        expected_revision = self.get_expected_revision()
        self.invalid_version = int(expected_revision)
        if not self.revision == expected_revision:
            err_msg = STATUS_CODE[201] + " (Version %s is expected)" % expected_revision
            self.add_meta_data_error('revision', err_msg)
        title = self.get_title()
        abstract = self.get_abstract()
        if len(self.meta_data_errors_msg) > 0:
            self.status_id = 206
            warning_message = '<li>' + '</li>\n<li>'.join(self.meta_data_errors_msg) + '</li>'
        else:
            self.status_id = 2
            warning_message = ""
        if not self.filename or self.filename is None:
            self.filename = None
            self.revision = 'NA'
            self.status_id = 111
        elif not re.match(r'^[a-z0-9-\.]+$', self.filename):
            self.status_id = 112
        meta_data_fields = {
           'filename': self.filename,
           'revision': self.revision,
           'title': title,
           #'group': self.get_group_id(),
           'creation_date': self.get_creation_date(),
           'abstract': abstract,
           'filesize': self.filesize,
           'remote_ip': self.remote_ip,
           'first_two_pages': self.get_first_two_pages(),
           'txt_page_count': self.page_num,
           'idnits_message': self.idnits_message,
           'warning_message': warning_message,
           'remote_ip': self.remote_ip,
           'status_id': self.status_id,
           'invalid_version': self.invalid_version,
           'idnits_failed': self.idnits_failed
        }

        return meta_data_fields

    def check_dos_threshold(self):
        today = date.today()
        subenv = SubmissionEnv.objects.all()[0]
        max_same_draft_size = subenv.max_same_draft_size * 1000000;
        max_same_submitter_size = subenv.max_same_submitter_size * 1000000;
        max_same_wg_draft_size = subenv.max_same_wg_draft_size * 1000000;
        max_daily_submission_size = subenv.max_daily_submission_size * 1000000;

        cur_same_draft = IdSubmissionDetail.objects.filter(filename__exact=self.filename,
    	        					   revision__exact=self.revision,
         						   submission_date__exact=today)
        cur_same_draft_count = cur_same_draft.count()
        if (cur_same_draft_count >= subenv.max_same_draft_name):
            return "A same I-D cannot be submitted more than %d times a day." % subenv.max_same_draft_name

        cur_same_draft_size = sum([d.filesize for d in cur_same_draft])
        if (cur_same_draft_size >= max_same_draft_size):
	    return "A same I-D submission cannot exceed more than %d MByte a day." % max_same_draft_size

        cur_same_submitter = IdSubmissionDetail.objects.filter(remote_ip__exact=self.remote_ip,
							       submission_date__exact=today)
        cur_same_submitter_count = cur_same_submitter.count()
        if (cur_same_submitter_count >= subenv.max_same_submitter):
	    return "The same submitter cannot submit more than %d I-Ds a day." % subenv.max_same_submitter

        cur_same_submitter_size = sum([d.filesize for d in cur_same_submitter])
        if (cur_same_submitter_size >= max_same_submitter_size):
	    return "The same submitter cannot submit more than %d bytes of I-Ds a day." % max_same_submitter_size
        (group_id, err) = self.get_group_id()
        cur_same_wg_draft = IdSubmissionDetail.objects.filter(group=group_id, submission_date__exact=today).exclude(group=Acronym.NONE)
        cur_same_wg_draft_count = cur_same_wg_draft.count()
        if (cur_same_wg_draft_count >= subenv.max_same_wg_draft):
	    return "A same working group I-Ds cannot be submitted more than %d times a day." % subenv.max_same_wg_draft

        cur_same_wg_draft_size = sum([d.filesize for d in cur_same_wg_draft])
        if (cur_same_wg_draft_size >= max_same_wg_draft_size):
	    return "Total size of same working group I-Ds cannot exceed %d MByte a day." % max_same_wg_draft_size

        cur_daily = IdSubmissionDetail.objects.filter(submission_date__exact=today)
        cur_daily_count = cur_daily.count()
        if (cur_daily_count >= subenv.max_daily_submission):
	    return "The total number of today's submission has reached the maximum number of submission per day."

        cur_daily_size = sum([d.filesize for d in cur_daily])
        if (cur_daily_size >= max_daily_submission_size):
	    return "The total size of today's submission has reached the maximum size of submission per day."
        return False

if __name__ == "__main__":
    import sys
    f = open( sys.argv[1] )
    dp = DraftParser( f.read() )
    print dp.get_creation_date()
    print dp.get_expected_revision()
    print dp.filename
    print dp.revision
    print dp.get_meta_data_fields()
    print dp.get_authors_info()
    print dp.get_author_list( dp.get_authors_info() )
