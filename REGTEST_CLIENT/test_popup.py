import time

def run(t):
    t.goto_url("http://%s:8888/=super.user/9999/Test/average/=print-table=" % t.server)
    t.check_image("print-table")

    return # The others tests don't work (popup forbidden)

    t.xnee.key('Tab')
    t.xnee.key('Return')
    t.check_image("signature-page")

    t.xnee.key('Tab')
    t.xnee.key('Return')
    t.check_image("paginated")

    t.xnee.key('Tab')
    t.xnee.string('FOO')
    t.check_image("signature-column")

    t.xnee.key('Tab')
    t.xnee.key('BackSpace')
    t.check_image("signature-hide")

    t.goto_url("http://%s:8888/=super.user/9999/Test/demo_animaux/=facebook=" % t.server)
    t.check_image("facebook")

