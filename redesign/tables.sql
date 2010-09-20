BEGIN;
CREATE TABLE `doc_document` (
    `time` datetime NOT NULL,
    `comment` longtext NOT NULL,
    `agent_id` varchar(64),
    `type_id` integer,
    `title` varchar(255) NOT NULL,
    `state_id` varchar(8),
    `doc_stream_id` integer,
    `wg_state_id` varchar(8),
    `iesg_state_id` varchar(8),
    `iana_state_id` varchar(8),
    `rfc_state_id` varchar(8),
    `abstract` longtext NOT NULL,
    `rev` varchar(16) NOT NULL,
    `pages` integer,
    `intended_std_level_id` varchar(8),
    `ad_id` varchar(64),
    `shepherd_id` varchar(64),
    `name` varchar(255) NOT NULL PRIMARY KEY
)
;
ALTER TABLE `doc_document` ADD CONSTRAINT `agent_id_refs_address_27eabf35` FOREIGN KEY (`agent_id`) REFERENCES `person_email` (`address`);
ALTER TABLE `doc_document` ADD CONSTRAINT `ad_id_refs_address_27eabf35` FOREIGN KEY (`ad_id`) REFERENCES `person_email` (`address`);
ALTER TABLE `doc_document` ADD CONSTRAINT `shepherd_id_refs_address_27eabf35` FOREIGN KEY (`shepherd_id`) REFERENCES `person_email` (`address`);
ALTER TABLE `doc_document` ADD CONSTRAINT `intended_std_level_id_refs_slug_43eb85c1` FOREIGN KEY (`intended_std_level_id`) REFERENCES `name_stdstatusname` (`slug`);
ALTER TABLE `doc_document` ADD CONSTRAINT `iesg_state_id_refs_slug_38865336` FOREIGN KEY (`iesg_state_id`) REFERENCES `name_iesgdocstatename` (`slug`);
ALTER TABLE `doc_document` ADD CONSTRAINT `state_id_refs_slug_64f753ba` FOREIGN KEY (`state_id`) REFERENCES `name_docstatename` (`slug`);
ALTER TABLE `doc_document` ADD CONSTRAINT `wg_state_id_refs_slug_19900d46` FOREIGN KEY (`wg_state_id`) REFERENCES `name_wgdocstatename` (`slug`);
ALTER TABLE `doc_document` ADD CONSTRAINT `iana_state_id_refs_slug_76d34843` FOREIGN KEY (`iana_state_id`) REFERENCES `name_ianadocstatename` (`slug`);
ALTER TABLE `doc_document` ADD CONSTRAINT `rfc_state_id_refs_slug_6bbf2c30` FOREIGN KEY (`rfc_state_id`) REFERENCES `name_rfcdocstatename` (`slug`);
ALTER TABLE `doc_document` ADD CONSTRAINT `doc_stream_id_refs_id_473ce07e` FOREIGN KEY (`doc_stream_id`) REFERENCES `name_docstreamname` (`id`);
ALTER TABLE `doc_document` ADD CONSTRAINT `type_id_refs_id_7d950f50` FOREIGN KEY (`type_id`) REFERENCES `name_doctypename` (`id`);
CREATE TABLE `doc_dochistory` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `time` datetime NOT NULL,
    `comment` longtext NOT NULL,
    `agent_id` varchar(64),
    `type_id` integer,
    `title` varchar(255) NOT NULL,
    `state_id` varchar(8),
    `doc_stream_id` integer,
    `wg_state_id` varchar(8),
    `iesg_state_id` varchar(8),
    `iana_state_id` varchar(8),
    `rfc_state_id` varchar(8),
    `abstract` longtext NOT NULL,
    `rev` varchar(16) NOT NULL,
    `pages` integer,
    `intended_std_level_id` varchar(8),
    `ad_id` varchar(64),
    `shepherd_id` varchar(64),
    `name_id` varchar(255) NOT NULL
)
;
ALTER TABLE `doc_dochistory` ADD CONSTRAINT `agent_id_refs_address_f8d4184` FOREIGN KEY (`agent_id`) REFERENCES `person_email` (`address`);
ALTER TABLE `doc_dochistory` ADD CONSTRAINT `ad_id_refs_address_f8d4184` FOREIGN KEY (`ad_id`) REFERENCES `person_email` (`address`);
ALTER TABLE `doc_dochistory` ADD CONSTRAINT `shepherd_id_refs_address_f8d4184` FOREIGN KEY (`shepherd_id`) REFERENCES `person_email` (`address`);
ALTER TABLE `doc_dochistory` ADD CONSTRAINT `intended_std_level_id_refs_slug_23abf7f0` FOREIGN KEY (`intended_std_level_id`) REFERENCES `name_stdstatusname` (`slug`);
ALTER TABLE `doc_dochistory` ADD CONSTRAINT `iesg_state_id_refs_slug_28809733` FOREIGN KEY (`iesg_state_id`) REFERENCES `name_iesgdocstatename` (`slug`);
ALTER TABLE `doc_dochistory` ADD CONSTRAINT `state_id_refs_slug_48d4ab23` FOREIGN KEY (`state_id`) REFERENCES `name_docstatename` (`slug`);
ALTER TABLE `doc_dochistory` ADD CONSTRAINT `wg_state_id_refs_slug_c94cc23` FOREIGN KEY (`wg_state_id`) REFERENCES `name_wgdocstatename` (`slug`);
ALTER TABLE `doc_dochistory` ADD CONSTRAINT `name_id_refs_name_39a48e78` FOREIGN KEY (`name_id`) REFERENCES `doc_document` (`name`);
ALTER TABLE `doc_dochistory` ADD CONSTRAINT `iana_state_id_refs_slug_ed78f5a` FOREIGN KEY (`iana_state_id`) REFERENCES `name_ianadocstatename` (`slug`);
ALTER TABLE `doc_dochistory` ADD CONSTRAINT `rfc_state_id_refs_slug_29c1ae7f` FOREIGN KEY (`rfc_state_id`) REFERENCES `name_rfcdocstatename` (`slug`);
ALTER TABLE `doc_dochistory` ADD CONSTRAINT `doc_stream_id_refs_id_205d637f` FOREIGN KEY (`doc_stream_id`) REFERENCES `name_docstreamname` (`id`);
ALTER TABLE `doc_dochistory` ADD CONSTRAINT `type_id_refs_id_b34b2ff` FOREIGN KEY (`type_id`) REFERENCES `name_doctypename` (`id`);
CREATE TABLE `doc_infotag` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `document_id` varchar(255) NOT NULL,
    `infotag_id` varchar(8) NOT NULL
)
;
ALTER TABLE `doc_infotag` ADD CONSTRAINT `infotag_id_refs_slug_5eb38d49` FOREIGN KEY (`infotag_id`) REFERENCES `name_docinfotagname` (`slug`);
ALTER TABLE `doc_infotag` ADD CONSTRAINT `document_id_refs_name_4003710d` FOREIGN KEY (`document_id`) REFERENCES `doc_document` (`name`);
CREATE TABLE `doc_docalias` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `document_id` varchar(255) NOT NULL,
    `name` varchar(255) NOT NULL
)
;
ALTER TABLE `doc_docalias` ADD CONSTRAINT `document_id_refs_name_5a52432e` FOREIGN KEY (`document_id`) REFERENCES `doc_document` (`name`);
CREATE TABLE `doc_message` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `time` datetime NOT NULL,
    `type_id` varchar(8) NOT NULL,
    `doc_id` varchar(255) NOT NULL,
    `frm_id` varchar(64) NOT NULL,
    `subj` varchar(255) NOT NULL,
    `pos_id` varchar(8) NOT NULL,
    `text` longtext NOT NULL
)
;
ALTER TABLE `doc_message` ADD CONSTRAINT `doc_id_refs_name_28cd61a0` FOREIGN KEY (`doc_id`) REFERENCES `doc_document` (`name`);
ALTER TABLE `doc_message` ADD CONSTRAINT `frm_id_refs_address_160e7fdc` FOREIGN KEY (`frm_id`) REFERENCES `person_email` (`address`);
ALTER TABLE `doc_message` ADD CONSTRAINT `type_id_refs_slug_10f26c64` FOREIGN KEY (`type_id`) REFERENCES `name_msgtypename` (`slug`);
ALTER TABLE `doc_message` ADD CONSTRAINT `pos_id_refs_slug_5c37684d` FOREIGN KEY (`pos_id`) REFERENCES `name_ballotpositionname` (`slug`);
CREATE TABLE `doc_sendqueue` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `time` datetime NOT NULL,
    `agent_id` varchar(64) NOT NULL,
    `comment` longtext NOT NULL,
    `msg_id` integer NOT NULL,
    `to_id` varchar(64) NOT NULL,
    `send` datetime NOT NULL
)
;
ALTER TABLE `doc_sendqueue` ADD CONSTRAINT `msg_id_refs_id_215fa8cb` FOREIGN KEY (`msg_id`) REFERENCES `doc_message` (`id`);
ALTER TABLE `doc_sendqueue` ADD CONSTRAINT `agent_id_refs_address_7360e08c` FOREIGN KEY (`agent_id`) REFERENCES `person_email` (`address`);
ALTER TABLE `doc_sendqueue` ADD CONSTRAINT `to_id_refs_address_7360e08c` FOREIGN KEY (`to_id`) REFERENCES `person_email` (`address`);
CREATE TABLE `doc_ballot` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `initiated_id` integer NOT NULL,
    `deferred_id` integer,
    `last_call_id` integer,
    `closed_id` integer,
    `announced_id` integer
)
;
ALTER TABLE `doc_ballot` ADD CONSTRAINT `initiated_id_refs_id_19aefebb` FOREIGN KEY (`initiated_id`) REFERENCES `doc_message` (`id`);
ALTER TABLE `doc_ballot` ADD CONSTRAINT `deferred_id_refs_id_19aefebb` FOREIGN KEY (`deferred_id`) REFERENCES `doc_message` (`id`);
ALTER TABLE `doc_ballot` ADD CONSTRAINT `last_call_id_refs_id_19aefebb` FOREIGN KEY (`last_call_id`) REFERENCES `doc_message` (`id`);
ALTER TABLE `doc_ballot` ADD CONSTRAINT `closed_id_refs_id_19aefebb` FOREIGN KEY (`closed_id`) REFERENCES `doc_message` (`id`);
ALTER TABLE `doc_ballot` ADD CONSTRAINT `announced_id_refs_id_19aefebb` FOREIGN KEY (`announced_id`) REFERENCES `doc_message` (`id`);
CREATE TABLE `doc_document_authors` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `document_id` varchar(255) NOT NULL,
    `email_id` varchar(64) NOT NULL,
    UNIQUE (`document_id`, `email_id`)
)
;
ALTER TABLE `doc_document_authors` ADD CONSTRAINT `document_id_refs_name_5225391e` FOREIGN KEY (`document_id`) REFERENCES `doc_document` (`name`);
ALTER TABLE `doc_document_authors` ADD CONSTRAINT `email_id_refs_address_1b51152e` FOREIGN KEY (`email_id`) REFERENCES `person_email` (`address`);
CREATE TABLE `doc_document_updates` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `from_document_id` varchar(255) NOT NULL,
    `to_document_id` varchar(255) NOT NULL,
    UNIQUE (`from_document_id`, `to_document_id`)
)
;
ALTER TABLE `doc_document_updates` ADD CONSTRAINT `from_document_id_refs_name_7b222bc8` FOREIGN KEY (`from_document_id`) REFERENCES `doc_document` (`name`);
ALTER TABLE `doc_document_updates` ADD CONSTRAINT `to_document_id_refs_name_7b222bc8` FOREIGN KEY (`to_document_id`) REFERENCES `doc_document` (`name`);
CREATE TABLE `doc_document_replaces` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `from_document_id` varchar(255) NOT NULL,
    `to_document_id` varchar(255) NOT NULL,
    UNIQUE (`from_document_id`, `to_document_id`)
)
;
ALTER TABLE `doc_document_replaces` ADD CONSTRAINT `from_document_id_refs_name_13df0fce` FOREIGN KEY (`from_document_id`) REFERENCES `doc_document` (`name`);
ALTER TABLE `doc_document_replaces` ADD CONSTRAINT `to_document_id_refs_name_13df0fce` FOREIGN KEY (`to_document_id`) REFERENCES `doc_document` (`name`);
CREATE TABLE `doc_document_obsoletes` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `from_document_id` varchar(255) NOT NULL,
    `to_document_id` varchar(255) NOT NULL,
    UNIQUE (`from_document_id`, `to_document_id`)
)
;
ALTER TABLE `doc_document_obsoletes` ADD CONSTRAINT `from_document_id_refs_name_18a3d034` FOREIGN KEY (`from_document_id`) REFERENCES `doc_document` (`name`);
ALTER TABLE `doc_document_obsoletes` ADD CONSTRAINT `to_document_id_refs_name_18a3d034` FOREIGN KEY (`to_document_id`) REFERENCES `doc_document` (`name`);
CREATE TABLE `doc_document_reviews` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `from_document_id` varchar(255) NOT NULL,
    `to_document_id` varchar(255) NOT NULL,
    UNIQUE (`from_document_id`, `to_document_id`)
)
;
ALTER TABLE `doc_document_reviews` ADD CONSTRAINT `from_document_id_refs_name_7c39a32d` FOREIGN KEY (`from_document_id`) REFERENCES `doc_document` (`name`);
ALTER TABLE `doc_document_reviews` ADD CONSTRAINT `to_document_id_refs_name_7c39a32d` FOREIGN KEY (`to_document_id`) REFERENCES `doc_document` (`name`);
CREATE TABLE `doc_dochistory_authors` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `dochistory_id` integer NOT NULL,
    `email_id` varchar(64) NOT NULL,
    UNIQUE (`dochistory_id`, `email_id`)
)
;
ALTER TABLE `doc_dochistory_authors` ADD CONSTRAINT `dochistory_id_refs_id_cb0ae34` FOREIGN KEY (`dochistory_id`) REFERENCES `doc_dochistory` (`id`);
ALTER TABLE `doc_dochistory_authors` ADD CONSTRAINT `email_id_refs_address_774e2343` FOREIGN KEY (`email_id`) REFERENCES `person_email` (`address`);
CREATE TABLE `doc_dochistory_updates` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `dochistory_id` integer NOT NULL,
    `document_id` varchar(255) NOT NULL,
    UNIQUE (`dochistory_id`, `document_id`)
)
;
ALTER TABLE `doc_dochistory_updates` ADD CONSTRAINT `dochistory_id_refs_id_7f9507e2` FOREIGN KEY (`dochistory_id`) REFERENCES `doc_dochistory` (`id`);
ALTER TABLE `doc_dochistory_updates` ADD CONSTRAINT `document_id_refs_name_5426349` FOREIGN KEY (`document_id`) REFERENCES `doc_document` (`name`);
CREATE TABLE `doc_dochistory_replaces` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `dochistory_id` integer NOT NULL,
    `document_id` varchar(255) NOT NULL,
    UNIQUE (`dochistory_id`, `document_id`)
)
;
ALTER TABLE `doc_dochistory_replaces` ADD CONSTRAINT `dochistory_id_refs_id_3d7c3f06` FOREIGN KEY (`dochistory_id`) REFERENCES `doc_dochistory` (`id`);
ALTER TABLE `doc_dochistory_replaces` ADD CONSTRAINT `document_id_refs_name_76bd6ab3` FOREIGN KEY (`document_id`) REFERENCES `doc_document` (`name`);
CREATE TABLE `doc_dochistory_obsoletes` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `dochistory_id` integer NOT NULL,
    `document_id` varchar(255) NOT NULL,
    UNIQUE (`dochistory_id`, `document_id`)
)
;
ALTER TABLE `doc_dochistory_obsoletes` ADD CONSTRAINT `dochistory_id_refs_id_27baae4e` FOREIGN KEY (`dochistory_id`) REFERENCES `doc_dochistory` (`id`);
ALTER TABLE `doc_dochistory_obsoletes` ADD CONSTRAINT `document_id_refs_name_75cad495` FOREIGN KEY (`document_id`) REFERENCES `doc_document` (`name`);
CREATE TABLE `doc_dochistory_reviews` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `dochistory_id` integer NOT NULL,
    `document_id` varchar(255) NOT NULL,
    UNIQUE (`dochistory_id`, `document_id`)
)
;
ALTER TABLE `doc_dochistory_reviews` ADD CONSTRAINT `dochistory_id_refs_id_460e1ec3` FOREIGN KEY (`dochistory_id`) REFERENCES `doc_dochistory` (`id`);
ALTER TABLE `doc_dochistory_reviews` ADD CONSTRAINT `document_id_refs_name_68f4b42a` FOREIGN KEY (`document_id`) REFERENCES `doc_document` (`name`);
CREATE TABLE `doc_sendqueue_cc` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `sendqueue_id` integer NOT NULL,
    `email_id` varchar(64) NOT NULL,
    UNIQUE (`sendqueue_id`, `email_id`)
)
;
ALTER TABLE `doc_sendqueue_cc` ADD CONSTRAINT `sendqueue_id_refs_id_4995f73f` FOREIGN KEY (`sendqueue_id`) REFERENCES `doc_sendqueue` (`id`);
ALTER TABLE `doc_sendqueue_cc` ADD CONSTRAINT `email_id_refs_address_1767dd80` FOREIGN KEY (`email_id`) REFERENCES `person_email` (`address`);
CREATE TABLE `group_groupstate` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `name` varchar(32) NOT NULL
)
;
CREATE TABLE `group_grouptype` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `name` varchar(32) NOT NULL
)
;
CREATE TABLE `group_group` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `name` varchar(64) NOT NULL,
    `acronym` varchar(16) NOT NULL,
    `status_id` integer NOT NULL,
    `type_id` integer NOT NULL,
    `charter_id` varchar(255) NOT NULL,
    `parent_id` integer NOT NULL,
    `list_email` varchar(64) NOT NULL,
    `list_pages` varchar(64) NOT NULL,
    `comments` longtext NOT NULL
)
;
ALTER TABLE `group_group` ADD CONSTRAINT `type_id_refs_id_5fcffc5` FOREIGN KEY (`type_id`) REFERENCES `group_grouptype` (`id`);
ALTER TABLE `group_group` ADD CONSTRAINT `status_id_refs_id_9a8c185` FOREIGN KEY (`status_id`) REFERENCES `group_groupstate` (`id`);
ALTER TABLE `group_group` ADD CONSTRAINT `charter_id_refs_name_362a2761` FOREIGN KEY (`charter_id`) REFERENCES `doc_document` (`name`);
ALTER TABLE `group_group` ADD CONSTRAINT `parent_id_refs_id_753effb9` FOREIGN KEY (`parent_id`) REFERENCES `group_group` (`id`);
CREATE TABLE `group_grouphistory` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `group_id` integer NOT NULL,
    `time` datetime NOT NULL,
    `comment` longtext NOT NULL,
    `who_id` varchar(64) NOT NULL,
    `name` varchar(64) NOT NULL,
    `acronym` varchar(16) NOT NULL,
    `status_id` integer NOT NULL,
    `type_id` integer NOT NULL,
    `charter_id` varchar(255) NOT NULL,
    `parent_id` integer NOT NULL,
    `list_email` varchar(64) NOT NULL,
    `list_pages` varchar(64) NOT NULL,
    `comments` longtext NOT NULL
)
;
ALTER TABLE `group_grouphistory` ADD CONSTRAINT `who_id_refs_address_19a7c7b0` FOREIGN KEY (`who_id`) REFERENCES `person_email` (`address`);
ALTER TABLE `group_grouphistory` ADD CONSTRAINT `status_id_refs_id_7c02918e` FOREIGN KEY (`status_id`) REFERENCES `group_groupstate` (`id`);
ALTER TABLE `group_grouphistory` ADD CONSTRAINT `group_id_refs_id_11b8ebf4` FOREIGN KEY (`group_id`) REFERENCES `group_group` (`id`);
ALTER TABLE `group_grouphistory` ADD CONSTRAINT `parent_id_refs_id_11b8ebf4` FOREIGN KEY (`parent_id`) REFERENCES `group_group` (`id`);
ALTER TABLE `group_grouphistory` ADD CONSTRAINT `charter_id_refs_name_695367b4` FOREIGN KEY (`charter_id`) REFERENCES `doc_document` (`name`);
ALTER TABLE `group_grouphistory` ADD CONSTRAINT `type_id_refs_id_278fcbc8` FOREIGN KEY (`type_id`) REFERENCES `group_grouptype` (`id`);
CREATE TABLE `group_role` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `name_id` varchar(8) NOT NULL,
    `group_id` integer NOT NULL,
    `email_id` varchar(64) NOT NULL,
    `auth` varchar(255) NOT NULL
)
;
ALTER TABLE `group_role` ADD CONSTRAINT `group_id_refs_id_dd2da61` FOREIGN KEY (`group_id`) REFERENCES `group_group` (`id`);
ALTER TABLE `group_role` ADD CONSTRAINT `email_id_refs_address_5d4c5afb` FOREIGN KEY (`email_id`) REFERENCES `person_email` (`address`);
ALTER TABLE `group_role` ADD CONSTRAINT `name_id_refs_slug_4a5826b` FOREIGN KEY (`name_id`) REFERENCES `name_rolename` (`slug`);
CREATE TABLE `group_group_documents` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `group_id` integer NOT NULL,
    `document_id` varchar(255) NOT NULL,
    UNIQUE (`group_id`, `document_id`)
)
;
ALTER TABLE `group_group_documents` ADD CONSTRAINT `group_id_refs_id_5381bd7a` FOREIGN KEY (`group_id`) REFERENCES `group_group` (`id`);
ALTER TABLE `group_group_documents` ADD CONSTRAINT `document_id_refs_name_71e408ae` FOREIGN KEY (`document_id`) REFERENCES `doc_document` (`name`);
CREATE TABLE `group_group_chairs` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `group_id` integer NOT NULL,
    `email_id` varchar(64) NOT NULL,
    UNIQUE (`group_id`, `email_id`)
)
;
ALTER TABLE `group_group_chairs` ADD CONSTRAINT `group_id_refs_id_33a5d98b` FOREIGN KEY (`group_id`) REFERENCES `group_group` (`id`);
ALTER TABLE `group_group_chairs` ADD CONSTRAINT `email_id_refs_address_670cd899` FOREIGN KEY (`email_id`) REFERENCES `person_email` (`address`);
CREATE TABLE `group_grouphistory_documents` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `grouphistory_id` integer NOT NULL,
    `document_id` varchar(255) NOT NULL,
    UNIQUE (`grouphistory_id`, `document_id`)
)
;
ALTER TABLE `group_grouphistory_documents` ADD CONSTRAINT `grouphistory_id_refs_id_344910` FOREIGN KEY (`grouphistory_id`) REFERENCES `group_grouphistory` (`id`);
ALTER TABLE `group_grouphistory_documents` ADD CONSTRAINT `document_id_refs_name_6ad71b19` FOREIGN KEY (`document_id`) REFERENCES `doc_document` (`name`);
CREATE TABLE `group_grouphistory_chairs` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `grouphistory_id` integer NOT NULL,
    `email_id` varchar(64) NOT NULL,
    UNIQUE (`grouphistory_id`, `email_id`)
)
;
ALTER TABLE `group_grouphistory_chairs` ADD CONSTRAINT `grouphistory_id_refs_id_2761eb63` FOREIGN KEY (`grouphistory_id`) REFERENCES `group_grouphistory` (`id`);
ALTER TABLE `group_grouphistory_chairs` ADD CONSTRAINT `email_id_refs_address_348bb410` FOREIGN KEY (`email_id`) REFERENCES `person_email` (`address`);
CREATE TABLE `issue_component` (
    `text_id` varchar(255) NOT NULL PRIMARY KEY,
    `owner` varchar(64) NOT NULL,
    `description` longtext NOT NULL
)
;
ALTER TABLE `issue_component` ADD CONSTRAINT `text_id_refs_name_70ca1fa1` FOREIGN KEY (`text_id`) REFERENCES `doc_document` (`name`);
CREATE TABLE `issue_ticket` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `type` varchar(256) NOT NULL,
    `time` datetime NOT NULL,
    `changetime` datetime NOT NULL,
    `component_id` varchar(255) NOT NULL,
    `severity` varchar(256) NOT NULL,
    `priority` varchar(256) NOT NULL,
    `owner_id` varchar(64) NOT NULL,
    `reporter` varchar(256) NOT NULL,
    `cc` varchar(256) NOT NULL,
    `version` varchar(256) NOT NULL,
    `milestone` varchar(256) NOT NULL,
    `status` varchar(256) NOT NULL,
    `resolution` varchar(256) NOT NULL,
    `summary` varchar(256) NOT NULL,
    `description` varchar(256) NOT NULL,
    `keywords` varchar(256) NOT NULL
)
;
ALTER TABLE `issue_ticket` ADD CONSTRAINT `owner_id_refs_address_71f0fae9` FOREIGN KEY (`owner_id`) REFERENCES `person_email` (`address`);
ALTER TABLE `issue_ticket` ADD CONSTRAINT `component_id_refs_text_id_46dbf49b` FOREIGN KEY (`component_id`) REFERENCES `issue_component` (`text_id`);
CREATE TABLE `name_rolename` (
    `slug` varchar(8) NOT NULL PRIMARY KEY,
    `name` varchar(32) NOT NULL,
    `desc` longtext,
    `used` bool NOT NULL
)
;
CREATE TABLE `name_docstreamname` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `name` varchar(32) NOT NULL,
    `slug` varchar(8) NOT NULL,
    `desc` longtext,
    `used` bool NOT NULL
)
;
CREATE TABLE `name_docstatename` (
    `slug` varchar(8) NOT NULL PRIMARY KEY,
    `name` varchar(32) NOT NULL,
    `desc` longtext,
    `used` bool NOT NULL
)
;
CREATE TABLE `name_wgdocstatename` (
    `slug` varchar(8) NOT NULL PRIMARY KEY,
    `name` varchar(32) NOT NULL,
    `desc` longtext,
    `used` bool NOT NULL
)
;
CREATE TABLE `name_iesgdocstatename` (
    `slug` varchar(8) NOT NULL PRIMARY KEY,
    `name` varchar(32) NOT NULL,
    `desc` longtext,
    `used` bool NOT NULL
)
;
CREATE TABLE `name_ianadocstatename` (
    `slug` varchar(8) NOT NULL PRIMARY KEY,
    `name` varchar(32) NOT NULL,
    `desc` longtext,
    `used` bool NOT NULL
)
;
CREATE TABLE `name_rfcdocstatename` (
    `slug` varchar(8) NOT NULL PRIMARY KEY,
    `name` varchar(32) NOT NULL,
    `desc` longtext,
    `used` bool NOT NULL
)
;
CREATE TABLE `name_doctypename` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `name` varchar(32) NOT NULL,
    `slug` varchar(8) NOT NULL,
    `desc` longtext,
    `used` bool NOT NULL
)
;
CREATE TABLE `name_docinfotagname` (
    `slug` varchar(8) NOT NULL PRIMARY KEY,
    `name` varchar(32) NOT NULL,
    `desc` longtext,
    `used` bool NOT NULL
)
;
CREATE TABLE `name_stdstatusname` (
    `slug` varchar(8) NOT NULL PRIMARY KEY,
    `name` varchar(32) NOT NULL,
    `desc` longtext,
    `used` bool NOT NULL
)
;
CREATE TABLE `name_msgtypename` (
    `slug` varchar(8) NOT NULL PRIMARY KEY,
    `name` varchar(32) NOT NULL,
    `desc` longtext,
    `used` bool NOT NULL
)
;
CREATE TABLE `name_ballotpositionname` (
    `slug` varchar(8) NOT NULL PRIMARY KEY,
    `name` varchar(32) NOT NULL,
    `desc` longtext,
    `used` bool NOT NULL
)
;
CREATE TABLE `person_person` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `time` datetime NOT NULL,
    `name` varchar(255) NOT NULL,
    `ascii` varchar(255) NOT NULL,
    `ascii_short` varchar(32),
    `address` longtext NOT NULL
)
;
CREATE TABLE `person_alias` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `person_id` integer NOT NULL,
    `name` varchar(255) NOT NULL
)
;
ALTER TABLE `person_alias` ADD CONSTRAINT `person_id_refs_id_f129d9b` FOREIGN KEY (`person_id`) REFERENCES `person_person` (`id`);
CREATE TABLE `person_email` (
    `address` varchar(64) NOT NULL PRIMARY KEY,
    `person_id` integer NOT NULL,
    `time` datetime NOT NULL,
    `active` bool NOT NULL
)
;
ALTER TABLE `person_email` ADD CONSTRAINT `person_id_refs_id_5aac240b` FOREIGN KEY (`person_id`) REFERENCES `person_person` (`id`);
COMMIT;
