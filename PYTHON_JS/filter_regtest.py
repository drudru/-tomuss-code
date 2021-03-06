#!/usr/bin/python3
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
        print(("user_date_to_date(",value,')=', user_date_to_date(value)))
        print(('Expected:', expected))
        regression_test_failed

minors = []

def localtime():
    return [2014, 5, 15, 12]

def millisec():
    return 1400148000 * 1000

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
        print((message + ' for ' + txt))
        print((Filter(txt, username, column_type).js()))
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
    tst = "joHé n<>Ê#@?&=→/\\\\"
    c = Cell(4, tst, "20140510181920", "14", "")
    line = []
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
                "#=", "=4 ", "4 ", "4.", "4.0", "@~\\\\\\\\",
                "@~\\ ", "@>é", "@<ô"
                ]:
        if not Filter(tst, "", "Note").evaluate(line, c):
            bug("BUG1", tst)
        if not Filter(tst, "", "").evaluate(line, c):
            bug("BUG1.0", tst)
        if not Filter(' ' + tst + ' ', "", "").evaluate(line, c):
            bug("BUG1.1", ' ' + tst + ' ')
        tst = '!' + tst
        if Filter(tst, "", "").evaluate(line, c):
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
                "@>ô",
                "@~=/", # Test if → is lost
                "\\ ",
                ]:
        if Filter(tst, "", "").evaluate(line, c):
            bug("BUG3", tst)
        if Filter(tst+' ', "", "").evaluate(line, c):
            bug("BUG3space", tst)
        tst = '!' + tst
        if not Filter(tst, "", "").evaluate(line, c):
            bug("BUG4", tst)
        if not Filter(tst + ' ', "", "").evaluate(line, c):
            bug("BUG4space", tst)

    # Complex filter that should return True.
    for tst in ["@j&:14", "@j &:14", "@j & :14", "@j& :14", "@j :14",
                "4 :14", "4  :14",
                "@j & :14 & =4", "@j :14 =4", "@j   :14   =4",
                "=4|=5", "=4 | =5", "=5 | =4", "=5 OR =4", "=5 OR !=6",
                "@~&=4", '!a !b', '!a 4', '4 !a',
                "=5 OR =4 OR =3", "=4 OR =3 OR =5", "=3 OR =5 OR =4",
                ">3 <5",
                ">3 <5 <9",
                ">3 <5 <9 OR >9",
                ">3 <5 <9 OR >9 >9",
                ">9 >9 OR >3 <5 <9",
                ]:
        tst = replace_all(tst, 'OR', or_keyword())
        if not Filter(tst, "", "").evaluate(line, c):
            bug("BUG5", tst)
        if not Filter(tst + ' ', "", "").evaluate(line, c):
            bug("BUG5space", tst)

    # Complex filter that should return False.
    for tst in ['@j & :13', '@k & :14', '@j :13', '@k :14', '@k   :14',
                '@~&=', "@~ n", 'b !4', '!4 b',
                ]:
        if Filter(tst, "", "").evaluate(line, c):
            bug("BUG6", tst)
        if Filter(tst+' ', "", "").evaluate(line, c):
            bug("BUG6space", tst)

    # Special cases
    for cell_filters_result in [
        [[''   , "john", "", "", ""], ["@"    , "xx"  , ""], False],
        [[''   , "john", "", "", ""], ["@"    , "john", ""], True ],
        [[''   , "john", "", "", ""], ["@"    , "joh" , ""], False],
        [['jo' , ""    , "", "", ""], ["=@[]" , "jo"  , ""], True],
        [['jo' , ""    , "", "", ""], ["=@[]o", "j"  , ""], True],
        [['jo' , ""    , "", "", ""], ["@[]"  , "jo"  , ""], True],
        [['jo2', ""    , "", "", ""], ["@[]"  , "jo"  , ""], True],
        [[''   , ""    , "", "", "jo"], ["#=@[]", "jo"  , ""], True],
        [[''   , ""    , "", "", "jo"], ["#=@[]", "jh"  , ""], False],
        [[''   , ""    , "", "", "joh"], ["#@[]", "jo"  , ""], True],
        [[''   , ""    , "", "", "joh"], ["#@[]", "jh"  , ""], False],
        [['j'  , ""    , "", "", ""], ["~@[]" , "jo"  , ""], False],
        [['j'  , ""    , "", "", ""], ["@[]"  , "jo"  , ""], False],
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
        [[''   , ""    , "", "", ""], ["0"    , ""    , ""], False],
        [[''   , ""    , "", "", ""], ["="    , ""    , ""], True],
        [['\n' , ""    , "", "", ""], ["="    , ""    , ""], False],
        [['a b', ""    , "", "", ""], ["a b"  , ""    , ""], True],
        [['a'  , ""    , "", "", ""], ["a | b", ""    , ""], True],
        [[''   , ""    , "", "", ""], ["x"    , ""    , "Date"], False],
        [[''   , ""    , "", "", ""], ["xd"   , ""    , "Date"], False],
        [['ab' , ""    , "", "", ""], ["=a"   , ""    , ""], False],
        [['a'  , ""    , "", "", ""], ["=a"   , ""    , ""], True],
        [[''   , ""    , "", "","x"], ["#=x"  , ""    , ""], True],
        [['0'  , ""    , "", "", ""], ["="    , ""    , ""], False],
        [['#'  , ""    , "", "", ""], ["\\#"  , ""    , ""], True],
        [['!'  , ""    , "", "", ""], ["\\!"  , ""    , ""], True],
        ]:
        cell, filters, result = cell_filters_result
        if Filter(filters[0], filters[1], filters[2]
                  ).evaluate(line, Cell(cell[0], cell[1], cell[2], cell[3], cell[4]
                              )) != result:
            bug("BUG7", filters[0], username=filters[1])
        if Filter('!'+filters[0], filters[1], filters[2]
                  ).evaluate(line, Cell(cell[0], cell[1], cell[2], cell[3], cell[4]
                              )) == result:
            print((cell, filters))
            bug("BUG8", '!'+filters[0], username=filters[1])

    # Date
    c = Cell('10/5/2014 18:19:20', "", "", "", "")
    for tst in ['<16/5/2014', '<16/5', '<16', "=10", "=10/5", "=10/5/2014",
                '<10/5/2014\\ 19', '<=10/5/2014-18:19','<10/5/2014-18:19:21']:
        if not Filter(tst, "", "Date").evaluate(line, c):
            bug("BUG10", tst, username="", column_type="Date")
    for tst in ['<9/5/2014', '<9/5', '<9',
                '<10/5/2014\\ 18', '<10/5/2014_18:19','<10/5/2014-18:19:20']:
        if Filter(tst, "", "Date").evaluate(line, c):
            bug("BUG11", tst, username="", column_type="Date")

    # Double spaces
    c = Cell('a  b', "", "", "", "")
    for tst in ['a ', 'a  b  ', 'a  ~b  ', '~\\ ', "~\\ \\ "]:
        if Filter(tst, "", "").evaluate(line, c) is not True:
            bug("BUG12", tst, username="", column_type="Text")

    # Other column on operator left
    columns_set([Column({'title': 'A'}),
                 Column({'title': 'B'}),
                 Column({'title': 'C'}),
                 Column({'title': 'D'}),
                 Column({'title': 'E'}),
                 Column({'title': 'F'}),
                 Column({'title': 'G'}),
                 Column({'title': 'H'}),
             ])
    line = [
        Cell('Va'                ,"Aa","20140510181920","8,8","Ca"),
        Cell('9,9'               ,"Ab","20140510181930","Va" ,"Cb"),
        Cell('10'                ,"Ac","20140510181940","8.8","Cc"),
        Cell('10/5/2014 18:19:35',"Ad","20140510181950",""   ,"Cd"),
        Cell(8.9                 ,"Ae","20140510181940","He" ,"Ce"),
        Cell("9a"                ,"Af","20140510181940","Hf" ,"Cf"),
        Cell(11                  ,"Ag","20140515120000","Aa" ,"15/5/2014 13"),
        Cell(0                   ,"Ah","20140515120000","Hh" ,"Cee"),
    ]
    for tst in ['9', '[A]=Va', '[C]=10', '[A]V', '[A]<Vb', '[A]~a', '![A]>Va',
                '[C]1', '[A] [C]', '9 [A]',
                '#[A]=Ca', '#[A]C', '!#[A]>D', '[B]<10',
                '[A]=Va [B]=9,9 @[C]Ac ?[B]=10/5/2014 !?[B]=11/5/2014',
                ":=[A]", ":<[C]", ":~[A]", "<=[B]", "<[C]",
                "?<[D]", "?[A]<[D]", "?[C]>[D]",
                "?[B]>?[A]", "?[C]>?[B]", "!?[C]<?[A]", "?>?[A]", "?<?[C]",
                ":[A]=:[C]", ":<:[A]",
                "[D]=[D]", ":[D]=:[D]", "#[D]=#[D]", "?[D]=?[D]", "@[D]=@[D]",
                "[D]>=[D]",":[D]>=:[D]","#[D]>=#[D]","?[D]>=?[D]","@[D]>=@[D]",
                "[D]<=[D]",":[D]<=:[D]","#[D]<=#[D]","?[D]<=?[D]","@[D]<=@[D]",
                "[D]~[D]", ":[D]~:[D]", "#[D]~#[D]", "?[D]~?[D]", "@[D]~@[D]",
                "@[C]>@[B] [C]>[B] [A]=:[B]",
                "[E]<[G]", "[E]<[B]",
                "[E]>[F]", # XXX Not nice because 9a is smaller than 8
                "@[A]=Aa", ":[G]=@[A]", "@[]=Ad", "@[]=@[D]", "@[]=ad",
                "?[]=15/5/2014-12", "?[]=?[G]", "?[G]=?[]", "[D]<?[]",
                "#[G]>?[]", "#[F]>?[]",
                "[H]=:[D]", "[H]0.", "#[H]#[E]",
                ">[F]", "!>\\[F]",
                "@>[F]", "!@<\\[A]", "@>\\[A]",
            ]:
        if Filter(tst, "Ad", "").evaluate(line, line[1]) is not True:
            bug("BUG13", tst, username="Ad", column_type="Text")

    # Check other_data_col
    for tst in [
            ["A", []],
            ["[B]", [1]],
            ["?[C]", [2]],
            [">[D]", [3]],
            ["?[] @[]", []],
            ["[E]>[F]", [4,5]],
            ["[G] | [H]", [6,7]],
            ["[H] [G] | ?[B]<?[A]", [0,1,6,7]],
            ]:
        computed = Filter(tst[0], "", "").other_data_col()
        expected = tst[1]
        error = len(computed) != len(expected)
        for i in range(len(computed)):
            if computed[i] != expected[i]:
                error = True
        if error:
            print(computed)
            print(expected)
            bug("other_data_col", tst[0])

    if len(bugs):
        regression_test_failed

if str(5) != '5': # For translation to JS source
    float2str_bug

if js_str('\\"\'\\') != '"\\\\\\"\'\\\\"':
    js_str_bug1

dateRegtest()
filterRegtest()
print('Filter regtest are fine')
