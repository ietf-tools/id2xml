#!/usr/bin/env python

from xml.dom import minidom
import datetime
import re

from ietf.idtracker.models import Acronym, InternetDraft, EmailAddress, IETFWG

class XMLDraftParser(object):
    def __init__(self, xml_content):
        self.set_content(xml_content)
        self.meta_data_errors_msg = []
        self.meta_data_errors = {}
        self.set_filename_revision()
        self.status_id = 1
        pass

    def set_content(self, content):
        self.content = content
        self.filesize = len(self.content)
        self.content_dom = minidom.parseString(self.content)

        els = self.content_dom.getElementsByTagName('front')
        if els.length < 1:
            raise Exception("XML Parse Failure: no <front> tag found")
        self.front_node = els[0]

    def set_filename_revision(self):
        doc_name = self.content_dom.documentElement.getAttribute("docName");
        matches = re.search(r'(?P<filename>draft-.+)-(?P<revision>\d+)', doc_name)
        if matches:
            self.filename = matches.group("filename")
            self.revision = matches.group("revision")
        else:
            self.add_meta_data_error('filename', 'Could not find filename')
            self.add_meta_data_error('revision', 'Could not find revision')



    def add_meta_data_error(self, key, err_msg):
        self.meta_data_errors[key] = True
        self.meta_data_errors_msg.append(err_msg)

    def get_creation_date(self):
        creation_date = getattr(self, 'creation_date', None)
        if creation_date is None:
            els = self.front_node.getElementsByTagName('date')
            if els.length > 0:
                date = els[0]
                year,month,day = None,None,1

                try:
                    month = date.getAttribute("month")
                    month = int( month )
                except ValueError:
                    month = datetime.datetime.strptime(month,'%B').month
                try:
                    year = int( date.getAttribute("year") )
                    if date.hasAttribute("day"):
                        day = int( date.getAttribute("day") )
                except ValueError:
                    self.add_meta_data_error('creation_date', 'Invalid creation date')
                    return None

                creation_date = datetime.date(year,month,day)
                self.creation_date = creation_date
        return creation_date

    def get_expected_revision(self):
        try:
            id = InternetDraft.objects.get(filename=self.filename)
            expected_revision = '%02d' % (int(id.revision)+1)
        except InternetDraft.DoesNotExist:
            expected_revision = '00'
        return expected_revision

    def get_title(self):
        title = getattr(self, 'title', None)
        if title is None:
            title = self._get_first_elements_text(self.front_node, 'title')
            self.title = title
        return title
    def get_abstract(self):
        abstract = getattr(self, 'abstract', None)
        if abstract is None:
            abstract = self._get_t_elements(self.front_node, 'abstract')
            abstract = '\n\n'.join(abstract)
            self.abstract = abstract
        return abstract
    def get_author_list(self):
        els = self.front_node.getElementsByTagName('author')
        if els.length < 1:
            return None
        out = []
        order = 1
        for author in els:
            address = XMLDraftParser._get_first_element(author, 'address')
            obj = {
                'author_order': order,
                'initials': author.getAttribute('initials'),
                'last_name': author.getAttribute('surname'),
                'full_name': author.getAttribute('fullname'),
                'organization': XMLDraftParser._get_first_elements_text(author, 'organization'),
                'email_address': XMLDraftParser._get_first_elements_text(address, 'email'),
                'URI': XMLDraftParser._get_first_elements_text(address, 'uri'),
            }
            out.append(obj)
            order += 1
        return out

    def get_wg_id(self):
        pass
    def get_group_id(self):
        pass
    def get_meta_data_fields(self):
        pass


    @staticmethod
    def _get_first_element(root_node, tag_name):
        els = root_node.getElementsByTagName(tag_name)
        if els.length < 1:
            return None
        return els[0]

    @staticmethod
    def _get_first_elements_text(root_node, tag_name):
        tag = XMLDraftParser._get_first_element(root_node, tag_name)
        return XMLDraftParser._get_all_text_nodes(tag)

    @staticmethod
    def _get_all_text_nodes(root_node):
        out = ''
        for child in root_node.childNodes:
            if isinstance(child, minidom.Text):
                out += child.data.strip()
        out = re.sub(r'\n +',r'\n',out)
        return out.strip()

    @staticmethod
    def _get_t_elements(root_node, tag_name):
        els = root_node.getElementsByTagName(tag_name)
        if els.length < 1:
            return None
        tag = els[0]
        els = tag.getElementsByTagName('t')
        out = []
        for el in els:
            out.append( XMLDraftParser._get_all_text_nodes(el) )
        return out


if __name__ == "__main__":
    import sys
    f = open( sys.argv[1] )
    dp = XMLDraftParser( f.read() )
    print dp.get_creation_date()
    print dp.get_expected_revision()
    print dp.filename
    print dp.revision
    #print dp.get_meta_data_fields()
    #print dp.get_authors_info()
    print dp.get_author_list()
    print dp.get_abstract()
