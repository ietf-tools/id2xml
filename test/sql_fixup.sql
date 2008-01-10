-- This file holds needed corrections to the database until they have been applied to
-- the live database.  This file is applied after importing a new dump of the live DB.

-- populate acronym table for IRTF groups
insert into acronym (acronym_id,acronym,name) values (1,'asrg','Anti-Spam Research Group');
insert into acronym (acronym_id,acronym,name) values (2,'cfrgrg','Crypto Forum Research Group');
insert into acronym (acronym_id,acronym,name) values (3,'dtnrg','Delay-Tolerant Networking Research Group');
insert into acronym (acronym_id,acronym,name) values (4,'e2erg','End-to-End Research Group Charter');
insert into acronym (acronym_id,acronym,name) values (5,'gsec','Group Security');
insert into acronym (acronym_id,acronym,name) values (6,'hiprg','Host Identity Protocol');
insert into acronym (acronym_id,acronym,name) values (7,'imrg','Internet Measurement Research Group');
insert into acronym (acronym_id,acronym,name) values (8,'mobopts','IP Mobility Optimizations Research Group');
insert into acronym (acronym_id,acronym,name) values (9,'nmrg','Network Management Research Group');
insert into acronym (acronym_id,acronym,name) values (10,'p2prg','Peer-to-Peer Research Group');
insert into acronym (acronym_id,acronym,name) values (11,'rrg','Routing Research Group');
insert into acronym (acronym_id,acronym,name) values (12,'samrg','Scalable Adaptive Multicast Research Group');
insert into acronym (acronym_id,acronym,name) values (13,'iccrg','Internet Congestion Control Research Group');
insert into acronym (acronym_id,acronym,name) values (14,'eme','End Middle End Research Group');
insert into acronym (acronym_id,acronym,name) values (15,'end2end','End-to-End Research Group');
insert into acronym (acronym_id,acronym,name) values (16,'tmrg','Transport Modeling Research Group');

-- create new group type, 'RG'
insert into g_type (group_type_id,group_type) values (6,'RG');

-- populate groups_ietf (IETFWG) with IRTF groups
insert into groups_ietf (group_acronym_id,group_type_id,status_id,comments)
values (1,6,1,'IRTF');
insert into groups_ietf (group_acronym_id,group_type_id,status_id,comments)
values (2,6,1,'IRTF');
insert into groups_ietf (group_acronym_id,group_type_id,status_id,comments)
values (3,6,1,'IRTF');
insert into groups_ietf (group_acronym_id,group_type_id,status_id,comments)
values (4,6,1,'IRTF');
insert into groups_ietf (group_acronym_id,group_type_id,status_id,comments)
values (5,6,1,'IRTF');
insert into groups_ietf (group_acronym_id,group_type_id,status_id,comments)
values (6,6,1,'IRTF');
insert into groups_ietf (group_acronym_id,group_type_id,status_id,comments)
values (7,6,1,'IRTF');
insert into groups_ietf (group_acronym_id,group_type_id,status_id,comments)
values (8,6,1,'IRTF');
insert into groups_ietf (group_acronym_id,group_type_id,status_id,comments)
values (9,6,1,'IRTF');
insert into groups_ietf (group_acronym_id,group_type_id,status_id,comments)
values (10,6,1,'IRTF');
insert into groups_ietf (group_acronym_id,group_type_id,status_id,comments)
values (11,6,1,'IRTF');
insert into groups_ietf (group_acronym_id,group_type_id,status_id,comments)
values (12,6,1,'IRTF');
insert into groups_ietf (group_acronym_id,group_type_id,status_id,comments)
values (13,6,1,'IRTF');
insert into groups_ietf (group_acronym_id,group_type_id,status_id,comments)
values (14,6,1,'IRTF');
insert into groups_ietf (group_acronym_id,group_type_id,status_id,comments)
values (15,6,1,'IRTF');
insert into groups_ietf (group_acronym_id,group_type_id,status_id,comments)
values (16,6,1,'IRTF');

-- create new acronym 'IRTF'
insert into acronym (acronym,name) values ('IRTF','IRTF');

-- add IRTF into area table as not active area
insert into areas (area_acronym_id,status_id,comments) values (1731,4,'IRTF');

-- assign each IRTF groups to IRTF area
insert into area_group (area_acronym_id,group_acronym_id) values (1731,1);
insert into area_group (area_acronym_id,group_acronym_id) values (1731,2);
insert into area_group (area_acronym_id,group_acronym_id) values (1731,3);
insert into area_group (area_acronym_id,group_acronym_id) values (1731,4);
insert into area_group (area_acronym_id,group_acronym_id) values (1731,5);
insert into area_group (area_acronym_id,group_acronym_id) values (1731,6);
insert into area_group (area_acronym_id,group_acronym_id) values (1731,7);
insert into area_group (area_acronym_id,group_acronym_id) values (1731,8);
insert into area_group (area_acronym_id,group_acronym_id) values (1731,9);
insert into area_group (area_acronym_id,group_acronym_id) values (1731,11);
insert into area_group (area_acronym_id,group_acronym_id) values (1731,12);
insert into area_group (area_acronym_id,group_acronym_id) values (1731,13);
insert into area_group (area_acronym_id,group_acronym_id) values (1731,14);
insert into area_group (area_acronym_id,group_acronym_id) values (1731,15);
insert into area_group (area_acronym_id,group_acronym_id) values (1731,16);
insert into area_group (area_acronym_id,group_acronym_id) values (1731,10);

-- populate g_chairs (WGChair) with IRTF chairs
insert into g_chairs (person_or_org_tag,group_acronym_id) values (6,105728);
insert into g_chairs (person_or_org_tag,group_acronym_id) values (6,107003);
insert into g_chairs (person_or_org_tag,group_acronym_id) values (1,11928);
insert into g_chairs (person_or_org_tag,group_acronym_id) values (8,101214);
insert into g_chairs (person_or_org_tag,group_acronym_id) values (8,10087);
insert into g_chairs (person_or_org_tag,group_acronym_id) values (10,107447);
insert into g_chairs (person_or_org_tag,group_acronym_id) values (3,19177);
insert into g_chairs (person_or_org_tag,group_acronym_id) values (3,3354);
insert into g_chairs (person_or_org_tag,group_acronym_id) values (9,21106);
insert into g_chairs (person_or_org_tag,group_acronym_id) values (12,107438);
insert into g_chairs (person_or_org_tag,group_acronym_id) values (12,107595);
insert into g_chairs (person_or_org_tag,group_acronym_id) values (11,4475);
insert into g_chairs (person_or_org_tag,group_acronym_id) values (11,567);
insert into g_chairs (person_or_org_tag,group_acronym_id) values (13,106659);
insert into g_chairs (person_or_org_tag,group_acronym_id) values (13,103877);
insert into g_chairs (person_or_org_tag,group_acronym_id) values (14,107964);

