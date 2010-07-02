-- This file holds needed corrections to the database until they have been applied to
-- the live database.  This file is applied after importing a new dump of the live DB.

-- adding submission cut off time
alter table id_submission_env add cut_off_time time;
alter table id_submission_env add cut_off_warn_days integer;
update id_submission_env set cut_off_time='17:00:00';
update id_submission_env set cut_off_warn_days=14;

-- making author_order mandatory
alter table id_authors change author_order author_order int( 11 ) not null;

-- fixing email_address rows created by old idst, which
-- creates rows without a type.
update email_addresses set email_type='INET' where email_type='';
-- and other variation from old idst: type='Primary' in a 4 letter field.
update email_addresses set email_type='INET' where email_type='Prim';

