BEGIN;
CREATE TABLE `interim_meetings` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `group_acronym_id` integer NOT NULL,
    `meeting_date` date NOT NULL,
    `created` date NOT NULL,
    `updated` date NOT NULL
)
;
CREATE TABLE `interim_files` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `meeting_id` integer NOT NULL,
    `file_type_id` integer NOT NULL,
    `title` varchar(255) NOT NULL,
    `file` varchar(100) NOT NULL,
    `order_num` integer,
    `slide_num` integer
)
;
ALTER TABLE `interim_files` ADD CONSTRAINT `meeting_id_refs_id_a7407a31` FOREIGN KEY (`meeting_id`) REFERENCES `interim_meetings` (`id`);
