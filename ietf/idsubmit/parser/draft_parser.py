import re, os
from datetime import datetime
from datetime import date
from datetime import timedelta

from ietf.idtracker.models import Acronym, InternetDraft, EmailAddress, IDAuthor, PersonOrOrgInfo
from ietf.idsubmit.models import IdSubmissionDetail, STATUS_CODE, SUBMISSION_ENV


from django.conf import settings

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
    invalid_version = False
    idnits_failed = False

    content = ""
    
    def __init__(self, cont):
        self.set_content(cont)
        self.filesize = len(self.content)
        self.pages = self._get_content_by_pages(self.content)
        self.content = ''.join(self.pages)
        self.page_num = len(self.pages)
        self.set_filename_revision()
        self.meta_data_errors_msg = []
        self.meta_data_errors.clear()
        self.status_id = 1

    def set_content(self, cont):
        new_line = re.compile('\r\n')
        self.content = new_line.sub( '\n', cont)

    def set_remote_ip(self, ip):
        self.remote_ip = ip

    def _set_meta_data_errors(self, key, err_msg):
        self.meta_data_errors[key] = True
        self.meta_data_errors_msg.append(err_msg)

    def set_filename_revision(self):
        filename_re = re.search('\n {3,}<?((draft-.+)-(\d\d)).*\n',self.pages[0])
        try:
            self.filename = filename_re.group(2)
        except AttributeError:
            self.filename = self.not_found
            self._set_meta_data_errors('filename', '<li>Can not find filename</li>')
        try:
            self.revision = filename_re.group(3)
        except AttributeError:
            self.revision = self.not_found
            self._set_meta_data_errors('revision', '<li>Can not find version</li>')

    def check_idnits(self, file_path):
        #Check IDNITS
        path_idnits = os.path.join(settings.BASE_DIR, "idsubmit", "idnits")
        child = os.popen("%s --nitcount %s" % (path_idnits, file_path))
        idnits_message = child.read()
        err = child.close()
        # error page print
        if err:
            return "Checking idnits failed: %s " % err
            self.idnits_failed = True
        self.idnits_message = idnits_message
        # if no error
        result = re.search('[Ss]ummary: (\d+) error.+\(\*\*\).+(\d+) [Ww]arning.+\(==\)', idnits_message)
        try:
            return {'error':int(result.group(1).strip()), 'warning':int(result.group(2).strip())}
        except AttributeError:
            return "Error in the idnits check "
            self.idnits_failed = True
        except ValueError:
            return "Error in the idnits check "
            self.idnits_failed = True
        
    def check_revision(self, expected_revision):
        if self.revision == expected_revision:
            return True
        else:
            self.invalid_version = True
            return False

    def get_expected_revision(self):
        try:
            id_query = InternetDraft.objects.get(filename=self.filename)
        except InternetDraft.DoesNotExist:
            expected_revision = '00'
        else:
            if id_query.status == 2 and not id_query.expired_tombstone:
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
        page_re_list.append(re.compile('\n.+\[?[Pp]age [0-9ivx]+\]?[\s\t\f]*\n.*\n*[Ii]{1}\w+[-\s]?[Dd]{1}\w+.+\s[0-9]{4}\n'))
        page_re_list.append(re.compile('\n.+\[?[Pp]age [0-9ivx]+\]?[\s\t\f]*\n.*\n*.+\s[0-9]{4}\n'))

        for page_re in page_re_list:
            pages = page_re.split(content)
            if len(pages) > 4:
                return pages

    def _get_header(self):
        headers_re = re.compile('\n\s{3,}<{0,1}draft-.+\n')
        return headers_re.sub('', self.content)

    def get_title(self):
        title_re = re.search('\s*[0-9]{4}\n{2,}((\s*.+\n){2,5})\n+Status of', self.pages[0])
        try:
            title = title_re.group(1)
            try:
                filename_re = re.compile('\n\s{3,}<{0,1}draft-.+\n')
                title = filename_re.split(title)
                title = title[0]
            except IndexError, extradata:
                title = self.not_found
        except AttributeError:
            title = self.not_found

        if title == self.not_found:
            self._set_meta_data_errors('title', '<li>Can not find title</li>')
            return title
        else:
            # this routine is added because the max length is 255
            if (len(title.strip()) > 255):
                self._set_meta_data_errors('title', '<li>Can not find title</li>')
                return self.not_found
            else:
                return title.strip()

    def _get_page_without_separator(self):
        headers_re = re.compile('\n.+expires.+[a-zA-Z]+.+[1920]+\d\d\s*[\[]page.+[\]]\n.+\nInternet[-| ]Draft.+[a-zA-Z]+ \d\d\d\d\n',re.I)
        return headers_re.sub('', self.content)

    def get_abstract(self):
        abstract_m = re.search('\nAbstract\s*\n+((\s{2,}.+\n+)+)\w.+',self.content)
        try:
            abstract = abstract_m.group(1)
            abstract_re = re.compile(' {3,}')
            abstract = abstract_re.sub('', abstract)
            abstract_re = re.compile('\n{2,}(?![A-Z])')
            abstract = abstract_re.sub('\n', abstract)
        except AttributeError:
            abstract = self.not_found
            self._set_meta_data_errors('abstract', '<li>Can not find abstract</li>')
        return abstract.strip()

    def get_creation_date(self):
        # \s{2,}[A-Z]{1}\w+\s[0-9]{1,2}\,\s[0-9]{4}
        _MONTH_NAMES = [ 'january', 'february', 'march', 'april', 'may',
                         'june', 'july', 'august', 'september', 'october',
                         'november', 'december' ]
        creation_re1 = re.compile('\s{3,}\w+\s[0-9]{1,2}\,?\s[0-9]{4}')
        creation_re2 = re.compile('\s{3,}[0-9]{1,2}\,?\s\w+\s[0-9]{4}')
        search_patterns = [creation_re1, creation_re2]
        for creation_re in search_patterns:
            searched_date = creation_re.search(self.pages[0])
            if searched_date:
                try:
                    cdate = searched_date.group(0).strip()
                    cdate_array = cdate.replace(',', '').split(' ')
                    if cdate_array[0].strip().lower() in _MONTH_NAMES:
                        month = _MONTH_NAMES.index(cdate_array[0].strip().lower()) + 1
                        return date(int(cdate_array[2]), month, int(cdate_array[1]))
                    else:
                        month = _MONTH_NAMES.index(cdate_array[1].strip().lower()) + 1
                        return date(int(cdate_array[2]), month, int(cdate_array[0]))
                except AttributeError:
                    creation_date = self.not_found
            else:
                creation_date = self.not_found
        if creation_date == self.not_found:
            self._set_meta_data_errors('creation_date', '<li>Can not find creation date</li>')
            creation_date = date(2000, 1, 1)
        return creation_date

    def check_creation_date(self, chk_date):
        if chk_date == self.not_found:
            return False
        today = date.today()
        pre_3_day = timedelta(days=-3)
        pos_3_day = timedelta(days=3)
        if today + pre_3_day < chk_date < today + pos_3_day:
            return True
        else:
            return False

    def get_authors_info(self):
        authors_section1 = re.compile('\n[0-9]{0,2}\.?\s*([Aa]uthor|[Ee]ditor)+\'?\s?s?\'?\s?s?\s?(Address[es]{0,2})?\s?:?\n{2}((\s{2,}.+\n+)+)\w+')
        authors_section2 = re.compile('\n[0-9]{0,2}\.?\s*([Aa]uthor|[Ee]ditor)+\'?\s?s?\'?\s?s?\s?(Address[es]{0,2})?\s?:?\n{2}((\s*.+\n+)+)\w+')

        for authors_re in [authors_section1, authors_section2]:
            searched_author = authors_re.search(self.content)

            if searched_author:
                try:
                    authors_info = '\n\n' + searched_author.group(3).strip()
                except AttributeError:
                    authors_info = self.not_found
                    self._set_meta_data_errors('authors', '<li>Can not find author information</li>')
                return authors_info
            else:
                authors_info = self.not_found
        if authors_info == self.not_found:
            self._set_meta_data_errors('authors', '<li>Can not find author information</li>')
        return authors_info

    def _get_name_by_email(self, email):
        person_or_org = EmailAddress.objects.filter(address__exact=email)
        if person_or_org: 
            return person_or_org[0].person_or_org
        else:
            return None

    def get_author_detailInfo(self, authors_info, submission_id):
        authors_list = []
        mail_srch = re.compile(r'[\w\-][\w\-\.]+@[\w\-][\w\-\.]+[a-zA-Z]{1,4}')
        name_srch = re.compile(r'\n\s*\n\s*.+[\w|\)]\n')
        mail_rst = mail_srch.findall(authors_info)
        name_rst = name_srch.findall(authors_info)
        name_rst = filter(lambda x: not (re.search('([Pp]hone|[Ee]mail|URI)\s?:\s?', x.strip())), name_rst)
        name_rst = map(self._filter_author_name, name_rst)
        author_order = 0
        for mail in mail_rst:
            author_detailInfo = {'submission_id':'','first_name':'','last_name':'','email_address':'','author_order':''}
            author_detailInfo['submission_id'] = submission_id

            author_info = self._get_name_by_email(mail)
            author_info = False
            if author_info:
                author_detailInfo['first_name'] = author_info.first_name
                author_detailInfo['last_name']  = author_info.last_name
            else:
                name = name_rst[author_order].split(' ')
                author_detailInfo['first_name'] = name[0]
                author_detailInfo['last_name']  = name[len(name)-1]

            author_order += 1
            author_detailInfo['email_address'] = mail
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
            wg_id = self.not_found
            self._set_meta_data_errors('group', '<li>Can not find working group id</li>')
        return wg_id

    def set_file_type(self, type_list):
        self.file_type_list = type_list

    def get_file_type(self):
        return ','.join(self.file_type_list)
    
    def get_first_two_pages(self):
        try:
            two_pages = self.pages[0] + self.pages[1]
        except IndexError, extradata:
            self._set_meta_data_errors('two_pages', '<li>Can not find first two pages</li>')
            two_pages = self.not_found
        return two_pages

    def get_group_id(self, wg_id):
        if wg_id == self.not_found:
            # Individual Document 1027
            group_id = Acronym.objects.get(acronym_id=1027)
        else:
            try:
                group_id = Acronym.objects.get(acronym=self.get_wg_id())
            except Acronym.DoesNotExist:
                group_id = Acronym.objects.get(acronym_id=1027)
        return group_id

    def get_meta_data_fields(self):
        # meta data check routine
        self.get_authors_info()
        if not self.check_creation_date(self.get_creation_date()):
            self._set_meta_data_errors('creation_date', '<li>' + STATUS_CODE[204] + '</li>')
        # error message here
        expected_revision = self.get_expected_revision()
        if not self.check_revision(expected_revision):
            err_msg = "<li>" + STATUS_CODE[201] + "(Version %s is expected)</li>" % expected_revision
            self._set_meta_data_errors('revision', err_msg)


        if len(self.meta_data_errors_msg) > 0:
            self.status_id = 206
            warning_message = "<ul>" + '\n'.join(self.meta_data_errors_msg) + "</ul>"
        else:
            self.status_id = 2
            warning_message = ""

        meta_data_fields = {
           'filename': self.filename,
           'revision': self.revision,
           'title': self.get_title(),
           'group': self.get_group_id(self.get_wg_id()),
           'creation_date': self.get_creation_date(),
           'file_type': self.get_file_type(),
           'abstract': self.get_abstract(),
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
        max_same_draft_size = SUBMISSION_ENV['max_same_draft_size'] * 1000000;
        max_same_submitter_size = SUBMISSION_ENV['max_same_submitter_size'] * 1000000;
        max_same_wg_draft_size = SUBMISSION_ENV['max_same_wg_draft_size'] * 1000000;
        max_daily_submission_size = SUBMISSION_ENV['max_daily_submission_size'] * 1000000;

        cur_same_draft = IdSubmissionDetail.objects.filter(filename__exact=self.filename,
    	        					   revision__exact=self.revision,
         						   submission_date__exact=today)
        cur_same_draft_count = cur_same_draft.count()
        if (cur_same_draft_count >= SUBMISSION_ENV['max_same_draft_name']):
            return "<li> A same I-D cannot be submitted more than $max_same_draft_name times a day. </li>"

        cur_same_draft_size = sum([d.filesize for d in cur_same_draft])
        if (cur_same_draft_size >= max_same_draft_size):
	    return "<li> A same I-D submission cannot exceed more than $max_same_draft_size MByte a day. </li>"

        cur_same_submitter = IdSubmissionDetail.objects.filter(remote_ip__exact=self.remote_ip,
							       submission_date__exact=today)
        cur_same_submitter_count = cur_same_submitter.count()
        if (cur_same_submitter_count >= SUBMISSION_ENV['max_same_submitter']):
	    return "<li> The same submitter cannot submit more than $max_same_submitter I-Ds a day. </li>"

        cur_same_submitter_size = sum([d.filesize for d in cur_same_submitter])
        if (cur_same_submitter_size >= max_same_submitter_size):
	    return "<li> A same submitter cannot submit more than $max_same_submitter I-Ds a day. </li>"

        cur_same_wg_draft = IdSubmissionDetail.objects.filter(group=self.get_group_id(self.get_wg_id()), submission_date__exact=today).exclude(group=1027)
        cur_same_wg_draft_count = cur_same_wg_draft.count()
        if (cur_same_wg_draft_count >= SUBMISSION_ENV['max_same_wg_draft']):
	    return "<li> A same working group I-Ds cannot be submitted more than $max_same_wg_draft times a day. </li>"

        cur_same_wg_draft_size = sum([d.filesize for d in cur_same_wg_draft])
        if (cur_same_wg_draft_size >= max_same_wg_draft_size):
	    return "<li> Total size of same working group I-Ds cannot exceed $max_same_wg_draft_size MByte a day. </li>"

        cur_daily = IdSubmissionDetail.objects.filter(submission_date__exact=today)
        cur_daily_count = cur_daily.count()
        if (cur_daily_count >= SUBMISSION_ENV['max_daily_submission']):
	    return "<li> The total number of today's submission has reached the maximum number of submission per day. </li>"

        cur_daily_size = sum([d.filesize for d in cur_daily])
        if (cur_daily_size >= max_daily_submission_size):
	    return "<li> The total size of today's submission has reached the maximum size of submission per day. </li>"
        return False
