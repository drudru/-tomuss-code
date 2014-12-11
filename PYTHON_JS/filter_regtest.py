# -*- coding: utf-8 -*-
# TOMUSS: The Online Multi User Simple Spreadsheet
# Copyright (C) 2013-2014 Thierry EXCOFFIER, Universite Claude Bernard
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Contact: Thierry.EXCOFFIER@univ-lyon1.fr

debug = True

def checkDate(value, expected):
    if user_date_to_date(value) != expected:
        print("user_date_to_date(",value,')=', user_date_to_date(value))
        print('Expected:', expected)
        regression_test_failed

year_month_day = [2014, 5, 15, 12]
current_seconds = 1400148000
        
def dateRegtest():
    if ','.join(REsplit("[ab]", "1a2b3")) != '1,2,3':
        regression_test_failed

    checkDate('1/1/2014', '20140101')
    checkDate('1', '20140501')
    checkDate('16', '20140516')
    checkDate('16/1', '20140116')
    checkDate('16 18', '2014051618')
    checkDate('16 18:1', '201405161801')
    checkDate('16/1 18:1:1', '20140116180101')
    checkDate('1h', '20140515110000')
    checkDate('0.5h', '20140515113000')
    checkDate('1d', '20140514120000')
    checkDate('24h', '20140514120000')
    checkDate('1w', '20140508120000')
    checkDate('1m', '20140415120000')
    checkDate('5j', '20140510120000')

def filterRegtest():
    bugs = []
    def bug(message, txt, username="", column_type=""):
        print(message + ' for ' + txt)
        print(Filter(txt, username, column_type).js())
        bugs.append(1)
    class Cell:
        def __init__(self, value, author, date, history, comment):
            self.value = value
            self.author = author
            self.date = date
            self.history = history
            self.comment = comment
        def js(self):
            return ('Cell(' + self.value + ',' + self.author + ','
                   + self.date + ',' + self.history + ',' + self.comment
                    + ')')
    tst = "joHé n<>Ê#@?&=→/"
    c = Cell(4, tst, "20140510181920", "14", "")
    # Simple filter that should return True.
    # They are also tested prefixed by !
    for tst in ['', '<5', '<=4', '>3', '=4', '>=4', '@j', '@<k', ':<15', ':~4',
                '<12', '<4.1', '=4.0', '<4,1', '<14,1', '=4,0',
                '?=10/05/2014', '?=10/05', '?=10',
                '?>9', '?<1/6', '?>=10',
                '?>10/05/2014\\ 18:18', '?>10/05/2014\\ 18:19:19',
                '?>10/05/2014_17',
                '?<5j', '?<114h', '?>4j',
                '#=', ":",
                '@~=', '@~\\&=', "@~\\ n", "@~\\ ", "@~H",
                "@~h", "@~e", "@~é", "@~ê", "@~E", "@~→/",
                "#=", "=4 ", "4 "
                ]:
        if not Filter(tst, "", "").evaluate(c):
            bug("BUG1", tst)
        tst = '!' + tst
        if Filter(tst, "", "").evaluate(c):
            bug("BUG2", tst)
    # Simple filter that should return False.
    # They are also tested prefixed by !
    for tst in ['<4', '<=3', '>4', '=5', '>=5', '@o', '@<j', ':>3', ':~3',
                '?=9/05/2014', '?=9/05', '?=9',
                '?>10', '?>=31', '@>k', "#",
                '?>10/05/2014-18:19', '?>10/05/2014\\ 18:19:20',
                '?>10/05/2014_18',
                '?', '?<=4j',
                'undefined',
                "@~è", contextual_case_sensitive and "@~J" or 'NO',
                "@~=/", # Test if → is lost
                "\\ ",
                ]:
        if Filter(tst, "", "").evaluate(c):
            bug("BUG3", tst)
        tst = '!' + tst
        if not Filter(tst, "", "").evaluate(c):
            bug("BUG4", tst)

    # Complex filter that should return True.
    for tst in ["@j&:14", "@j &:14", "@j & :14", "@j& :14", "@j :14",
                "@j & :14 & =4", "@j :14 =4", "@j   :14   =4",
                "=4|=5", "=4 | =5", "=5 | =4", "=5 OR =4", "=5 OR !=6",
                "@~&=4", '!a !b', '!a 4', '4 !a'
                ]:
        tst = tst.replace('OR', or_keyword())
        if not Filter(tst, "", "").evaluate(c):
            bug("BUG5", tst)

    # Complex filter that should return False.
    for tst in ['@j & :13', '@k & :14', '@j :13', '@k :14', '@k   :14',
                '@~&=', "@~ n", 'b !4', '!4 b',
                ]:
        if Filter(tst, "", "").evaluate(c):
            bug("BUG6", tst)

    # Special cases
    for cell_filters_result in [
        [[''   , "john", "", "", ""], ["@"    , "xx"  , ""], False],
        [[''   , "john", "", "", ""], ["@"    , "john", ""], True ],
        [[''   , "john", "", "", ""], ["@"    , "joh" , ""], False],
        [['5,3', ""    , "", "", ""], ["<5.2" , ""    , ""], False],
        [['5,3', ""    , "", "", ""], ["<5.31", ""    , ""], True ],
        [['5.3', ""    , "", "", ""], ["<5,31", ""    , ""], True ],
        [['5.3', ""    , "", "", ""], ["<5,2" , ""    , ""], False],
        [['5/' , ""    , "", "", ""], ["<51"  , ""    , ""], False],
        [['5a' , ""    , "", "", ""], ["<51"  , ""    , ""], False],
        [['a'  , ""    , "", "", ""], [">10"  , ""    , ""], False],
        [[''   , ""    , "", "", ""], ["<4"   , ""    , ""], True],
        [[''   , ""    , "", "", ""], [">=0"  , ""    , ""], True],
        [[''   , ""    , "", "", ""], ["=0"   , ""    , ""], True],
        [[''   , ""    , "", "", ""], ["<0"   , ""    , ""], False],
        [[''   , ""    , "", "", ""], [">0"   , ""    , ""], False],
        [['\n' , ""    , "", "", ""], ["="    , ""    , ""], False],
        [['a b', ""    , "", "", ""], ["a b"  , ""    , ""], True],
        [['a'  , ""    , "", "", ""], ["a | b", ""    , ""], True],
        [[''   , ""    , "", "", ""], ["x"    , ""    , "Date"], False],
        [[''   , ""    , "", "", ""], ["xd"   , ""    , "Date"], False],
        [['ab' , ""    , "", "", ""], ["=a"   , ""    , ""], False],
        [['a'  , ""    , "", "", ""], ["=a"   , ""    , ""], True],
        [[''   , ""    , "", "","x"], ["#=x"  , ""    , ""], True],
        [['0'  , ""    , "", "", ""], ["="    , ""    , ""], False],
        ]:
        cell, filters, result = cell_filters_result
        if Filter(filters[0], filters[1], filters[2]
                  ).evaluate(Cell(cell[0], cell[1], cell[2], cell[3], cell[4]
                              )) != result:
            bug("BUG7", filters[0], username=filters[1])
        if Filter('!'+filters[0], filters[1], filters[2]
                  ).evaluate(Cell(cell[0], cell[1], cell[2], cell[3], cell[4]
                              )) == result:
            print(cell, filters)
            bug("BUG8", '!'+filters[0], username=filters[1])

    # Date
    c = Cell('10/5/2014 18:19:20', "", "", "", "")
    for tst in ['<16/5/2014', '<16/5', '<16', "=10", "=10/5", "=10/5/2014",
                '<10/5/2014\\ 19', '<=10/5/2014-18:19','<10/5/2014-18:19:21']:
        if not Filter(tst, "", "Date").evaluate(c):
            bug("BUG10", tst, username="", column_type="Date")
    for tst in ['<9/5/2014', '<9/5', '<9',
                '<10/5/2014\\ 18', '<10/5/2014_18:19','<10/5/2014-18:19:20']:
        if Filter(tst, "", "Date").evaluate(c):
            bug("BUG11", tst, username="", column_type="Date")

        
    if len(bugs):
        regression_test_failed

if str(5) != '5': # For translation to JS source
    float2str_bug
dateRegtest()
filterRegtest()
print('Filter regtest are fine')
