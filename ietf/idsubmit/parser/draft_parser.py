import re, os
from datetime import datetime
from datetime import date
from datetime import timedelta

from ietf.idtracker.models import Acronym, InternetDraft, EmailAddress, IDAuthor, PersonOrOrgInfo, IETFWG
from ietf.idsubmit.models import IdSubmissionDetail, STATUS_CODE, SubmissionEnv


from django.conf import settings
import subprocess

def check_creation_date(chk_date):
    if chk_date == 'Not Found':
        return False
    today = date.today()
    pre_3_day = timedelta(days=-3)
    pos_3_day = timedelta(days=3)
    if today + pre_3_day < chk_date < today + pos_3_day:
        return True
    else:
        return False

class DraftParser:

    not_found = "Not Found"
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
    idnits_failed = False

    content = ""
    
    def __init__(self, cont):
        self.set_content(cont)
        self.filesize = len(self.content)
        self.pages = self._get_content_by_pages(self.content)
        self.page_num = len(self.pages)
        self.content = ''.join(self.pages)
        #self.title = self.get_title()
        self.set_filename_revision()
        self.meta_data_errors_msg = []
        self.meta_data_errors.clear()
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
 
    def set_content(self, cont):
        new_line = re.compile('\r\n')
        self.content = new_line.sub( '\n', cont)
        extra_ld_blank_m = re.search(r'\n( +)Abstract\s*\n',self.content)
        try:
            extra_ld_blank = extra_ld_blank_m.group(1)
            extra_ld_blank_re = re.compile('\n%s' % extra_ld_blank)
            self.content = extra_ld_blank_re.sub('\n',self.content)
        except AttributeError:
            pass 

    def set_remote_ip(self, ip):
        self.remote_ip = ip

    def set_meta_data_errors(self, key, err_msg):
        self.meta_data_errors[key] = True
        self.meta_data_errors_msg.append(err_msg)

    def set_filename_revision(self):
        filename_section1 = re.search('\n {3,}<?((draft-.+)-(\d\d)).*\n',self.pages[0])
        filename_section2 = re.search('((draft-.+)-(\d\d)\.txt)',self.pages[0])
        for filename_re in [filename_section1, filename_section2]:
            #filename_re = re.search('\n {3,}<?((draft-.+)-(\d\d)).*\n',self.pages[0])
            try:
                self.filename = filename_re.group(2)
                try:
                    self.revision = filename_re.group(3)
                    return True
                except AttributeError:
                    self.revision = self.not_found
                    self.set_meta_data_errors('revision', '<li>Could not find version</li>')
            except AttributeError:
                self.filename = self.not_found
                self.revision = self.not_found
                self.set_meta_data_errors('filename', '<li>Could not find filename</li>')
                self.set_meta_data_errors('revision', '<li>Could not find version</li>')

    def check_idnits(self, file_path):
        #Check IDNITS
        path_idnits = os.path.join(settings.BASE_DIR, "idsubmit", "idnits")
        child = os.popen("%s --checklistwarn %s" % (path_idnits, file_path))
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
            id_query = InternetDraft.objects.get(filename=self.filename)
        except InternetDraft.DoesNotExist:
            expected_revision = '00'
        else:
            if id_query.status.status_id == 2 and id_query.expired_tombstone == 0:
                expected_revision = id_query.revision
            else:
                expected_revision = self.increase_revision(id_query.revision) 
        return expected_revision

    def increase_revision (self, revision):
        new_revision = int(revision) + 1
        return str(new_revision).zfill(2)

    def decrease_revision (self, revision):
        new_revision = int(revision)
        if new_revision == 0:
           return "00"
        else:
           new_revision = new_revision - 1
           return str(new_revision).zfill(2)

    def _get_content_by_pages(self, content):
        # page_re = re.compile('\n.+\[?[Pp]age [0-9ivx]+\]?[ \t\f]*\n.+\n{1,}.+\n')
        # window version \n.+\[?[Pp]age [0-9ivx]+\]?[ \t\f]*\r\n.+\r\n{1,}(Internet-Draft.+\r\n)* v0.1
        # window version \n.+\[?[Pp]age [0-9ivx]+\]?[\s\t\f]*\r\n.+(\r\n){1,}Internet-Draft.+\s(\d\d\d\d)\r\n v0.2
        page_re_list = []
        page_re_list.append(re.compile('\n.+\[?[Pp]age [0-9ivx]+\]\s*\n+\s*\f\s*\n*.+\n+'))
        page_re_list.append(re.compile('\n.+\[?[Pp]age [0-9ivx]+\]?[\s\t\f]*\n.*\n*[Ii]{1}\w+[-\s]?[Dd]{1}\w+.+\s[0-9]{4}\n'))
        page_re_list.append(re.compile('\n.+\[?[Pp]age [0-9ivx]+\]?[\s\t\f]*\n.*\n*.+\s[0-9]{4}\n'))

        for page_re in page_re_list:
            pages = page_re.split(content)
            if len(pages) > 4:
                return pages

    #def _get_header(self):
    #    headers_re = re.compile('\n\s{3,}<{0,1}draft-.+\n')
    #    return headers_re.sub('', self.content)

    def get_title(self):
        page = self.pages[0]
        lead_blank_re = re.compile('\n +')
        page = lead_blank_re.sub('\n',page)
        title_section1 = re.search('\s*[0-9]{4}\)*\s*\n{2,}((\s*.+\n){2,5})\n+\s*Status of', page)
        title_section2 = re.search('\n{2,}((.+\n)+<{0,1}draft-.+\n)', page)
        
        for title_re in [title_section1,title_section2]:
            try:
                title = title_re.group(1)
                try:
                    filename_re = re.compile('\n*<{0,1}draft-.+\n')
                    title = filename_re.sub('',title)
                    break 
                except IndexError, extradata:
                    title = self.not_found
            except AttributeError:
                title = self.not_found

        if title == self.not_found:
            self.set_meta_data_errors('title', '<li>Could not find title</li>')
            return title
        else:
            # this routine is added because the max length is 255
            if (len(title.strip()) > 255):
                self.set_meta_data_errors('title', '<li>Title has more than 255 characters</li>')
                return self.not_found
            else:
                title = re.sub('\n\s+',' ',title)
                return title.strip()

    def _get_page_without_separator(self):
        headers_re = re.compile('\n.+expires.+[a-zA-Z]+.+[1920]+\d\d\s*[\[]page.+[\]]\n.+\nInternet[-| ]Draft.+[a-zA-Z]+ \d\d\d\d\n',re.I)
        return headers_re.sub('', self.content)

    def get_abstract(self):
        if self.page_num > 4:
            temp_content = '\n'.join(self.pages[0:4])
        else:
            temp_content = self.content
        #temp_content = self.delete_extra_ld_blank(temp_content,'Abstract')
        #deleting blank spaces from blank lines
        lead_blank_re = re.compile('\n {1,}\n')
        temp_content = lead_blank_re.sub('\n\n',temp_content)
        abstract_m = re.search('\nAbstract *\n+((\s{2,}.+\n+)+)',temp_content)
        try:
            abstract = abstract_m.group(1)
            abstract_re = re.compile('\n\w.+\n(.*\n)+')
            abstract = abstract_re.sub('',abstract)
            abstract_re = re.compile('\n.*Table of Contents\s*\n+(.*\n)+')
            abstract = abstract_re.sub('',abstract)
            #abstract = abstract.replace('\f','')
            #abstract_re = re.compile(' {3,}')
            #abstract = abstract_re.sub('', abstract)
            #abstract_re = re.compile('\n{2,}(?![A-Z])')
            #abstract = abstract_re.sub('\n', abstract)
            abstract_re = re.compile('(\n *){3,}')
            abstract = abstract_re.sub('\n\n',abstract)
        except AttributeError:
            abstract = self.not_found
            self.set_meta_data_errors('abstract', '<li>Could not find abstract</li>')
        return abstract.strip()

    def get_creation_date(self):
        # \s{2,}[A-Z]{1}\w+\s[0-9]{1,2}\,\s[0-9]{4}
        _MONTH_NAMES = [ 'jan', 'feb', 'mar', 'apr', 'may',
                         'jun', 'jul', 'aug', 'sep', 'oct',
                         'nov', 'dec' ]
        #_MONTH_NAMES = [ 'january', 'february', 'march', 'april', 'may',
        #                 'june', 'july', 'august', 'september', 'october',
        #                 'november', 'december' ]
        creation_re1 = re.compile('\s{3,}\w+\s[0-9]{1,2}\,?\s[0-9]{4}')
        creation_re2 = re.compile('\s{3,}[0-9]{1,2}\,?\s\w+\s[0-9]{4}')
        creation_re3 = re.compile('\s{3,}[0-9]{1,2}-\w+-[0-9]{4}')
        search_patterns = [creation_re1, creation_re2, creation_re3]
        for creation_re in search_patterns:
            searched_date = creation_re.search(self.pages[0])
            if searched_date:
                try:
                    cdate = searched_date.group(0).strip()
                    cdate = cdate.replace('-',' ')
                    cdate_array = cdate.replace(',', '').split(' ')
                    if cdate_array[0][0:3].strip().lower() in _MONTH_NAMES:
                        month = _MONTH_NAMES.index(cdate_array[0][0:3].strip().lower()) + 1
                        return date(int(cdate_array[2]), month, int(cdate_array[1]))
                    else:
                        try:
                            month = _MONTH_NAMES.index(cdate_array[1][0:3].strip().lower()) + 1
                            return date(int(cdate_array[2]), month, int(cdate_array[0]))
                        except ValueError:
                            try:
                                month = _MONTH_NAMES.index(cdate_array[0][0:3].strip().lower()) + 1
                                return date(int(cdate_array[2]), month, int(cdate_array[0]))
                            except :
                                creation_date = self.not_found
                except AttributeError:
                    creation_date = self.not_found
            else:
                creation_date = self.not_found
        if creation_date == self.not_found:
            self.set_meta_data_errors('creation_date', '<li>Creation Date field is empty or the creation date is not in a proper format.</li>')
            creation_date = None
            #creation_date = date(2000, 1, 1)
        return creation_date

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
                    authors_info = self.not_found
                    self.set_meta_data_errors('authors', "<li>The I-D Submission tool could not find the authors' information</li>")
                if not address_not_found:
                    return authors_info
            else:
                authors_info = self.not_found
        if authors_info == self.not_found or address_not_found:
            self.set_meta_data_errors('authors', "<li>The I-D Submission tool could not find the authors' information</li>")
        return authors_info

    def _get_name_by_email(self, email):
        person_or_org = EmailAddress.objects.filter(address__exact=email)
        if person_or_org: 
            return person_or_org[0].person_or_org
        else:
            return None

    def get_author_detailInfo(self, authors_info, submission_id):
        authors_list = []
        one_word_re = re.compile(r'\n\s*[a-zA-Z]+\s*\n')
        authors_info = one_word_re.sub('\n',authors_info)
        lead_blank_re = re.compile('\n {1,}\n')
        authors_info = lead_blank_re.sub('\n\n',authors_info)
        # Delete Contributors section
        contributor_re = re.compile('ontributor.*\n(.*\n*)+')
        authors_info = contributor_re.sub('',authors_info)
        # Delete Extra Emails
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
                continue
            mail_list.append(mail)
            author_detailInfo = {'submission_id':'','first_name':'','last_name':'','email_address':'','author_order':''}
            author_detailInfo['submission_id'] = submission_id

            author_info = self._get_name_by_email(mail)
            if author_info:
                author_detailInfo['first_name'] = author_info.first_name
                author_detailInfo['last_name']  = author_info.last_name
            else:
                try: 
                    name = name_rst[author_order].split(' ')
                    author_detailInfo['first_name'] = name[0]
                    author_detailInfo['last_name']  = name[len(name)-1]
                except:
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
        wg_lists = self.filename.split('-')
        try:
            if wg_lists[1] == 'ietf':
                if wg_lists[2] == 'krb' and wg_lists[3] == 'wg':
                    wg_id = wg_lists[2] + '-' + wg_lists[3]
                else:
                    wg_id = wg_lists[2]
            else:
                wg_id = self.not_found
        except IndexError, extradata:
            wg_id = None
            #wg_id = self.not_found
            #self.set_meta_data_errors('group', '<li>Can not find working group id</li>')
        return wg_id

    #def set_file_type(self, type_list):
    #    self.file_type_list = type_list

    #def get_file_type(self):
    #    return ','.join(self.file_type_list)
    
    def get_first_two_pages(self):
        try:
            two_pages = self.pages[0] + self.pages[1]
        except IndexError, extradata:
            self.set_meta_data_errors('two_pages', '<li>Can not find first two pages</li>')
            two_pages = self.not_found
        return two_pages

    def get_group_id(self):
        wg_id = self.get_wg_id()
        if not wg_id: 
            return None, None
        elif wg_id == self.not_found:
            # Individual Document 1027
            group_id = Acronym.objects.get(acronym_id=1027)
        else:
            try:
                ac = Acronym.objects.get(acronym=self.get_wg_id())
                if IETFWG.objects.filter(group_acronym=ac,status__status_id=1,group_type__group_type_id=1).count():
                    return ac, None
                else:
                    return None, wg_id
            except Acronym.DoesNotExist:
                return None, wg_id
                #group_id = Acronym.objects.get(acronym_id=1027)
        return group_id, None

    def get_meta_data_fields(self):
        # meta data check routine
        self.get_authors_info()
        if self.get_creation_date():
            if not check_creation_date(self.get_creation_date()):
                self.set_meta_data_errors('creation_date', '<li>' + STATUS_CODE[204] + '</li>')
        # error message here
        expected_revision = self.get_expected_revision()
        self.invalid_version = int(expected_revision)
        if not self.revision == expected_revision:
            err_msg = "<li>" + STATUS_CODE[201] + "(Version %s is expected)</li>" % expected_revision
            self.set_meta_data_errors('revision', err_msg)
        title = self.get_title()
        abstract = self.get_abstract()
        if len(self.meta_data_errors_msg) > 0:
            self.status_id = 206
            warning_message = '\n'.join(self.meta_data_errors_msg) 
        else:
            self.status_id = 2
            warning_message = ""
        if not self.filename or self.filename == self.not_found:
            self.filename = self.not_found
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
           #'file_type': self.get_file_type(),
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
        import datetime
        today = datetime.date.today()
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
            return "<li> A same I-D cannot be submitted more than %d times a day. </li>" % subenv.max_same_draft_name

        cur_same_draft_size = sum([d.filesize for d in cur_same_draft])
        if (cur_same_draft_size >= max_same_draft_size):
	    return "<li> A same I-D submission cannot exceed more than %d MByte a day. </li>" % max_same_draft_size

        cur_same_submitter = IdSubmissionDetail.objects.filter(remote_ip__exact=self.remote_ip,
							       submission_date__exact=today)
        cur_same_submitter_count = cur_same_submitter.count()
        if (cur_same_submitter_count >= subenv.max_same_submitter):
	    return "<li> The same submitter cannot submit more than %d I-Ds a day. </li>" % subenv.max_same_submitter

        cur_same_submitter_size = sum([d.filesize for d in cur_same_submitter])
        if (cur_same_submitter_size >= max_same_submitter_size):
	    return "<li> A same submitter cannot submit more than %d I-Ds a day. </li>" % max_same_submitter_size
        (group_id, err) = self.get_group_id()
        cur_same_wg_draft = IdSubmissionDetail.objects.filter(group=group_id, submission_date__exact=today).exclude(group=1027)
        cur_same_wg_draft_count = cur_same_wg_draft.count()
        if (cur_same_wg_draft_count >= subenv.max_same_wg_draft):
	    return "<li> A same working group I-Ds cannot be submitted more than %d times a day. </li>" % subenv.max_same_wg_draft

        cur_same_wg_draft_size = sum([d.filesize for d in cur_same_wg_draft])
        if (cur_same_wg_draft_size >= max_same_wg_draft_size):
	    return "<li> Total size of same working group I-Ds cannot exceed %d MByte a day. </li>" % max_same_wg_draft_size

        cur_daily = IdSubmissionDetail.objects.filter(submission_date__exact=today)
        cur_daily_count = cur_daily.count()
        if (cur_daily_count >= subenv.max_daily_submission):
	    return "<li> The total number of today's submission has reached the maximum number of submission per day. </li>"

        cur_daily_size = sum([d.filesize for d in cur_daily])
        if (cur_daily_size >= max_daily_submission_size):
	    return "<li> The total size of today's submission has reached the maximum size of submission per day. </li>"
        return False
