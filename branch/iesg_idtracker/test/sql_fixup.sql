-- This file holds needed corrections to the database until they have been applied to
-- the live database.  This file is applied after importing a new dump of the live DB.

-- new table idtracker_comments to store all comments used by the I-D Tracker
create table idtracker_comments (

);

-- Add primary key to telchat_dates table
alter table telechat_dates add id integer primary key auto_increment;

