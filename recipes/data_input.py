def get_token_request(request):
    """
    Obtain the token from the headers
    @param request: Request.
    @return: token
    """
    return request.META.get("HTTP_X_AUTH_TOKEN")


def get_name(root):
    """
    Obtain the software name
    @param root: request xml body
    @return: the software name
    """
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
    """
    Obtain the software version
    @param root: request xml body
    @return: the software version
    """
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
    """
    Obtain the software repository url
    @param root: request xml body
    @return: the software repository url
    """
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
    """
    Obtain the software description
    @param root: request xml body
    @return: the software description
    """
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
    """
    Obtain the dependencies necessaries for the software
    @param root: request xml body
    @return: the dependencies necessaries for the software
    """
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
    """
    Obtain the images where the software must work
    @param root: request xml body
    @return: list of the images where the software must work
    """
    sos = []
    for child in root:
        if child.tag == "sos":
            sos.append(child.text)
    return sos


def get_manager(root):
    """
    Obtain the configuration management
    @param root: request xml body
    @return: the configuration management
    """
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
    """
    Obtain the kind of repository
    @param root: request xml body
    @return: the kind of repository
    """
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


def get_ports(root, my_tag):
    """
    Obtain the open ports
    @param my_tag: type of ports (udp, tcp...)
    @param root: request xml body
    @return: the open ports string
    """
    ports = ""
    exist = False
    for child in root:
        if child.tag == my_tag and child.text != "22":
            ports += child.text + " "
            exist = True
    if not exist:
        return ""
    return ports[:-1]


def get_attr(root):
    """
    Obtain the attributes necessary to run the software
    @param root: request xml body
    @return: a string with the attributes necessary to run the software
    """
    attr = ""
    for child in root:
        if child.tag == "attr":
            name = child[0].text
            value = child[1].text
            try:
                description = child[2].text
            except Exception:
                description = ""
            attr += name + "=" + value + "," + description + ";"
    return attr[:-1]
