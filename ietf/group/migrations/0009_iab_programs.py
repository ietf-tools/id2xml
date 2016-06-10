# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re

from django.db import migrations

def email(person):
        e = person.email_set.filter(primary=True).first()
        if not e:
            e = person.email_set.filter(active=True).order_by("-time").first()
        return e

def add_group_community_lists(apps, schema_editor, group):
    DocAlias = apps.get_model("doc", "DocAlias")
    State = apps.get_model("doc", "State")
    CommunityList = apps.get_model("community", "CommunityList")
    SearchRule = apps.get_model("community", "SearchRule")

    active_state = State.objects.get(slug="active", type="draft")
    rfc_state = State.objects.get(slug="rfc", type="draft")

    draft_aliases = DocAlias.objects.filter(name__startswith="draft")

    clist = CommunityList.objects.create(group=group)
    SearchRule.objects.create(community_list=clist, rule_type="group", group=group, state=active_state)
    SearchRule.objects.create(community_list=clist, rule_type="group_rfc", group=group, state=rfc_state)
    r = SearchRule.objects.create(community_list=clist, rule_type="name_contains", text=r"^draft-[^-]+-%s-" % group.acronym, state=active_state)
    name_re = re.compile(r.text)
    r.name_contains_index = [ a.document_id for a in draft_aliases if name_re.match(a.name) ]

def addPrograms(apps, schema_editor):

    Group = apps.get_model('group','Group')
    Person = apps.get_model('person','Person')

    fb = Person.objects.create(name='Francis Bond',ascii='Francis Bond')
    fb.email_set.create(address='bond@ieee.org',primary=True,active=True)

    cr = Person.objects.create(name='Christine Runnegar',ascii='Christine Runnegar')
    cr.email_set.create(address='runnegar@isoc.org')

    iab = Group.objects.get(acronym='iab')

    def build_group(acronym, name, description, lead, members, docs):
        g = Group.objects.create(acronym=acronym,
                                 name=name,
                                 state_id='active',
                                 type_id='program',
                                 parent = iab,
                                 description=description,
                            )

        add_group_community_lists(apps, schema_editor, g) 
        cl = g.communitylist_set.first()
        for doc in docs:
            cl.added_docs.add(doc)

        lead_person = Person.objects.get(name=lead)
        g.role_set.create(person=lead_person,name_id='lead',email=email(lead_person))
        for name in members:
            p = Person.objects.get(name=name)
            g.role_set.create(person=p,name_id='member',email=email(p))

    build_group(acronym='stackevo',
                name='IP Stack Evolution',
                description='The IP Stack Evolution program covers various topics in the evolution of IPv4 and IPv6, the transport protocols running over IP, and the overall protocol stack architecture. The program addresses challenges that affect the stack in some way and where the IETF community requires architectural guidance, responding to community requests as well as actively monitoring work within IETF WGs which touch on relevant topics.\n\nThere is an observed trend of functionality moving “up the stack”: where the “waist” was once IP, now most applications run over TCP/IP, or even HTTP/TCP/IP; the stack has become increasingly ossified. This is in response both to reduced path transparency within the Internet — middleboxes that limit the protocols of the traffic that can pass through them — as well as insufficiently flexible interfaces for platform and application developers. The emergence of both new application requirements demanding more flexibility from the stack, especially at layer 4, as well as the increasing ubiquity of encryption to protect against pervasive surveillance, provides an opportunity to re-evaluate and reverse this trend.\n\nThis program aims to provide architectural guidance, and a point of coordination for work at the architectural level to improve the present situation of ossification in the Internet protocol stack. Where a working group relevant to a particular aspect of IP stack evolution exists, the program will facilitate cross-group and cross-area coordination. The program also produces documents on the IAB stream providing general guidance on and covering architectural aspects of stack evolution.',
                lead="Brian Trammell",
                members= ['Brian Trammell',
                           'Ralph Droms',
                           'Ted Hardie',
                           'Joe Hildebrand',
                           'Lee Howard',
                           'Erik Nordmark',
                           'Robert Sparks',
                           'Dave Thaler',
                           'Mary Barnes',
                           'Marc Blanchet',
                           'David L. Black',
                           'Spencer Dawkins',
                           'Lars Eggert',
                           'Aaron Falk',
                           'Janardhan Iyengar',
                           'Suresh Krishnan',
                           u'Mirja K\xfchlewind',
                           'Eliot Lear',
                           'Eric Rescorla',
                           'Natasha Rooney',
                           'Martin Stiemerling',
                           'Michael Welzl',
                          ],
                docs = [ 'draft-iab-protocol-transitions',
                       ],
               )

    build_group(acronym='rfcedprog',
                name='RFC Editor',
                description='The purpose of this program is to provide a focus for the IAB’s responsibility to manage the RFC Editor function, including the RSE.\nThe details of the RSE function, and the RSOC are document in RFC 6635.\n\nThe Program’s main focus is on:\n\n Oversight of the RFC Series\n Assisting the RSE in policy matters as needed\n Oversight of the RSE\n\nThe active membership of this program consists of the RFC Series Oversight Committee (RSOC), which is primarily charged with executing the IAB responsibility to oversee the RSE.',
                lead="Robert Sparks",
                members= ['Joe Hildebrand',
                           'Robert Sparks',
                           'Sarah Banks',
                           'Nevil Brownlee',
                           'Heather Flanagan',
                           'Joel M. Halpern',
                           'Tony Hansen',
                           'Robert M. Hinden',
                           'Ray Pelletier',
                           'Adam Roach',
                          ],
                docs = ['draft-iab-rfc5741bis',
                        'draft-iab-html-rfc',
                        'draft-iab-rfc-css',
                        'draft-iab-rfc-framework',
                        'draft-iab-rfc-nonascii',
                        'draft-iab-rfc-plaintext',
                        'draft-iab-rfc-use-of-pdf',
                        'draft-iab-rfcv3-preptool',
                        'draft-iab-svg-rfc',
                        'draft-iab-xml2rfc',
                        'draft-iab-styleguide',
                        'draft-iab-rfcformatreq',
                       ],
               )

    build_group(acronym='privsec',
                name='Privacy and Security',
                description='The IAB Privacy and Security Program is a successor to its previous Security and Privacy programs.  It provides a forum to develop, synthesize and promote security and privacy guidance within the Internet technical standards community.   While security and privacy have each been explicitly and implicitly considered during the design of Internet protocols, there are three major challenges which face the community:\n\n    * most Internet protocols are developed as building blocks and will be used in a variety of situations.  This means that the security and privacy protections each protocol provides may depend on adjacent protocols and substrates.  The resulting security and privacy protections depend, however, on the initial assumptions remaining true as adjacent systems change.  These assumptions and dependencies are commonly undocumented and may be ill-understood.\n\n    * many security approaches have presumed that attackers have resources on par with those available to those secure the system.  Pervasive monitoring, distributed networks of compromised machines, and the availability of cloud compute each challenge those assumptions.\n\n    * many systems breach the confidentiality of individuals’ communication or request more than the minimally appropriate data from that communication in order to simplify the delivery of services or meet other requirements.  When other design considerations contend with privacy considerations, privacy has historically lost.\n\nThis program seeks to consolidate, generalize, and expand understanding of Internet-scale system design considerations for privacy and security;  to raise broad awareness of the changing threat models and their impact on the properties of Internet protocols; and to champion the value of privacy to users of the Internet and, through that value, as a contributor to the network effect for the Internet.',
                lead='Ted Hardie',
                members=[
                         'Ted Hardie',
                         'Russ Housley',
                         'Martin Thomson',
                         'Brian Trammell',
                         'Suzanne Woolf',
                         'Mary Barnes',
                         'Richard Barnes',
                         'Alissa Cooper',
                         'Stephen Farrell',
                         'Joseph Lorenzo Hall',
                         'Christian Huitema',
                         'Eliot Lear',
                         'Xing Li',
                         'Lucy Lynch',
                         'Karen O\'Donoghue',
                         'Andrei Robachevsky',
                         'Christine Runnegar',
                         'Wendy Seltzer',
                         'Juan-Carlos Z\xfa\xf1iga',
                        ],
                docs = [ 'draft-iab-privsec-confidentiality-mitigations', ]
               )

    build_group(acronym='inip',
                name='Names and Identifiers',
                description='The Names and Identifiers Program covers various topics concerning naming and resolution. As RFC 6055 points out, the DNS is not the only way that naming and resolution happens. Identifiers — not just domain names, but all identifiers — and the resolution of them are important both to users and applications on the Internet. Further, as Internet infrastructure becomes more complex and ubiquitous, the need for powerful, flexible systems of identifiers gets more important. However, in many ways we’re limited by the success of the DNS: it’s used so widely and successfully, for so many things, that compatibility with it is essential, even as demands grow for namespace characteristics and protocol behavior that aren’t included in the DNS and may be fundamentally incompatible with it.\n\nThe IAB has worked on these issues before, but there are several things that have recently changed which make the topic worth revisiting. First, we’re pushing the limits of flexibility in the DNS in new ways: there are growing numbers of protocols and applications (some of them built outside the IETF) that are creating DNS-like naming systems, but that differ from naming rules, wire protocol, or operational restrictions implicit in DNS. We’ve particularly seen cases where these protocols and applications expect to be able to use “domain name slots” where domain names have traditionally appeared in protocols, and the potential for subtle incompatibilities among them provides an opportunity for various forms of surprising results, from unexpected comparison failures to name collisions. In addition, it may be that as a consequence of the vast expansion of the root zone, the intended hierarchical structure of the DNS namespace could be lost, which raises not only operational concerns but also architectural questions of what characteristics are necessary in naming systems for various uses.\n\nAt the same time as that is changing, pressures to provide facilities not previously imagined for the DNS (such as bidirectional aliasing, or better protection for privacy, or context information such as localization or administrative boundaries) require that naming systems for the internet will continue to evolve.\n\nBeyond specific stresses provided by the practical need for compatibility with DNS and its limitations, there are questions about the implications of identifier resolution more widely. For example, various methods for treating different domain names as “the same” have implications for email addresses, and this might have implications for identifier use and comparison more generally, including for i18n. Perhaps more broadly yet, we see an impact on naming systems as we examine needs such as support for scaling in new environments (mobile, IoT) and new priorities such as supporting widespread encryption.\n\nThe program seeks to provide a useful framework for thinking about naming and resolution issues for the internet in general, and to deliver recommendations for future naming or resolution systems.\n\nThe scope of initial investigations is deliberately somewhat open, but could include:\n\n  a. some basic terminology: what do we mean by “names,” “identifiers,” and “name resolution” in the internet? What attributes of naming systems and identifiers are important with regards to comparison, search, human accessibility, and other interactions?\n  b. overview: where are naming protocols and infrastructure important to the work of the IETF (and perhaps elsewhere)? Where is the DNS being used (and perhaps stretched too far)? What other identifier systems are we coming up with, and how well are those efforts working? This area will include examination of some of the naming systems under development or in use elsewhere, such as NDN, as a way of informing our thinking.\n  c. For protocols (inside the IETF or outside), what should protocol designers know about re-using existing naming systems or inventing their own? Are there guidelines we can usefully provide?',
                lead='Suzanne Woolf',
                members=[
                         'Suzanne Woolf',
                         'Marc Blanchet',
                         'Ralph Droms',
                         'Ted Hardie',
                         'Joe Hildebrand',
                         'Erik Nordmark',
                         'Robert Sparks',
                         'Andrew Sullivan',
                         'Dave Thaler',
                         'Brian Trammell',
                         'Edward Lewis',
                         'Jon Peterson',
                         'Wendy Seltzer',
                         'Dr. Lixia Zhang',
                        ],
                docs = [ 'draft-lewis-domain-names', ],
               )

    build_group(acronym='i18n-program',
                name='Internationalization',
                description='Work in the IETF and other areas has exposed the general topic of Internationalization (i18n) as a very complex one, with almost all decisions involving complex tradeoffs along multiple dimensions rather than “right” or “wrong” answers. The IAB intends to try to bring these issues together to reduce the number of decisions that are made on an isolated topic basis and, where appropriate, to review prior IAB and IETF work that has may require updating to reflect accumulated experience.',
                lead='Ted Hardie',
                members=[
                         'Ted Hardie',
                         'Joe Hildebrand',
                         'Andrew Sullivan',
                         'Dave Thaler',
                         'Marc Blanchet',
                         'Francis Bond',
                         'Stuart Cheshire',
                         'Patrik Faltstrom',
                         'Heather Flanagan',
                         'Dr. John C. Klensin',
                         'Olaf Kolkman',
                         'Barry Leiba',
                         'Xing Li',
                         'Pete Resnick',
                         'Peter Saint-Andre',
                        ],
                docs= [],
               )

    build_group(acronym='iproc',
                name='IETF Protocol Registries Oversight',
                description='The IETF Protocol Registries Oversight Committee (IPROC) is an IAB program, as well as subcommittee of the IETF Administrative Oversight Committee (IAOC).\n\nThe primary focus of the IPROC is oversight of operations related to processing IETF protocol parameter requests.  In addition, the IPROC reviews the service level agreement (SLA) between the IETF and ICANN, which is typically updated each year to reflect current expectations.\n\nThe IPROC advises the IAB and the IAOC.  The IAB is responsible for IANA oversight with respect to the protocol parameter registries.  The IAOC is ultimately responsible for the fiscal and administrative support for the IANA protocol parameter registries.\n\nThe IPROC is focused on operations of the protocol parameter registries, not all of the IANA-related activities for the global Internet.  For more information on IAB activities related to broader IANA topics, please see the IANA Evolution Program.',
                lead='Russ Housley',
                members=[
                         'Jari Arkko',
                         'Russ Housley',
                         'Andrew Sullivan',
                         'Bernard Aboba',
                         'Michelle S. Cotton',
                         'Leslie Daigle',
                         'Elise P. Gerich',
                         'Ray Pelletier',
                         'Jonne Soininen',
                        ],
                docs=[],
               )

    build_group(acronym='iana-evolution',
                name='IANA Evolution',
                description='The IANA evolution program’s primary focus is the stewardship over the IANA functions for the Internet in General and the IETF in particular.\n\nIts main focus is on:\n\n  * the contractual relations between the US DoC and ICANN and the globalization thereof;\n  * the IANA MoU (RFC2860) and related agreements between stakeholders;\n  * the development of a vision with respect to the future of the IANA functions; and\n  * implementation and interpretation of the above.\n\nThe program acts also as a think-tank and advises the IAB on strategic and liaison issues.\n\nIn some cases this group may provide guidance and insight on matters relating ICANN in general.\n\nThe group is not responsible for daily operational guidance, such as review of the SLA between the IETF and ICANN.  Those responsibilities are delegated to the IETF Protocol Registries Oversight Committee (IPROC).',
                lead='Russ Housley',
                members=[
                         'Jari Arkko',
                         'Marc Blanchet',
                         'Ted Hardie',
                         'Russ Housley',
                         'Andrew Sullivan',
                         'Suzanne Woolf',
                         'Bernard Aboba',
                         'Kathy Brown',
                         'Alissa Cooper',
                         'Leslie Daigle',
                         'Dr. John C. Klensin',
                         'Olaf Kolkman',
                         'Eliot Lear',
                         'Barry Leiba',
                         'Dr. Thomas Narten',
                         'Andrei Robachevsky',
                         'Jonne Soininen',
                         'Lynn St.Amour',
                        ],
                docs=[ 'draft-iab-aina-mou', 'draft-iab-iana-principles' ],
               )


def removePrograms(apps, schema_editor):
    Group = apps.get_model('group','Group')
    Group.objects.filter(acronym__in=(
                                       'stackevo',
                                        'rfcedprog',
                                        'privsec',
                                        'inip',
                                        'i18n-program',
                                        'iproc',
                                        'iana-evolution',
                                     )
                        ).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('group', '0008_auto_20160505_0523'),
        ('name', '0011_iab_programs'),
        ('person', '0011_populate_photos'),
        ('community','0004_cleanup_data'),
    ]

    operations = [
        migrations.RunPython(addPrograms,removePrograms)
    ]
