#!/usr/local/bin/perl

system "/usr/informix/local/wgsummary -mysql >/ftp/ietf/1wg-summary.txt";
system "/usr/informix/local/wgsummary -mysql -byacronym > /ftp/ietf/1wg-summary-by-acronym.txt";
system "/usr/informix/local/idabstracts -mysql >/ftp/internet-drafts/1id-abstracts.txt";
system "/usr/informix/local/idindex >/ftp/internet-drafts/1id-index.txt";
system "/usr/informix/local/old_standards >/ftp/iesg/1old_standards.txt";
system "/usr/informix/local/protocol_actions >/ftp/iesg/1protocol_actions.txt";
system "/usr/informix/local/wgactions >/ftp/iesg/1wg_actions.txt";
system "/usr/informix/local/wgdescriptions >/ftp/ietf/1wg-charters.txt";

chdir "/export/home/ietf/temp";
system "/usr/informix/local/wgdescriptions -byacronym >/ftp/ietf/1wg-charters-by-acronym.txt";
system "/usr/informix/local/wgchairs";
chdir "/export/home/ietf/MAILING-LISTS";
system "/export/home/ietf/MAILING-LISTS/WG.EXE";
system "/usr/informix/local/update_charters";
system "/export/home/ietf/getrfc.cron";
system "cp /ftp/iesg/1rfc_index.txt /ftp/ietf/1rfc_index.txt";

chdir "/usr/local/etc/httpd/htdocs";
system "/usr/informix/local/ids2html.pl /ftp/internet-drafts/1id-abstracts.txt ids.by.wg";


system "/export/home/mlee/RELEASE/gen_agenda_html.pl -deploy";
system "/export/home/mlee/RELEASE/gen_soi_html.pl -deploy";
system "/export/home/mlee/RELEASE/gen_pwg_html.pl -deploy";
system "/export/home/mlee/RELEASE/gen_lastcall_html.pl -deploy";

exit;

