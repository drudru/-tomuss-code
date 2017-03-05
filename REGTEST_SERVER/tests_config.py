vars = {
    'test_int': ("Test title", 6),
    'test_str': ("Test title", "7"),
    'test_tuple': ("Test title", (8,9)),
    'test_list': ("Test title", [10,11]),
    'test_dict': ("Test title", {"a": "A", "b": "B"}),
}

def init(year):
    import os
    import shutil
    import glob
    for dirname in ['DBregtest', 'BACKUP_DBregtest',
                    '/tmp/DBregtest', '/tmp/BACKUP_DBregtest', 
                    ] + glob.glob('TMP/TICKETS/*'):
        print('delete:', dirname)
        try:
            os.unlink(dirname)
        except OSError:
            shutil.rmtree(dirname, ignore_errors=True)
    for i in ('DBregtest', 'BACKUP_DBregtest'):
        name = '/tmp'
        for j in (i, 'Y%d' % (year - 1), 'SAutomne'):
            name += "/" + j
            os.mkdir(name)
            open(os.path.join(name, "__init__.py"), "w").close()
        os.symlink(name, i)
