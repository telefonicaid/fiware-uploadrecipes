def get_token_request(request):
    #token = "12fc35a0d529416da5941e5dd13db4ab"
    #return token
    return request.META.get("HTTP_X_AUTH_TOKEN")


def get_name(root):
    child = None
    exist = False
    for child in root:
        if child.tag == "name":
            exist = True
            break
    if not exist:
        return ''
    return child.text


def get_version(root):
    child = None
    exist = False
    for child in root:
        if child.tag == "version":
            exist = True
            break
    if not exist:
        return ''
    return child.text


def get_cookbook(root):
    exist = False
    child = None
    for child in root:
        if child.tag == "url":
            exist = True
            break
    if not exist:
        return ''
    return child.text


def get_description(root):
    exist = False
    child = None
    for child in root:
        if child.tag == "description":
            exist = True
            break
    if not exist:
        return ''
    return child.text


def get_dependencies(root):
    dependencies = []
    depends_string = ""
    for child in root:
        if child.tag == "dependencies":
            for mych in child:
                #Nombre de la dependencia
                #tambien tenemos la version pero ahora no se usa
                if mych.tag == "name":
                    dependencies.append(mych.text)
                    if depends_string == "":
                        depends_string = "dependencies=" + mych.text
                    else:
                        depends_string += " " + mych.text
    if depends_string == "":
        depends_string = None
    return dependencies, depends_string


def get_sos(root):
    sos = []
    for child in root:
        if child.tag == "sos":
            sos.append(child.text)
    return sos


def get_manager(root):
    child = None
    for child in root:
        if child.tag == "config_management":
            break
    who = child.text
    chef = None
    pupet = None
    if who == "chef":
        chef = "checked"
    if who == "pupet":
        pupet = "checked"
    return who, chef, pupet


def get_repository(root):
    child = None
    for child in root:
        if child.tag == "repository":
            break
    repo = child.text
    svn = None
    git = None
    if repo == "git":
        git = "checked"
    if repo == 'svn':
        svn = "checked"
    return svn, git, repo


def get_ports(root):
    ports = ""
    exist = False
    for child in root:
        if child.tag == "ports" and child.text != "22":
            ports += child.text + " "
            exist = True
    if not exist:
        return ""
    return ports[:-1]


def get_attr(root):
    attr = ""
    for child in root:
        if child.tag == "attr":
            name = child[0].text
            value = child[1].text
            #Hay que ver como meter la descripcion de los attributos
            #description = child[2].text
            attr += name + "=" + value + ";"
    return attr[:-1]
