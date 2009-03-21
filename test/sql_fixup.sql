-- This file holds needed corrections to the database until they have been applied to
-- the live database.  This file is applied after importing a new dump of the live DB.

ALTER TABLE ietfauth_usermap ADD rfced_htdigest VARCHAR(32);


