import time

def run(t):
    t.goto_url("http://%s:8888/=super.user/9999/Test/average" % t.server)
    t.check_image("home_average")

    t.xnee.key('Down')
    t.check_image('table_cur_down', message='Cursor down')

    t.xnee.key('Right')
    t.check_image('table_cur_right', message='Cursor right')

    for i in range(10):
        t.xnee.key('Down')
    # Empty cell in 'Note1' column
    t.xnee.key('1')
    t.xnee.key('Right')
    t.check_image('table_input_1', message="Input '1' in a cell")

    t.xnee.key('a')
    time.sleep(0.2)
    t.xnee.key('b')
    time.sleep(0.2)
    t.xnee.key('j')
    t.check_image('table_input_abj',
                  message="Input 'abj' in a cell to test completion")

    t.xnee.key('Right')
    t.xnee.key('1')
    t.check_image('table_input_ro',
                  message="Try to modify a constant cell")
        
    t.xnee.key('Tab')
    t.check_image('table_cur_tab', message='Tabulation')

    t.xnee.key('2')
    t.xnee.key('2')
    t.xnee.key('2')
    t.xnee.key('Return')
    t.check_image('table_bad_note', message='Bad note')
    t.xnee.key('Escape')
    time.sleep(0.1)

    t.xnee.key('Up')
    t.xnee.key('2')
    t.xnee.key('Tab')
    t.check_image('table_edit_tab', message='Tab key on edit')

    t.xnee.key('Left')
    t.xnee.key('3')
    t.xnee.key('3')
    t.xnee.key('3')
    time.sleep(0.5)
    t.xnee.key('Escape')
    time.sleep(0.5)
    t.xnee.key('Right') # Do not stay on the cell to not see the date
    t.check_image('table_edit_escape', message='Escape to stop edit')
