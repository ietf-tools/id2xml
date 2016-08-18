# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


content ='''The Internet Engineering Task Force (IETF) provides a forum for working groups to coordinate technical development of new protocols. Its most important function is the development and selection of standards within the Internet protocol suite.

The IETF began in January 1986 as a forum for technical coordination by contractors for the then US Defense Advanced Research Projects Agency (DARPA), working on the ARPANET, US Defense Data Network (DDN), and the Internet core gateway system. Since that time, the IETF has grown into a large open international community of network designers, operators, vendors, and researchers concerned with the evolution of the Internet architecture and the smooth operation of the Internet.

The IETF mission includes:

* Identifying and proposing solutions to pressing operational and technical problems in the Internet
* Specifying the development or usage of protocols and the near-term architecture, to solve technical problems for the Internet
* Facilitating technology transfer from the Internet Research Task Force (IRTF) to the wider Internet community;and
* Providing a forum for the exchange of relevant information within the Internet community between vendors, users, researchers, agency contractors, and network managers.

Technical activities in the IETF are addressed within working groups. All working groups are organized roughly by function into seven areas. Each area is led by one or more Area Directors who have primary responsibility for that one area of IETF activity. Together with the Chair of the IETF/IESG, these Area Directors comprise the Internet Engineering Steering Group (IESG).
'''

def new_templates(apps, schema_editor):
    DBTemplate = apps.get_model("dbtemplate", "DBTemplate")
    Group = apps.get_model("group", "Group")
    group = Group.objects.get(acronym='ietf')
    DBTemplate.objects.create(
        content=content,
        group=group,
        path='/meeting/proceedings/overview.rst',
        title='Proceedings Overview Template',
        type_id='rst')
    

class Migration(migrations.Migration):

    dependencies = [
        ('meeting', '0034_auto_20160818_1555'),
    ]

    operations = [
        migrations.RunPython(new_templates),
    ]
