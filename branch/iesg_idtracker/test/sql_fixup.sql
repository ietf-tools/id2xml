-- This file holds needed corrections to the database until they have been applied to
-- the live database.  This file is applied after importing a new dump of the live DB.

-- Add primary key to telchat_dates table
alter table telechat_dates add id integer primary key auto_increment;

