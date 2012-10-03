"""
Example of template of table.

To use it:   http://tomuss...../2012/Example/a_table_name


If you want to use a table with students, then you should start with the
Automne.py and Printemps.py templates and modify them.
If you do not do this, the Mail and ABJ and TT functionnalities will not work.

"""


from ... import data
from ... import document
from ... import configuration

def create(table):
    """This function is called when the table is created on first visit.
    It will never be called once the file exists.
    """
    # Use ro_page to set UNMODIFIABLE values, even by root.
    ro_page = table.new_page('' ,data.ro_user, '', '')
    # Use rw_page to set values modifiables only by root.
    rw_page = table.new_page('' , configuration.root[0], '', '')
    # Use everybody to set values modifiables by anybody
    everybody_page = table.new_page('' , data.rw_user, '', '')
    # Create the columns.
    # You can use this function to modify existing columns.
    # You can use it more than once.
    # It will not delete columns.
    # The column key must NEVER be modified.
    # The column order is the alphabetical order of the keys,
    # to change the order, use the 'position' attribute.
    # All the column attributes are optional.
    table.update_columns(
        {
            '0': {'type': 'Login',      # The content type
                  'freezed': 'F',       # 'F': Fixed, so always visible
                  'title': 'ID'},
            '1': {'type': 'Firstname',  # Compute the firstname
                  'freezed': 'F',       # 'F': Fixed,
                  'columns': 'ID',      # Firstname of ID in first column
                  'title': 'Firstname',
                  },
            '2': {'type': 'Surname',    # Compute the surname
                  'freezed': 'F',       # 'F': Fixed,
                  'columns': 'ID',      # Surname of ID in first column
                  'title': 'Surname',
                  },                  
            'a': {'type': 'Bool',       # The content type
                  'title': 'A_boolean', # The title
                  'empty_is': 'YES',    # The value is empty
                  'green': 'YES',       # Display in green the YES (filter)
                  'comment': "blabla",  # A comment
                  },
            'b': {'type': 'Note',       # column of grades
                  'title':'First_Exam' },
            'c': {'type': 'Note',
                  'title':'Second_Exam',
                  'minmax': '[0;10]',   # Maximum grade is 10 on 10
                  'weight': 2,          # If not defined, the weight is '1'
                  },
            'd': {'type': 'Moy',        # Compute average
                  'title': 'Average',
                  'columns': 'First_Exam Second_Exam',
                  'red': '<6',          # Display in red if the grade is <6
                  },            
            'e': {'type': 'Text',
                  'title': 'Remarks',
                  'width': 10,          # Proportionnal width
                  },            
            },
        rw_page # Change to ro_user if you wan these values not modifiable.
        )

    # Define table attributes :
    table.table_attr(rw_page, 'default_nr_columns', 8)

def init(table):
    """This function is called before loading the table content.
    This can be used to change default values, the user can override them.
    """
    # Allow the table to be modified by users.
    if table.year > 2010:
        table.modifiable = 1
    # Call the 'check' method of the template to update the table
    table.update_inscrits = table.modifiable

def onload(table):
    """This function is called after loading the table content.
    This can be used to change values setted by the user
    or to work on the table content.
    """
    pass

def check(table):
    """This function is called asynchronously to update the table content.
    This function can take time to execute, it will not freeze the server.
    This example compute the table content.
    It can also update the column definitions.
    """
    ro_page = table.pages[0]
    rw_page = table.pages[1]
    everybody_page = table.pages[2]
    table.lock()
    try:
        # Create some cell content automaticaly
        for line in ('x', 'y', 'z'):
            table.cell_change(rw_page,     # The author of the change
                              '0',         # The column identifier
                              line,        # The line identifier: [a-Z0-9_]*
                              'ID ' + line # The cell content
                              )
            table.cell_change(rw_page,     # The author of the change
                              'a',         # The column identifier
                              line,        # The line identifier: [a-Z0-9_]*
                              line == 'y' and 'YES' or 'NO'
                              )
    finally:
        table.unlock()

    # If you want to have the mails workings :
    from ...TEMPLATES import _ucbl_
    _ucbl_.check(table, update_inscrits=lambda x,y,z: None)


def content(table):
    """This javascript code allow to redefine functions in the libraries.
    This allows to change the GUI for the table editor.
    """
    return """
// This function is called each time the cursor change of line.
function update_student_information(line)
{
   if ( t_student_picture.tagName === 'IMG' )
      {
         // We do not want the student picture in this table
         t_student_picture = t_student_picture.parentNode ;
      }
      
   t_student_picture.innerHTML = 'NO PICTURE<br>LINE INFORMATION:<br>'
                               + line[0].value ;
}
"""

def cell_change(table, page, col_id, lin_id, new_value, date):
    """This function is called each time the USER change a value.
    It is not called when loading the table.
    If an error is raised, the value will not be changed.
    This function must be quick.
    """
    pass
