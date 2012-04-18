import os
from datetime import datetime
from time import mktime
import sqlite3

data      = "src-data    : /home/amethist/data/%(date)s/"
outlook   = "src-outlook : /home/amethist/outlook/%(date)s/"
thuis_oud = "src-thuis   : /home/amethist/backups_oud/thuis/"
thuis     = "src-thuis   : /home/amethist/thuis/"
website   = "src-website : /var/www/amethist/"

configs = [
( 1, '2010-08-01', [data, outlook]),
( 2, '2010-09-01', [data]),
( 3, '2010-10-01', [data]),
( 4, '2010-11-01', [data]),
( 5, '2010-12-01', [data]),
( 6, '2011-01-01', [data]),
( 7, '2011-02-01', [data]),
( 8, '2011-03-01', [data]),
( 9, '2011-04-01', [data]),
(10, '2011-05-01', [data, thuis_oud]),
(11, '2011-06-01', [data]),
(12, '2011-07-01', [data]),
(13, '2011-08-01', [data]),
(14, '2011-09-01', [data, outlook]),
(15, '2011-10-01', [data, outlook]),
(16, '2011-11-01', [data, outlook]),
(17, '2011-12-01', [data, outlook]),
(18, '2012-01-01', [data, outlook]),
(19, '2012-02-01', [data, outlook]),
(20, '2012-03-01', [data, outlook]),
(21, '2012-04-01', [data, outlook]),
(22, '2012-04-02', [data]),
(23, '2012-04-03', [data]),
(24, '2012-04-04', [data]),
(25, '2012-04-05', [data]),
(26, '2012-04-06', [data]),
(27, '2012-04-07', [data, outlook]),
(28, '2012-04-08', []),
(29, '2012-04-09', []),
(30, '2012-04-10', [data, outlook]),
(31, '2012-04-11', [data, outlook]),
(32, '2012-04-12', [data, outlook]),
(33, '2012-04-13', [outlook]),
(34, '2012-04-14', [data, outlook]),
(35, '2012-04-15', [data, outlook, thuis, website])]

fp = file('config/convert.cfg.tpl', 'r')
base = fp.read()
fp.close()

for (i, date, sources) in configs:
    print "\n\n"
    print date + "  : " + str(datetime.now())
    output = ''
    for source in sources:
        output += source % {'date': date} + "\n"
    print output
    fp = file('config/convert.cfg', 'w')
    fp.write(base + output)
    fp.close()

#    continue;

    os.system('./argyver.py -c config/convert.cfg -v 5')
    db = sqlite3.connect('/home/amethist/backup_new/.data.sqlite')
    db.cursor().execute('UPDATE iterations SET time = ? WHERE id = ?', (mktime(datetime.strptime(date, '%Y-%m-%d').timetuple())+27*60*60, i))
    db.commit()
    db.close()
