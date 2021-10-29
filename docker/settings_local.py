# Copyright The IETF Trust 2007-2019, All Rights Reserved
# -*- coding: utf-8 -*-

DATABASES = {
    "default": {
        "NAME": "ietf_utf8",
        "ENGINE": "django.db.backends.mysql",
        "USER": "django",
        "PASSWORD": "RkTkDPFnKpko",
        "OPTIONS": {
            "sql_mode": "STRICT_TRANS_TABLES",
            "init_command": 'SET storage_engine=InnoDB; SET names "utf8"',
        },
    },
}

USING_DEBUG_EMAIL_SERVER = True
EMAIL_HOST = "localhost"
EMAIL_PORT = 2025

IDSUBMIT_IDNITS_BINARY = "/usr/local/bin/idnits"

IDSUBMIT_REPOSITORY_PATH = "test/id/"
IDSUBMIT_STAGING_PATH = "test/staging/"

AGENDA_PATH = "/root/data/proceedings/"
BOFREQ_PATH = "/nonexistent"  # not on rsync yet?
CHARTER_PATH = "/root/data/charter/"
CONFLICT_REVIEW_PATH = "/root/data/conflict-review/"
FLOORPLAN_DIR = "/root/data/floor/"
INTERNET_DRAFT_PATH = "/root/data/internet-drafts/"
INTERNET_ALL_DRAFTS_ARCHIVE_DIR = INTERNET_DRAFT_PATH
INTERNET_DRAFT_ARCHIVE_DIR = INTERNET_DRAFT_PATH
RFC_PATH = "/root/data/rfc/"
STATUS_CHANGE_PATH = "/root/data/status-change/"
SUBMIT_YANG_CATALOG_MODEL_DIR = "/root/data/yang/catalogmod/"
SUBMIT_YANG_DRAFT_MODEL_DIR = "/root/data/yang/draftmod/"
SUBMIT_YANG_IANA_MODEL_DIR = "/root/data/yang/ianamod/"
SUBMIT_YANG_RFC_MODEL_DIR = "/root/data/yang/rfcmod/"