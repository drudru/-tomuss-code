/* -*- coding: utf-8 -*- */
/*
  TOMUSS: The Online Multi User Simple Spreadsheet
  Copyright (C) 2011 Thierry EXCOFFIER, Universite Claude Bernard

  This program is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 2 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program; if not, write to the Free Software
  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

  Contact: Thierry.EXCOFFIER@bat710.univ-lyon1.fr
*/

function go_referent_set()
{
  create_popup('import_list',
	       "Indiquer le référent d'une liste d'étudiants",
	       "Indiquer les <b>numéros d'étudiants</b> pour qui "
	       + '<input id="go_referent_set">'
	       + " va devenir référent pédagogique",
	       'Puis cliquez sur : <BUTTON OnClick="go_referent_set_do();">Affecter les étudiants</BUTTON>.',
	       '') ;
}

function go_referent_set_do()
{
  var values = popup_text_area().value.split(/[ \t\n,;.:]+/) ;
  var teacher = document.getElementById('go_referent_set').value ;

  create_popup('import_list',
	       "Résultat de l'opération :",
	       '<iframe width="100%" src="' + base
	       + 'referent_set/' + teacher + '/'
	       + values.join('/') + '">' + '</iframe>',
	       "",
	       false) ;
}
