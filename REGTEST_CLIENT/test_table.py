
def run(t):
    t.goto_url("http://%s:8888/=super.user/9999/Test/average" % t.server)
    t.check_image("home_average")

    t.xnee.key('Down')
    t.check_image('table_cur_down', message='Cursor down')

    t.xnee.key('Right')
    t.check_image('table_cur_right', message='Cursor right')

    t.xnee.key('Tab')
    t.check_image('table_cur_tab', message='Tabulation')
