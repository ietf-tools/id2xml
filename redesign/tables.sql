BEGIN;
CREATE TABLE `doc_document` (
    `name` varchar(50) NOT NULL PRIMARY KEY,
    `type_id` integer NOT NULL,
    `title` varchar(255) NOT NULL,
    `state_id` integer NOT NULL,
    `abstract` longtext NOT NULL,
    `rev` varchar(16) NOT NULL,
    `pages` integer NOT NULL,
    `intended_status_id` integer NOT NULL,
    `replaces_id` varchar(50) NOT NULL,
    `ad_id` varchar(64) NOT NULL,
    `shepherd_id` varchar(64) NOT NULL
);
ALTER TABLE `doc_document` ADD CONSTRAINT replaces_id_refs_name_61a43889 FOREIGN KEY (`replaces_id`) REFERENCES `doc_document` (`name`);
CREATE TABLE `doc_dochistory` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `doc_id` varchar(50) NOT NULL REFERENCES `doc_document` (`name`),
    `time` datetime NOT NULL,
    `comment` longtext NOT NULL,
    `agent_id` varchar(64) NOT NULL,
    `name` varchar(50) NOT NULL,
    `type_id` integer NOT NULL,
    `title` varchar(255) NOT NULL,
    `state_id` integer NOT NULL,
    `abstract` longtext NOT NULL,
    `rev` varchar(16) NOT NULL,
    `pages` integer NOT NULL,
    `intended_status_id` integer NOT NULL,
    `replaces_id` varchar(50) NOT NULL REFERENCES `doc_document` (`name`),
    `ad_id` varchar(64) NOT NULL,
    `shepherd_id` varchar(64) NOT NULL
);
CREATE TABLE `doc_alias` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `document_id` varchar(50) NOT NULL REFERENCES `doc_document` (`name`),
    `name` varchar(64) NOT NULL
);
CREATE TABLE `doc_message` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `time` datetime NOT NULL,
    `type_id` integer NOT NULL,
    `doc_id` varchar(50) NOT NULL REFERENCES `doc_document` (`name`),
    `frm_id` varchar(64) NOT NULL,
    `subj` varchar(255) NOT NULL,
    `pos_id` integer NOT NULL,
    `text` longtext NOT NULL
);
CREATE TABLE `doc_infotag` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `document_id` varchar(50) NOT NULL REFERENCES `doc_document` (`name`),
    `infotag_id` integer NOT NULL
);
CREATE TABLE `doc_ballot` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `initiated_id` integer NOT NULL REFERENCES `doc_message` (`id`),
    `deferred_id` integer NULL REFERENCES `doc_message` (`id`),
    `last_call_id` integer NULL REFERENCES `doc_message` (`id`),
    `closed_id` integer NULL REFERENCES `doc_message` (`id`),
    `announced_id` integer NULL REFERENCES `doc_message` (`id`)
);
CREATE TABLE `doc_sendqueue` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `time` datetime NOT NULL,
    `agent_id` varchar(64) NOT NULL,
    `comment` longtext NOT NULL,
    `msg_id` integer NOT NULL REFERENCES `doc_message` (`id`),
    `to_id` varchar(64) NOT NULL,
    `send` datetime NOT NULL
);
CREATE TABLE `doc_document_authors` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `document_id` varchar(50) NOT NULL REFERENCES `doc_document` (`name`),
    `email_id` varchar(64) NOT NULL REFERENCES `person_email` (`address`),
    UNIQUE (`document_id`, `email_id`)
);
CREATE TABLE `doc_dochistory_authors` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `dochistory_id` integer NOT NULL REFERENCES `doc_dochistory` (`id`),
    `email_id` varchar(64) NOT NULL REFERENCES `person_email` (`address`),
    UNIQUE (`dochistory_id`, `email_id`)
);
CREATE TABLE `doc_sendqueue_cc` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `sendqueue_id` integer NOT NULL REFERENCES `doc_sendqueue` (`id`),
    `email_id` varchar(64) NOT NULL REFERENCES `person_email` (`address`),
    UNIQUE (`sendqueue_id`, `email_id`)
);
-- The following references should be added but depend on non-existent tables:
-- ALTER TABLE `doc_document` ADD CONSTRAINT ad_id_refs_address_27eabf35 FOREIGN KEY (`ad_id`) REFERENCES `person_email` (`address`);
-- ALTER TABLE `doc_document` ADD CONSTRAINT shepherd_id_refs_address_27eabf35 FOREIGN KEY (`shepherd_id`) REFERENCES `person_email` (`address`);
-- ALTER TABLE `doc_dochistory` ADD CONSTRAINT agent_id_refs_address_f8d4184 FOREIGN KEY (`agent_id`) REFERENCES `person_email` (`address`);
-- ALTER TABLE `doc_dochistory` ADD CONSTRAINT ad_id_refs_address_f8d4184 FOREIGN KEY (`ad_id`) REFERENCES `person_email` (`address`);
-- ALTER TABLE `doc_dochistory` ADD CONSTRAINT shepherd_id_refs_address_f8d4184 FOREIGN KEY (`shepherd_id`) REFERENCES `person_email` (`address`);
-- ALTER TABLE `doc_message` ADD CONSTRAINT frm_id_refs_address_160e7fdc FOREIGN KEY (`frm_id`) REFERENCES `person_email` (`address`);
-- ALTER TABLE `doc_sendqueue` ADD CONSTRAINT agent_id_refs_address_7360e08c FOREIGN KEY (`agent_id`) REFERENCES `person_email` (`address`);
-- ALTER TABLE `doc_sendqueue` ADD CONSTRAINT to_id_refs_address_7360e08c FOREIGN KEY (`to_id`) REFERENCES `person_email` (`address`);
-- ALTER TABLE `doc_document` ADD CONSTRAINT type_id_refs_id_5d6c69e3 FOREIGN KEY (`type_id`) REFERENCES `names_doctype` (`id`);
-- ALTER TABLE `doc_dochistory` ADD CONSTRAINT type_id_refs_id_1cb33b34 FOREIGN KEY (`type_id`) REFERENCES `names_doctype` (`id`);
-- ALTER TABLE `doc_infotag` ADD CONSTRAINT infotag_id_refs_id_1c2ad3b4 FOREIGN KEY (`infotag_id`) REFERENCES `names_docinfotag` (`id`);
-- ALTER TABLE `doc_message` ADD CONSTRAINT type_id_refs_id_73665bc1 FOREIGN KEY (`type_id`) REFERENCES `names_msgtype` (`id`);
-- ALTER TABLE `doc_message` ADD CONSTRAINT pos_id_refs_id_d46dc3e FOREIGN KEY (`pos_id`) REFERENCES `names_ballotposition` (`id`);
-- ALTER TABLE `doc_document` ADD CONSTRAINT intended_status_id_refs_id_af297e8 FOREIGN KEY (`intended_status_id`) REFERENCES `names_stdstatus` (`id`);
-- ALTER TABLE `doc_dochistory` ADD CONSTRAINT intended_status_id_refs_id_4babc697 FOREIGN KEY (`intended_status_id`) REFERENCES `names_stdstatus` (`id`);
-- ALTER TABLE `doc_document` ADD CONSTRAINT state_id_refs_id_6eeeee9 FOREIGN KEY (`state_id`) REFERENCES `names_docstate` (`id`);
-- ALTER TABLE `doc_dochistory` ADD CONSTRAINT state_id_refs_id_1c6c523a FOREIGN KEY (`state_id`) REFERENCES `names_docstate` (`id`);
CREATE TABLE `names_docinfotag` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `name` varchar(32) NOT NULL,
    `desc` longtext NOT NULL
);
CREATE TABLE `names_stdstatus` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `name` varchar(32) NOT NULL,
    `desc` longtext NOT NULL
);
CREATE TABLE `names_doctype` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `name` varchar(32) NOT NULL,
    `desc` longtext NOT NULL
);
CREATE TABLE `names_msgtype` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `name` varchar(32) NOT NULL,
    `desc` longtext NOT NULL
);
CREATE TABLE `names_docstate` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `name` varchar(32) NOT NULL,
    `desc` longtext NOT NULL
);
CREATE TABLE `names_rolename` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `name` varchar(32) NOT NULL,
    `desc` longtext NOT NULL
);
CREATE TABLE `names_ballotposition` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `name` varchar(32) NOT NULL,
    `desc` longtext NOT NULL
);
CREATE TABLE `person_person` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `given` varchar(64) NOT NULL,
    `middle` varchar(64) NOT NULL,
    `family` varchar(64) NOT NULL,
    `address` longtext NOT NULL
);
CREATE TABLE `person_email` (
    `address` varchar(64) NOT NULL PRIMARY KEY,
    `person_id` integer NOT NULL REFERENCES `person_person` (`id`),
    `time` datetime NOT NULL,
    `active` bool NOT NULL
);
CREATE TABLE `group_grouptype` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `name` varchar(32) NOT NULL
);
CREATE TABLE `group_role` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `name_id` integer NOT NULL,
    `group_id` integer NOT NULL,
    `email_id` varchar(64) NOT NULL,
    `auth` varchar(255) NOT NULL
);
CREATE TABLE `group_grouphistory` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `group_id` integer NOT NULL,
    `time` datetime NOT NULL,
    `comment` longtext NOT NULL,
    `who_id` varchar(64) NOT NULL,
    `name` varchar(64) NOT NULL,
    `acronym` varchar(16) NOT NULL,
    `status_id` integer NOT NULL,
    `type_id` integer NOT NULL REFERENCES `group_grouptype` (`id`),
    `charter_id` varchar(50) NOT NULL,
    `parent_id` integer NOT NULL,
    `list_email` varchar(64) NOT NULL,
    `list_pages` varchar(64) NOT NULL,
    `comments` longtext NOT NULL
);
CREATE TABLE `group_group` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `name` varchar(64) NOT NULL,
    `acronym` varchar(16) NOT NULL,
    `status_id` integer NOT NULL,
    `type_id` integer NOT NULL REFERENCES `group_grouptype` (`id`),
    `charter_id` varchar(50) NOT NULL,
    `parent_id` integer NOT NULL,
    `list_email` varchar(64) NOT NULL,
    `list_pages` varchar(64) NOT NULL,
    `comments` longtext NOT NULL
);
ALTER TABLE `group_role` ADD CONSTRAINT group_id_refs_id_dd2da61 FOREIGN KEY (`group_id`) REFERENCES `group_group` (`id`);
ALTER TABLE `group_grouphistory` ADD CONSTRAINT group_id_refs_id_11b8ebf4 FOREIGN KEY (`group_id`) REFERENCES `group_group` (`id`);
ALTER TABLE `group_grouphistory` ADD CONSTRAINT parent_id_refs_id_11b8ebf4 FOREIGN KEY (`parent_id`) REFERENCES `group_group` (`id`);
ALTER TABLE `group_group` ADD CONSTRAINT parent_id_refs_id_753effb9 FOREIGN KEY (`parent_id`) REFERENCES `group_group` (`id`);
CREATE TABLE `group_groupstate` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `name` varchar(32) NOT NULL
);
ALTER TABLE `group_grouphistory` ADD CONSTRAINT status_id_refs_id_7c02918e FOREIGN KEY (`status_id`) REFERENCES `group_groupstate` (`id`);
ALTER TABLE `group_group` ADD CONSTRAINT status_id_refs_id_9a8c185 FOREIGN KEY (`status_id`) REFERENCES `group_groupstate` (`id`);
CREATE TABLE `group_grouphistory_documents` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `grouphistory_id` integer NOT NULL REFERENCES `group_grouphistory` (`id`),
    `document_id` varchar(50) NOT NULL REFERENCES `doc_document` (`name`),
    UNIQUE (`grouphistory_id`, `document_id`)
);
CREATE TABLE `group_grouphistory_chairs` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `grouphistory_id` integer NOT NULL REFERENCES `group_grouphistory` (`id`),
    `email_id` varchar(64) NOT NULL REFERENCES `person_email` (`address`),
    UNIQUE (`grouphistory_id`, `email_id`)
);
CREATE TABLE `group_group_documents` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `group_id` integer NOT NULL REFERENCES `group_group` (`id`),
    `document_id` varchar(50) NOT NULL REFERENCES `doc_document` (`name`),
    UNIQUE (`group_id`, `document_id`)
);
CREATE TABLE `group_group_chairs` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `group_id` integer NOT NULL REFERENCES `group_group` (`id`),
    `email_id` varchar(64) NOT NULL REFERENCES `person_email` (`address`),
    UNIQUE (`group_id`, `email_id`)
);
-- The following references should be added but depend on non-existent tables:
-- ALTER TABLE `group_grouphistory` ADD CONSTRAINT charter_id_refs_name_695367b4 FOREIGN KEY (`charter_id`) REFERENCES `doc_document` (`name`);
-- ALTER TABLE `group_group` ADD CONSTRAINT charter_id_refs_name_362a2761 FOREIGN KEY (`charter_id`) REFERENCES `doc_document` (`name`);
-- ALTER TABLE `group_role` ADD CONSTRAINT name_id_refs_id_61ea528b FOREIGN KEY (`name_id`) REFERENCES `names_rolename` (`id`);
-- ALTER TABLE `group_role` ADD CONSTRAINT email_id_refs_address_5d4c5afb FOREIGN KEY (`email_id`) REFERENCES `person_email` (`address`);
-- ALTER TABLE `group_grouphistory` ADD CONSTRAINT who_id_refs_address_19a7c7b0 FOREIGN KEY (`who_id`) REFERENCES `person_email` (`address`);
COMMIT;
