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
    centos = request.POST.get('centos')
    ubuntu = request.POST.get('ubuntu')
    sos = []
    if centos is not None:
        centos = "checked"
        sos.append("centos")
    if ubuntu is not None:
        ubuntu = "checked"
        sos.append("ubuntu")
    return sos, centos, ubuntu


def get_installator(request):
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


def is_error(url, svn, git, name, version, centos, ubuntu, chef, pupet):
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

    if (centos is None) and (ubuntu is None):
        if err == 1:
            my_error += ", "
        err = 1
        my_error += "Operating Systems"
    return err, my_error
