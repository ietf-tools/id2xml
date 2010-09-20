from models import *

class InternetDraft(Document):
    DAYS_TO_EXPIRE=185
#     id_document_tag = models.AutoField(primary_key=True)
    @property
    def id_document_tag(self):
        return self.name              # Will only work for some use cases
#     title = models.CharField(max_length=255, db_column='id_document_name')
#     id_document_key = models.CharField(max_length=255, editable=False)
    @property
    def id_document_key(self):
        return self.title.upper()
#     group = models.ForeignKey(Acronym, db_column='group_acronym_id')
    @property
    def group(self):
        return Acronym(super(Document, self).group)
#     filename = models.CharField(max_length=255, unique=True)
    @property
    def filename(self):
        return self.name
#     revision = models.CharField(max_length=2)
    @property
    def revision(self):
        return self.rev
#     revision_date = models.DateField()
    @property
    def revision_date(self):
        return self.dochistory_set().filter(rev=self.rev).dates("time","day","ASC")[0]
#     file_type = models.CharField(max_length=20)
    @property
    def file_type(self):
        return ".txt"                   # XXX should look in the repository to see what's available
#     txt_page_count = models.IntegerField()
    @property
    def txt_page_count(self):
        return self.pages
#     local_path = models.CharField(max_length=255, blank=True)
#     start_date = models.DateField()
    @property
    def start_date(self):
        return self.dochistory_set.dates("time","day","ASC")[0]
#     expiration_date = models.DateField()
    @property
    def expiration_date(self):
        return self.expiration()
#     abstract = models.TextField()
#     dunn_sent_date = models.DateField(null=True, blank=True)
#     extension_date = models.DateField(null=True, blank=True)
#     status = models.ForeignKey(IDStatus)
    @property
    def status(self):
        
#     intended_status = models.ForeignKey(IDIntendedStatus)
    @property
    def intended_status(self):
        
#     lc_sent_date = models.DateField(null=True, blank=True)
    @property
    def lc_sent_date(self):
        
#     lc_changes = models.CharField(max_length=3)
    @property
    def lc_changes(self):
        
#     lc_expiration_date = models.DateField(null=True, blank=True)
    @property
    def lc_expiration_date(self):
        
#     b_sent_date = models.DateField(null=True, blank=True)
    @property
    def b_sent_date(self):
        
#     b_discussion_date = models.DateField(null=True, blank=True)
    @property
    def b_discussion_date(self):
        
#     b_approve_date = models.DateField(null=True, blank=True)
    @property
    def b_approve_date(self):
        
#     wgreturn_date = models.DateField(null=True, blank=True)
    @property
    def wgreturn_date(self):
        
#     rfc_number = models.IntegerField(null=True, blank=True, db_index=True)
    @property
    def rfc_number(self):
        
#     comments = models.TextField(blank=True)
    @property
    def comments(self):
        
#     last_modified_date = models.DateField()
    @property
    def last_modified_date(self):
        
#     replaced_by = models.ForeignKey('self', db_column='replaced_by', blank=True, null=True, related_name='replaces_set')
    @property
    def replaced_by(self):
        
#     replaces = FKAsOneToOne('replaces', reverse=True)
    @property
    def replaces(self):
        
#     review_by_rfc_editor = models.BooleanField()
    @property
    def review_by_rfc_editor(self):
        
#     expired_tombstone = models.BooleanField()
    @property
    def expired_tombstone(self):
        
#     idinternal = FKAsOneToOne('idinternal', reverse=True, query=models.Q(rfc_flag = 0))
    @property
    def idinternal(self):
        
#     def displayname(self):
#     def displayname_current(self):
#     def displayname_with_link(self):
#     def doclink(self):
#     def doclink_current(self):
#     def group_acronym(self):
#     def __str__(self):
#     def idstate(self):
#     def revision_display(self):
#     def doctype(self):
#     def filename_with_link(self, text=None):
    def expiration(self):
        return self.revision_date + datetime.timedelta(self.DAYS_TO_EXPIRE)
#     def can_expire(self):
    class Meta:
        proxy = True
