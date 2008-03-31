-- This file holds needed corrections to the database until they have been applied to
-- the live database.  This file is applied after importing a new dump of the live DB.

-- adding submission cut off time
alter table id_submission_env add cut_off_time integer;

