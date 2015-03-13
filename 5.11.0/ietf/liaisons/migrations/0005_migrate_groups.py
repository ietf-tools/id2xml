# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def create_new_groups(apps, schema_editor):
    Group = apps.get_model("group","Group")
    for group in NEW_GROUPS:
        if group[2]:
            print "Get parent: {}".format(group[2])
            parent = Group.objects.get(acronym=group[2])
        else:
            parent = None
        Group.objects.create(
            acronym=group[0],
            name=group[1],
            parent=parent,
            type_id='sdo',
            state_id=group[3])

def change_acronyms(apps, schema_editor):
    '''Modify some existing groups'''
    Group = apps.get_model("group","Group")
    for old,new in CHANGE_ACRONYM:
        group = Group.objects.get(acronym=old)
        group.acronym = new
        group.save()

def set_parents(apps, schema_editor):
    '''Modify some existing groups'''
    Group = apps.get_model("group","Group")
    for child_acronym,parent_acronym in SET_PARENT:
        print "Setting parent {}:{}".format(child_acronym,parent_acronym)
        child = Group.objects.get(acronym=child_acronym)
        parent = Group.objects.get(acronym=parent_acronym)
        child.parent = parent
        child.save()

def reassign_groups(apps,schema_editor):
    '''For Statements that have a multi to_group assignment, remove the group
    assignment and populate the to_name field for conversion to multiple groups
    in later function'''
    LiaisonStatement = apps.get_model("liaisons", "LiaisonStatement")
    for acronym,name in MULTI_TO_GROUPS:
        for stmt in LiaisonStatement.objects.filter(to_group__acronym=acronym):
            stmt.to_name=name
            stmt.to_group=None
            stmt.save()

def cleanup_groups(apps, schema_editor):
    Group = apps.get_model("group","Group")
    for group,x in MULTI_TO_GROUPS:
        Group.objects.get(acronym=group).delete()

def copy_to_group(apps, schema_editor):
    LiaisonStatement = apps.get_model("liaisons", "LiaisonStatement")
    Group = apps.get_model("group","Group")
    for s in LiaisonStatement.objects.all():
        if s.to_group:
            s.to_groups.add(s.to_group)
        elif s.to_name:
            if s.to_name in TO_NAME_MAPPING:
                if TO_NAME_MAPPING[s.to_name]:
                    for acronym in TO_NAME_MAPPING[s.to_name]:
                        try:
                            s.to_groups.add(Group.objects.get(acronym=acronym))
                        except Group.DoesNotExist:
                            print "Group Does Not Exist: {}".format(acronym)
                    s.to_name = ''
                    s.save()
                else:
                    print "{} empty to_group mapping"
            else:
                print "{} not in mapping".format(s.to_name)

def copy_from_group(apps, schema_editor):
    LiaisonStatement = apps.get_model("liaisons", "LiaisonStatement")
    Group = apps.get_model("group","Group")
    for s in LiaisonStatement.objects.all():
        if s.from_group:
            s.from_groups.add(s.from_group)
        elif s.from_name:
            if s.from_name in FROM_NAME_MAPPING:
                if FROM_NAME_MAPPING[s.from_name]:
                    for acronym in FROM_NAME_MAPPING[s.from_name]:
                        try:
                            s.from_groups.add(Group.objects.get(acronym=acronym))
                        except Group.DoesNotExist:
                            print "Group Does Not Exist: {}".format(acronym)
                    s.from_name = ''
                    s.save()
                else:
                    print "{} empty from_group mapping"
            else:
                print "{} not in mapping".format(s.to_name)


class Migration(migrations.Migration):

    dependencies = [
        ('liaisons', '0004_migrate_attachments'),
    ]

    operations = [
        migrations.RunPython(change_acronyms),
        migrations.RunPython(create_new_groups),
        migrations.RunPython(set_parents),
        migrations.RunPython(reassign_groups),
        migrations.RunPython(copy_to_group),
        migrations.RunPython(copy_from_group),
        migrations.RunPython(cleanup_groups),
    ]

# ----------------------------------------------------------
# x_name to group mappings
# -----------------------------------------------------------
NEW_GROUPS = [
    ('3gpp-tsg-sa2','3GPP-TSG-SA2','3gpp','active'),
    ('3gpp-tsg-ct4','3GPP-TSG-CT4','3gpp','active'),
    ('3gpp-tsg-ran2','3GPP-TSG-ran2','3gpp','active'),
    ('itu','ITU',None,'active'),
    ('itu-r-wp5a','ITU-R-WP5A','itu-r','active'),
    ('itu-r-wp5d','ITU-R-WP5D','itu-r','active'),
    ('itu-r-wp8a','ITU-R-WP8A','itu-r','active'),
    ('itu-r-wp8f','ITU-R-WP8F','itu-r','active'),
    ('itu-t-ipv6-group','ITU-T-IPV6-GROUP','itu-t','active'),
    ('itu-t-fg-cloud','ITU-T-FG-CLOUD','itu-t','conclude'),
    ('itu-t-fg-iptv','ITU-T-FG-IPTV','itu-t','conclude'),
    ('itu-t-fg-ngnm','ITU-T-FG-NGNM','itu-t','conclude'),
    ('itu-t-jca-idm','ITU-T-JCA-IDM','itu-t','active'),
    ('itu-t-sg-4','ITU-T-SG-4','itu-t','conclude'),
    ('itu-t-sg-6','ITU-T-SG-6','itu-t','conclude'),
    ('itu-t-sg-7','ITU-T-SG-7','itu-t','conclude'),
    ('itu-t-sg-8','ITU-T-SG-8','itu-t','conclude'),
    ('itu-t-sg-9','ITU-T-SG-9','itu-t','active'),
    ('itu-t-sg-2-q1','ITU-T-SG-2-Q1','itu-t-sg-2','active'),
    ('itu-t-sg-11-q5','ITU-T-SG-11-Q5','itu-t-sg-11','active'),
    ('itu-t-sg-11-wp2','ITU-T-SG-11-WP2','itu-t-sg-11','active'),
    ('itu-t-sg-12-q12','ITU-T-SG-12-Q12','itu-t-sg-12','active'),
    ('itu-t-sg-12-q17','ITU-T-SG-12-Q17','itu-t-sg-12','active'),
    ('itu-t-sg-13-q3','ITU-T-SG-13-Q3','itu-t-sg-13','active'),
    ('itu-t-sg-13-q5','ITU-T-SG-13-Q5','itu-t-sg-13','active'),
    ('itu-t-sg-13-q7','ITU-T-SG-13-Q7','itu-t-sg-13','active'),
    ('itu-t-sg-13-q9','ITU-T-SG-13-Q9','itu-t-sg-13','active'),
    ('itu-t-sg-13-q11','ITU-T-SG-13-Q11','itu-t-sg-13','active'),
    ('itu-t-sg-13-wp3','ITU-T-SG-13-WP3','itu-t-sg-13','conclude'),
    ('itu-t-sg-13-wp4','ITU-T-SG-13-WP4','itu-t-sg-13','conclude'),
    ('itu-t-sg-13-wp5','ITU-T-SG-13-WP5','itu-t-sg-13','conclude'),
    ('itu-t-sg-14','ITU-T-SG-14','itu-t','active'),
    ('itu-t-sg-15-q1','ITU-T-SG-15-Q1','itu-t-sg-15','active'),
    ('itu-t-sg-15-q3','ITU-T-SG-15-Q3','itu-t-sg-15','active'),
    ('itu-t-sg-15-q4','ITU-T-SG-15-Q4','itu-t-sg-15','active'),
    ('itu-t-sg-15-q6','ITU-T-SG-15-Q6','itu-t-sg-15','active'),
    ('itu-t-sg-15-q9','ITU-T-SG-15-Q9','itu-t-sg-15','active'),
    ('itu-t-sg-15-q10','ITU-T-SG-15-Q10','itu-t-sg-15','active'),
    ('itu-t-sg-15-q11','ITU-T-SG-15-Q11','itu-t-sg-15','active'),
    ('itu-t-sg-15-q12','ITU-T-SG-15-Q12','itu-t-sg-15','active'),
    ('itu-t-sg-15-q14','ITU-T-SG-15-Q14','itu-t-sg-15','active'),
    ('itu-t-sg-15-q15','ITU-T-SG-15-Q15','itu-t-sg-15','active'),
    ('itu-t-sg-15-wp1','ITU-T-SG-15-WP1','itu-t-sg-15','active'),
    ('itu-t-sg-15-wp3','ITU-T-SG-15-WP3','itu-t-sg-15','active'),
    ('itu-t-sg-16-q8','ITU-T-SG-16-Q8','itu-t-sg-16','active'),
    ('itu-t-sg-16-q9','ITU-T-SG-16-Q9','itu-t-sg-16','active'),
    ('itu-t-sg-16-q10','ITU-T-SG-16-Q10','itu-t-sg-16','active'),
    ('itu-t-sg-17-q2','ITU-T-SG-17-Q2','itu-t-sg-17','active'),
    ('itu-t-sg-17-q4','ITU-T-SG-17-Q4','itu-t-sg-17','active'),
    ('ieee','IEEE',None,'active'),
    ('ieee-802','IEEE 802','ieee','active'),
    ('ieee-802-ec','IEEE 802 Executive Committee','ieee','active'),
    ('ieee-802-21','IEEE 802.21','ieee-802','active'),
    ('iso-iec-jtc1','ISO/IEC JTC1',None,'active'),
    ('iso-iec-jtc1-sc29-wg1','ISO/IEC JTC1 SC29 WG1','iso-iec-jtc1-sc29','active'),
    ('iso-iec-jtc1-sc31','ISO/IEC JTC1 SC31','iso-iec-jtc1','active'),
    ('iso-iec-jtc1-sc31-wg4','ISO/IEC JTC1 SC31 WG4','iso-iec-jtc1-sc31','active'),
    ('iso-iec-jtc1-sgsn','ISO/IEC JTC1 SGSN','iso-iec-jtc1','active'),
    ('iso-iec-jtc1-wg7','ISO/IEC JTC1 WG7','iso-iec-jtc1','active'),
]

CHANGE_ACRONYM = [
    ('ieee-8021','ieee-802-1'),
    ('ieee-8023','ieee-802-3'),
    ('ieee-80211','ieee-802-11'),
    ('ieee-80216','ieee-802-16'),
    ('ieee-80223','ieee-802-23'),
    ('isoiec-jtc1-sc2','iso-iec-jtc1-sc2'),
    ('isoiec-jtc1-sc6','iso-iec-jtc1-sc6'),
    ('isoiec-jtc1-sc29','iso-iec-jtc1-sc29'),
    ('isoiec-jtc-1sc-29wg-11','iso-iec-jtc1-sc29-wg11'),
    ('itu-t-fgd','itu-t-fg-dist'),
    ('3GPP-TSG-SA-WG4','3gpp-tsg-sa4'),
]
    
SET_PARENT = [
    ('itu-t','itu'),
    ('itu-r','itu'),
    ('itu-t-jca-cloud','itu-t'),
    ('itu-t-jca-cop','itu-t'),
    ('itu-t-jca-sdn','itu-t'),
    ('itu-t-mpls','itu-t'),
    ('itu-t-sg-2','itu-t'),
    ('itu-t-sg-3','itu-t'),
    ('itu-t-sg-11','itu-t'),
    ('itu-t-sg-12','itu-t'),
    ('itu-t-sg-13','itu-t'),
    ('itu-t-sg-15','itu-t'),
    ('itu-t-sg-16','itu-t'),
    ('itu-t-sg-17','itu-t'),
    ('itu-t-tsag','itu-t'),
    ('ieee-sa','ieee'),
    ('ieee-802-1','ieee-802'),
    ('ieee-802-3','ieee-802'),
    ('ieee-802-11','ieee-802'),
    ('ieee-802-16','ieee-802'),
    ('ieee-802-23','ieee-802'),
    ('iso-iec-jtc1-sc2','iso-iec-jtc1'),
    ('iso-iec-jtc1-sc6','iso-iec-jtc1'),
    ('iso-iec-jtc1-sc7','iso-iec-jtc1'),
    ('iso-iec-jtc1-sc27','iso-iec-jtc1'),
    ('iso-iec-jtc1-sc29','iso-iec-jtc1'),
    ('iso-iec-jtc1-sc29-wg11','iso-iec-jtc1-sc29'),
]

MULTI_TO_GROUPS = [
    ('itu-t-sg15-q9-q10-q12-and-q14','ITU-T SG 15 Q9, Q10, Q12 and Q14'),
    ('itu-t-sg12-q-12-17','ITU-T SG 12, Q12, Q17'),
]

TO_NAME_MAPPING = {
    u'': None,
    u'(bwijnen@lucent.com) Bert Wijnen': [u'sming'],
    u'(lyong@ciena.com)Lyndon Ong': [u'itu-t-sg-15'],
    u'(sob@harvard.edu) Scott Bradner': None,
    u'(sob@harvard.edu)Scott Bradner': None,
    u'3GPP SA WG4': [u'3gpp-tsg-sa4'],
    u'3GPP SA2': [u'3gpp-tsg-sa2'],
    u'3GPP TSG CT WG4': [u'3gpp-tsg-ct4'],
    u'3GPP TSG RAN WG2': [u'3gpp-tsg-ran2'],
    u'3GPP TSG SA WG4': [u'3gpp-tsg-sa4'],
    u'3GPP, 3GPP2, ARIB, ATIS, CCSA, ETSI, ETSI-DECT, ETSI-BRAN, IEEE, IETF,': None,
    u'3GPP/IETF and 3GPP/ITU-T Co-ordinator': None,
    u'ACIF, ARIB, ATIS, CCSA, ETSI, IEEE, IETF, ISACC, TIA, TTA, TTC': None,
    u'ASON-related Work': None,
    u'ATIS': None,
    u'BBF': None,
    u'BMWG': [u'bmwg'],
    u'Bert Wijnen and the IETF O & M Area': [u'ops'],
    u'Bert Wijnen, Bernard Aboba and the IETF': [u'ietf'],
    u'CCAMP WG co-chairs and IEEE-IETF': None,
    u'CCAMP WG co-chairs and IEEE-IETF liaisons': None,
    u'Completes action above Scott Bradner, Area co-Director (sob@harvard.edu)': ['tsv'],
    u'DLNA': None,
    u'DONE': None,
    u'DSL Forum': None,
    u'DSL Forum Architecture & Transport Working Group': None,
    u'DVB IPI': None,
    u'DVB TM-IPI, ETSI TISPAN, ATIS IIF, IETF RMT, IETF FECFRAME': None,
    u'EAP Method Update Working Group': None,
    u'ETSI AT working group Digital': None,
    u'ETSI TC HF': None,
    u'ETSI TISPAN': None,
    u'G.7712 Editor, ITU-T SG15Q14 Rapporteur, ITU-T SG15': None,
    u'Generic EAP Encapsulation': None,
    u'Harald Alvestrand': None,
    u'IAB and IETF Routing Area Directors': [u'iab', 'rtg'],
    u'IAB, IESG': [u'iab', 'iesg'],
    u'IANA': [u'iana'],
    u'ICANN, IETF/IAB, NRO and ACSIS': None,
    u'IEEE 802': [u'ieee-802'],
    u'IEEE NGSON Study Group': None,
    u'IEEE802.1': [u'ieee-802-1'],
    u'IESG members, IAB members': [u'iesg', u'iab'],
    u'IESG, IETF-RAI': [u'iesg', u'rai'],
    u'IESG/IAB Chair': [u'iesg', u'iab'],
    u'IETF  PWE3 and TICTOC': [u'pwe3', u'tictoc'],
    u'IETF (CCAMP, PCE and MPLS WGs)': [u'ccamp', u'pce', u'mpls'],
    u'IETF (Management)': None,
    u'IETF (SAVI and V6OPS WGS, OPS Area and INT Area)': [u'savi', u'v6ops', u'ops', u'int'],
    u'IETF (Sub-IP & Transport Areas)': [u'sub', u'tsv'],
    u'IETF (and others)': [u'ietf'],
    u'IETF (ccamp, pce and mpls WGs)': [u'ccamp', u'pce', u'mpls'],
    u'IETF 6MAN WG, IETF Internet Area': [u'6man', u'int'],
    u'IETF AVT WG, ITU-T SG11': [u'avt', u'itu-t-sg-11'],
    u'IETF CCAMP WG, Routing Area Directors': [u'ccamp', u'rtg'],
    u'IETF CCAMP and MPLS WGs': [u'ccamp', u'mpls'],
    u'IETF CCAMP and MPLS WGs and the Routing Area Directors of the IETF': [u'ccamp', u'mpls', u'rtg'],
    u'IETF CCAMP and PCE WGs': [u'ccamp', u'pce'],
    u'IETF CCAMP, IETF Routing Area Directors': [u'ccamp', u'rtg'],
    u'IETF CCAMP, PCE and MPLS WGs': [u'ccamp', u'pce', u'mpls'],
    u'IETF Charter group on Authority to Citizen Alert (ATOCA)': [u'atoca'],
    u'IETF DNSOP WG, SAAG, IAB': [u'dnsop', u'saag', u'iab'],
    u'IETF IAB, IETF IESG': [u'iab', u'ietf', u'iesg'],
    u'IETF IESG, IAB, PWE3 WG, MPLS WG, routing and internet Area Directors': [u'iesg', u'iab', u'pwe3', u'mpls', u'rtg', u'int'],
    u'IETF IPPM, IETF AVT': [u'ippm', u'avt'],
    u'IETF Internet Area; IETF MIF WG; IETF v6ops WG; IETF 6man WG; IETF softwire WG;  IETF Operations and Management Area': [u'int', u'mif', u'v6ops', u'6man', u'softwire', u'ops'],
    u'IETF Liaison to the ITU on MPLS and PWE3 WG Co-Chair': [u'itu-t-mpls', u'pwe3'],
    u'IETF MEAD Team': None,
    u'IETF MEAD team': None,
    u'IETF MEXT WG': ['mext'],
    u'IETF MIPSHOP-WG': [u'mipshop'],
    u'IETF MPLS & PWE3': [u'mpls', u'pwe3'],
    u'IETF MPLS WG, CC: IETF CCAMP and PWE3  WGs': [u'mpls', u'ccamp', u'pwe3'],
    u'IETF MPLS WG, CC: MFA Forum': None,
    u'IETF MPLS WG, IAB, IESG': [u'mpls', u'iab', u'iesg'],
    u'IETF MPLS WG, IETF IAB and IESG': [u'mpls', u'iab', u'iesg'],
    u'IETF MPLS WG, IETF PWE3 WG, Broadband Forum': [u'mpls', u'pwe3', u'broadband-forum'],
    u'IETF MPLS and GMPLS': None,
    u'IETF MPLS and PWE3 WG, MFA Forum, ITU-T Q7/13': None,
    u'IETF MPLS liaison representative': [u'mpls'],
    u'IETF MPLS, CCAMP and PWE3  WGs': [u'mpls', u'ccamp', u'pwe3'],
    u'IETF MPLS, CCAMP, PWE3 and L2VPN': [u'mpls', u'ccamp', u'pwe3', u'l2vpn'],
    u'IETF MPLS, PWE WGs (Info: IETF MEAD team)': None,
    u'IETF Mead Team': None,
    u'IETF NSIS WG Chairs, IETF TSV Area Directors, IESG members, IAB members': [u'nsis', u'tsv', u'iesg', u'iab'],
    u'IETF PWE3 and L2VPN': [u'pwe3', u'l2vpn'],
    u'IETF PWE3 and L2VPN Working Groups': [u'pwe3', u'l2vpn'],
    u'IETF PWE3 and MPLS WGs': [u'pwe3', u'mpls'],
    u'IETF PWE3 and MPLS Working Groups': [u'pwe3', u'mpls'],
    u'IETF PWE3, MPLS working groups': [u'pwe3', u'mpls'],
    u'IETF RAI and IESG': [u'rai', 'iesg'],
    u'IETF Real-time Applications and Infrastructure Area Director': [u'rai'],
    u'IETF Routing Area, the MPLS and CCAMP working groups': [u'rtg', u'mpls', u'ccamp'],
    u'IETF Routing and Transport areas': [u'rtg', u'tsv'],
    u'IETF SIP related Working Groups and IESG': None,
    u'IETF Transport and Internat Areas': [u'tsv', u'int'],
    u'IETF WG MPLS': [u'mpls'],
    u'IETF Working Groups IEPREP, TSV, NSIS': [u'ieprep', u'tsv', u'nsis'],
    u'IETF and Harald Alvestrand': None,
    u'IETF and IAB': [u'ietf', u'iab'],
    u'IETF pwe3, mpls WGs': [u'pwe3', u'mpls'],
    u'IETF re RoHC': [u'rohc'],
    u'IETF \u2013 Internet Area Directors, Internet Area Working Groups': [u'int'],
    u'IETF, IAB': [u'ietf', u'iab'],
    u'IETF/IAB': [u'ietf', u'iab'],
    u'IETF/IAB, NRO, ICANN and ACSIS': None,
    u'IETF/IAB/IESG': [u'ietf', u'iab', u'iesg'],
    u'IETF/PWE3 and L2VPN WGs': [u'pwe3', u'l2vpn'],
    u'ISIS': [u'isis'],
    u'ISMA': None,
    u'ISO/IEC JTC': [u'iso-iec-jtc1'],
    u'ISO/IEC JTC 1/SC 29/WG 1': [u'iso-iec-jtc1-sc29-wg1'],
    u'ISOC': [u'isoc'],
    u'ISOC/IAB Liaison': [u'isoc', 'iab'],
    u'ITU': [u'itu'],
    u'ITU IPv6 Group': [u'itu-t-ipv6-group'],
    u'ITU Q12/15 and Q14/15': [u'itu-t-sg-15-q12',u'itu-t-sg-15-q14'],
    u'ITU SG 16 Q8, 9, 10/16': [u'itu-t-sg-16-q8',u'itu-t-sg-16-q9',u'itu-t-sg-16-q10'],
    u'ITU SG13': [u'itu-t-sg-13'],
    u'ITU SG15': [u'itu-t-sg-15'],
    u'ITU-R': [u'itu-r'],
    u'ITU-R WP8F & IETF': [u'itu-r-wp8f',u'ietf'],
    u'ITU-SG15': [u'itu-t-sg-15'],
    u'ITU-SG2': [u'itu-t-sg-2'],
    u'ITU-T JCA-IdM': [u'itu-t-jca-idm'],
    u'ITU-T Q1/SG15': [u'itu-t-sg-15-q1'],
    u'ITU-T Q10/15': [u'itu-t-sg-15-q10'],
    u'ITU-T Q12/15 and Q14/15': [u'itu-t-sg-15-q12',u'itu-t-sg-15-q14'],
    u'ITU-T Q14/15': [u'itu-t-sg-15-q14'],
    u'ITU-T Q14/15 - Mr. Kam Lam, Rapporteur': [u'itu-t-sg-15-q14'],
    u'ITU-T Q14/15, ITU-T Q11/15': [u'itu-t-sg-15-q11',u'itu-t-sg-15-q14'],
    u'ITU-T Q3/15': [u'itu-t-sg-15-q3'],
    u'ITU-T Q5/13 (recently renamed ITU-T Q7/13)': [u'itu-t-sg-13-q7'],
    u'ITU-T Q7/SG13': [u'itu-t-sg-13-q7'],
    u'ITU-T Question 14/15': [u'itu-t-sg-15-q14'],
    u'ITU-T Question 3/15': [u'itu-t-sg-15-q3'],
    u'ITU-T SG 11 and ITU-T TSAG': [u'itu-t-sg-11',u'itu-t-tsag'],
    u'ITU-T SG 11, ITU-T Q.5/11, ITU-T WP 2/11': [u'itu-t-sg-11',u'itu-t-sg-11-q5',u'itu-t-sg-11-wp2'],
    u'ITU-T SG 12, Q12, Q17': [u'itu-t-sg12-q-12-17'],
    u'ITU-T SG 13 (ITU-T SG 11 and SG 12 for information)': [u'itu-t-sg-13',u'itu-t-sg-12',u'itu-t-sg-12'],
    u'ITU-T SG 13 (ITU-T SG 11 for information)': [u'itu-t-sg-13',u'itu-t-sg-11'],
    u'ITU-T SG 13, SG 15': [u'itu-t-sg-13', u'itu-t-sg-15'],
    u'ITU-T SG 15 <tsbsg15@itu.int, greg.jones@itu.int>': [u'itu-t-sg-15'],
    u'ITU-T SG 15 Q9, Q10, Q12 and Q14': [u'itu-t-sg-15-q9',u'itu-t-sg-15-q10',u'itu-t-sg-15-q12',u'itu-t-sg-15-q14'],
    u'ITU-T SG 15, Q.14/15': [u'itu-t-sg-15-q14'],
    u'ITU-T SG 15, Q9, Q11, Q12, Q14': [u'itu-t-sg-15-q9',u'itu-t-sg-15-q10',u'itu-t-sg-15-q12',u'itu-t-sg-15-q14'],
    u'ITU-T SG 17 Q.2/17': [u'itu-t-sg-17-q2'],
    u'ITU-T SG 4': [u'itu-t-sg-4'],
    u'ITU-T SG 4, 9, 11, 13, 16 and IETF': [u'itu-t-sg-4',u'itu-t-sg-9',u'itu-t-sg-11',u'itu-t-sg-13',u'itu-t-sg-16',u'ietf'],
    u'ITU-T SG-15': [u'itu-t-sg-15'],
    u'ITU-T SG-2': [u'itu-t-sg-2'],
    u'ITU-T SG11': [u'itu-t-sg-11'],
    u'ITU-T SG12, SG13, ATIS, TIA, IEC, IETF ccamp WG, IEEE 802.1, 802.3, OIF, Metro Ethernet Forum, ATM Forum': None,
    u'ITU-T SG13': [u'itu-t-sg-13'],
    u'ITU-T SG13 and SG15': [u'itu-t-sg-13', u'itu-t-sg-15'],
    u'ITU-T SG15': [u'itu-t-sg-15'],
    u'ITU-T SG15 (Optical Control Plane)': [u'itu-t-sg-15'],
    u'ITU-T SG15 Q10': [u'itu-t-sg-15-q10'],
    u'ITU-T SG15 Q10, Q12': [u'itu-t-sg-15-q10',u'itu-t-sg-15-q12'],
    u'ITU-T SG15 Q12': [u'itu-t-sg-15-q12'],
    u'ITU-T SG15 Q14': [u'itu-t-sg-15-q14'],
    u'ITU-T SG15 Q6': [u'itu-t-sg-15-q6'],
    u'ITU-T SG15 Q9, Q10, Q12 and Q14': [u'itu-t-sg-15-q9',u'itu-t-sg-15-q10',u'itu-t-sg-15-q12',u'itu-t-sg-15-q14'],
    u'ITU-T SG15 Q9, Q11, Q12 and Q14': [u'itu-t-sg-15-q9',u'itu-t-sg-15-q11',u'itu-t-sg-15-q12',u'itu-t-sg-15-q14'],
    u'ITU-T SG15 Question 12': [u'itu-t-sg-15-q12'],
    u'ITU-T SG15 Question 3': [u'itu-t-sg-15-q3'],
    u'ITU-T SG15 Question 6': [u'itu-t-sg-15-q6'],
    u'ITU-T SG15 Question 6, Question 12, and Question 14': [u'itu-t-sg-15-q6',u'itu-t-sg-15-q12',u'itu-t-sg-15-q14'],
    u'ITU-T SG15 Question 9': [u'itu-t-sg-15-q9'],
    u'ITU-T SG15 Questions 12 and 14': [u'itu-t-sg-15-q12',u'itu-t-sg-15-q14'],
    u'ITU-T SG15 and Q14/15': [u'itu-t-sg-15-q14'],
    u'ITU-T SG15, Q 9/15, Q 10/15, Q 12/15 and Q 14/15': [u'itu-t-sg-15-q9',u'itu-t-sg-15-q10',u'itu-t-sg-15-q12',u'itu-t-sg-15-q14'],
    u'ITU-T SG15, Q 9/15, Q10/15, Q12/15 and Q14/15': [u'itu-t-sg-15-q9',u'itu-t-sg-15-q10',u'itu-t-sg-15-q12',u'itu-t-sg-15-q14'],
    u'ITU-T SG15, Q9, Q11, Q12 and Q14': [u'itu-t-sg-15-q9',u'itu-t-sg-15-q11',u'itu-t-sg-15-q12',u'itu-t-sg-15-q14'],
    u'ITU-T SG16': [u'itu-t-sg-16'],
    u'ITU-T SG17': [u'itu-t-sg-17'],
    u'ITU-T SG2': [u'itu-t-sg-2'],
    u'ITU-T SG2 <tsbsg2@itu.int>': [u'itu-t-sg-2'],
    u'ITU-T SG2 Q 1/2': [u'itu-t-sg-2-q1'],
    u'ITU-T SG4': [u'itu-t-sg-4'],
    u'ITU-T SG4, ITU-T SG15, ITU-T NGNM Focus group, 3GPP SA5, 3GPP2, ATIS/TMOC, TMF, IETF Management, ETSI BRAN': None,
    u'ITU-T SGs, ITU-R WGs, ITU-D SG2 and the IETF': None,
    u'ITU-T SGs: 2 (info), 4, 9, 11, 12, 13, 17, 19; ITU-R SGs: 1, 4, 5, 6; ITU-D SG 2; Focus Group on \u2018From/In/To Cars II\u2019 (ITU-T SG 12); ISO TC 22 SC3 and TC 204 ; IEEE 802, 802.11 (WiFi), 802.15.1 (Bluetooth); AUTOSAR WPII-1.1, OSGi VEG, IrDA and JSR298 Tele': None,
    u'ITU-T SQ15 Question 14': [u'itu-t-sg-15-q14'],
    u'ITU-T Study Group 11': [u'itu-t-sg-11'],
    u'ITU-T Study Group 11 <tsg11gen@itu.int>': [u'itu-t-sg-11'],
    u'ITU-T Study Group 13': [u'itu-t-sg-13'],
    u'ITU-T Study Group 15': [u'itu-t-sg-15'],
    u'ITU-T Study Group 15 <greg.jones@itu.int>': [u'itu-t-sg-15'],
    u'ITU-T Study Group 15 Q4 <rlstuart@ieee.org>': [u'itu-t-sg-15-q4'],
    u'ITU-T Study Group 15 Question 14': [u'itu-t-sg-15-q14'],
    u'ITU-T Study Group 15 Question 3': [u'itu-t-sg-15-q3'],
    u'ITU-T Study Group 15 Question 6': [u'itu-t-sg-15-q6'],
    u'ITU-T TSAG External Relations Group': [u'itu-t-tsag'],
    u'ITU-T Working Party 3/13 and ITU-T Question 11/13': [u'itu-t-sg-13-wp3',u'itu-t-sg-13-q11'],
    u'ITU-T and ITU-T Study Group 13': [u'itu-t', u'itu-t-sg-13'],
    u'ITU-T, ITU SG13': [u'itu-t', u'itu-t-sg-13'],
    u'ITU-T-SG13': [u'itu-t-sg-13'],
    u'ITU-T/FG Cloud': ['itu-t-fg-cloud'],
    u'ITU-T/SG11': [u'itu-t-sg-11'],
    u'ITU-T/Study Group 11': [u'itu-t-sg-11'],
    u'Kam Lam, Rapporteur for Question 14 of ITU-T SG15': [u'itu-t-sg-15-q14'],
    u'Kam Lam, Rapporteur for Question 14 of ITU-T Study Group 15': [u'itu-t-sg-15-q14'],
    u'Lyndon Ong (lyong@ciena.com)': [u'sigtran'],
    u'MFA Forum': None,
    u'MPLS and Frame Relay Alliance': None,
    u'Mr. Kam Lam, Rapporteur for Question 14 of ITU-T Study Group 15': [u'itu-t-sg-15-q14'],
    u'National, Multi-National or Regional Organizations': None,
    u'OMA': None,
    u'OMA MEM': None,
    u'OMA MWG': None,
    u'OMA MWG MEM Sub Working Group': None,
    u'OMA TP': None,
    u'OPS ADs (Randy Bush and Bert Wijnen)': [u'ops'],
    u'OPS Area Director Bert Wijnen': [u'ops'],
    u'Open IPTV Forum': None,
    u'Open Mobile Alliance Broadcasting  Working Group': None,
    u'Open Mobile Alliance, PAG Working Group': None,
    u'PDNR ITU-R M.[IP CHAR]': None,
    u'PWE WG': None,
    u'Phase 1 report to SG 4': None,
    u'Q7/13': [u'itu-t-sg-13-q7'],
    u'Rao Cherukuri, Chair MPLS and Frame Relay Alliance Technical Committee': None,
    u'Rao Cherukuri, Chairman, MPLS and Frame Relay Alliance Technical Committee': None,
    u'SA2, T2, OMA TP, S3': None,
    u'SAVI WG, V6OPS WG, OPS AREA,  INT AREA': [u'savi', u'v6ops', u'ops', u'int'],
    u'SC 29/WG11': [u'iso-iec-jtc1-sc29-wg11'],
    u'SC29/WG11': [u'iso-iec-jtc1-sc29-wg11'],
    u'SG 15,Questions 3,9, 11,12, 14 and WP 3/15': [u'itu-t-sg-15-q3',u'itu-t-sg-15-q9',u'itu-t-sg-15-q11',u'itu-t-sg-15-q12',u'itu-t-sg-15-q14',u'itu-t-sg-15-wp3'],
    u'SG-13, Q.3/13, Q.9/13 and TSAG': [u'itu-t-sg-13-q3',u'itu-t-sg-13-q9',u'itu-t-tsag'],
    u'SG13, SG13 WP4': [u'itu-t-sg-13',u'itu-t-sg-13-wp4'],
    u'SG15 Q9': [u'itu-t-sg-15-q9'],
    u'SG15, Q9, Q10, Q12 and Q14': [u'itu-t-sg-15-q9',u'itu-t-sg-15-q10',u'itu-t-sg-15-q12',u'itu-t-sg-15-q14'],
    u'SG15, Q9, Q10, Q12, Q14': [u'itu-t-sg-15-q9',u'itu-t-sg-15-q10',u'itu-t-sg-15-q12',u'itu-t-sg-15-q14'],
    u'SG15, Q9, Q10, Q12, and Q14': [u'itu-t-sg-15-q9',u'itu-t-sg-15-q10',u'itu-t-sg-15-q12',u'itu-t-sg-15-q14'],
    u'SG15, Q9, Q11, Q12 and Q14': [u'itu-t-sg-15-q9',u'itu-t-sg-15-q11',u'itu-t-sg-15-q12',u'itu-t-sg-15-q14'],
    u'SG17, SG13, SG11, JCA-NID, ETSI TISPAN WG4, 3GPP TSG CT4, IESG': None,
    u'SG4': [u'itu-t-sg-4'],
    u'SIP aand SIPPING WGs': [u'sip', u'sipping'],
    u'SIP, SIPPING, SIMPLE WGs': [u'sip', u'sipping', u'simple'],
    u'SUB-IP and Transport Areas': [u'sub', u'tsv'],
    u'Scott Bradner': None,
    u'Scott Bradner (sob@harvard.edu)': None,
    u'Scott Bradner (sob@harvard.edu) Done': None,
    u'SubIP ADs (sob@harvard.edu,bwijnen@lucent.com)': [u'sub'],
    u'TEWG, MPLS, CCAMP WGs': [u'tewg', u'mpls', u'ccamp'],
    u'TRILL WG co-chairs and IEEE-IETF liaisons': None,
    u'TRILL WG co-chairs, ADs, and IEEE-IETF liaisons': None,
    u'TSG-X Corr to IETF re MIP6 Bootstrapping': None,
    u'The IAB': [u'iab'],
    u'The IESG': [u'iesg'],
    u'The IESG and the IAB': [u'iesg', u'iab'],
    u'The IETF': [u'ietf'],
    u'Tom Taylor (taylor@nortelnetworks.com), Megaco WG Chair': [u'megaco'],
    u'Transport ADs (Allison Mankin and Scott Bradner)': [u'tsv'],
    u'Transport Area Directors': [u'tsv'],
    u'Unicode Consortium': None,
    u'Unicode Technical Committee': None,
    u'Various IETF WGs': None,
    u'W3C Geolocation WG': None,
    u'W3C Geolocation Working Group': None,
    u'W3C Multimedia Interaction Work Group': None,
    u'WiFi Alliance and Wireless Broadband Alliance': None,
    u'chair@ietf.org': [u'ietf'],
    u'gonzalo.camarillo@ericsson.com': None,
    u'tsbdir@itu.int': None
}

FROM_NAME_MAPPING = {
    u'3GPP TSG RAN WG2': None,
    u'<unknown body 0>': None,
    u'ATIS': None,
    u'ATM Forum': [u'afic'],
    u'ATM Forum AIC WG': [u'afic'],
    u'BBF': [u'broadband-forum'],
    u'DSL Forum': None,
    u'EPCGlobal': None,
    u'ETSI': None,
    u'ETSI EMTEL': None,
    u'ETSI TC HF': None,
    u'ETSI TISPAN': None,
    u'ETSI TISPAN WG5': None,
    u'Femto Forum': None,
    u'GSMA WLAN': None,
    u'IEEE 802': [u'ieee-802'],
    u'IEEE 802.11': [u'ieee-802-11'],
    u'IEEE 802.21': [u'ieee-802-21'],
    u'IETF ADSL MIB': [u'adslmib'],
    u'IETF MEAD Team': None,
    u'IETF Mead Team': None,
    u'IETF liaison on MPLS': [u'mpls'],
    u'INCITS T11.5': None,
    u'ISO/IEC JTC 1 SC 29/WG 11': [u'iso-iec-jtc1-sc29-wg11'],
    u'ISO/IEC JTC 1 SGSN': None,
    u'ISO/IEC JTC 1/SC31/WG 4/SG 1': None,
    u'ISO/IEC JTC 1/WG 7': None,
    u'ISO/IEC JTC SC 29/WG1': [u'iso-iec-jtc1-sc29-wg1'],
    u'ISO/IEC JTC SC 29/WG11': [u'iso-iec-jtc1-sc29-wg11'],
    u'ISO/IEC JTC1/SC29/WG11': [u'iso-iec-jtc1-sc29-wg11'],
    u'ISO/IEC JTC1/SC6': [u'iso-iec-jtc1-sc6'],
    u'ITU': [u'itu'],
    u'ITU IPv6 Group': [u'itu-t-ipv6-group'],
    u'ITU-Q.14/15': [u'itu-t-sg-15-q14'],
    u'ITU-R WP 5A': [u'itu-r-wp5a'],
    u'ITU-R WP 5D': [u'itu-r-wp5d'],
    u'ITU-R WP8A': [u'itu-r-wp8a'],
    u'ITU-R WP8F': [u'itu-r-wp8f'],
    u'ITU-SC29': None,
    u'ITU-SG 15': [u'itu-t-sg-15'],
    u'ITU-SG 7': [u'itu-t-sg-7'],
    u'ITU-SG 8': [u'itu-t-sg-8'],
    u'ITU-T FG Cloud': [u'itu-t-fg-cloud'],
    u'ITU-T FG IPTV': [u'itu-t-fg-iptv'],
    u'ITU-T Q.5/13': [u'itu-t-sg-13-q5'],
    u'ITU-T SG 15 Q14/15': [u'itu-t-sg-15-q14'],
    u'ITU-T SG 15 WP 1': [u'itu-t-sg-15-wp1'],
    u'ITU-T SG 15, Q.11': [u'itu-t-sg-15-q11'],
    u'ITU-T SG 15, Q.14/15': [u'itu-t-sg-15-q14'],
    u'ITU-T SG 4': [u'itu-t-sg-4'],
    u'ITU-T SG 6': [u'itu-t-sg-6'],
    u'ITU-T SG 7': [u'itu-t-sg-7'],
    u'ITU-T SG 9': [u'itu-t-sg-9'],
    u'ITUT-T SG 16': [u'itu-t-sg-16'],
    u'JCA-IdM': [u'itu-t-jca-idm'],
    u'MFA Forum': None,
    u'MPEG': None,
    u'MPLS Forum': None,
    u'MPLS and FR Alliance': None,
    u'MPLS and Frame Relay Alliance': None,
    u'NANP LNPA WG': None,
    u'NGN Management Focus Group': None,
    u'OMA': None,
    u'OMA COM-CAB SWG': None,
    u'OMA COM-CPM Group': None,
    u'Open IPTV Forum': None,
    u'SC 29/WG 1': [u'iso-iec-jtc1-sc29-wg1'],
    u'SC 29/WG 11': [u'iso-iec-jtc1-sc29-wg11'],
    u'SC29 4559': [u'iso-iec-jtc1-sc29-wg11'],
    u'SC29 4561': [u'iso-iec-jtc1-sc29-wg11'],
    u'SIP, SIPPING, SIMPLE WGs': [u'sip', u'sipping', u'simple'],
    u'T1M1': None,
    u'T1S1': None,
    u'T1X1 cc: ITU-T Q. 14/15 (for info)': None,
    u'TIA': None,
    u'TMOC': None,
    u'The IAB': [u'iab'],
    u'The IESG': [u'iesg'],
    u'The IESG and the IAB': [u'iesg', u'iab'],
    u'The IETF': [u'ietf'],
    u'W3C Geolocation WG': None,
    u'WIG': None
}
