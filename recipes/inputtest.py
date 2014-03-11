def get_dependencies(request):
    dependencies = []
    depends_string = ""
    try:
        depends = dict(request.POST)['depends']
    except Exception:
        depends = None
    if depends is not None:
        for d in depends:
            dependencies.append(d)
            if depends_string == "":
                depends_string = "dependencies=" + d
            else:
                depends_string += " " + d
        if depends_string == "":
            depends_string = None
    else:
        depends_string = None
    return dependencies, depends_string


def get_sos(request):
    sos = []
    try:
        depends = dict(request.POST)['sos']
    except Exception:
        depends = None
    if depends is not None:
        for d in depends:
            sos.append(d)
    return sos


def get_manager(request):
    who = request.POST.get('who')
    chef = None
    pupet = None
    if who == "chef":
        chef = "checked"
    if who == "pupet":
        pupet = "checked"
    return who, chef, pupet


def get_repository(request):
    svn = None
    git = None
    repo = request.POST.get('repo')
    if repo == "git":
        git = "checked"
    if repo == 'svn':
        svn = "checked"
    return svn, git, repo


def is_error(url, svn, git, name, version, sos, chef, pupet):
    err = 0
    my_error = ''
    if url == '':
        if err == 1:
            my_error += ", "
        err = 1
        my_error += "Cookbook URL"
    if (svn is None) and (git is None):
        if err == 1:
            my_error += ", "
        err = 1
        my_error += "Repository"
    if (chef is None) and (pupet is None):
        if err == 1:
            my_error += ", "
        err = 1
        my_error += "Configuration Management "
    if name == '':
        if err == 1:
            my_error += ", "
        err = 1
        my_error += "Name"
    if version == '':
        if err == 1:
            my_error += ", "
        err = 1
        my_error += "Version"

    if len(sos) == 0:
        if err == 1:
            my_error += ", "
        err = 1
        my_error += "Operating Systems"
    return err, my_error
