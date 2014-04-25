xifi-uploadrecipes
==================

Django application to automatically test new recipes to be incorporate in
the SDC component.


Prepare the server
------------------
1. Use a base image with a chef client correctly configured:

        http://wikis.hi.inet/boi/index.php/Configuracion_de_imagenes

2. The node should be configured as a admin. Execute into the chef-server:

        export EDITOR=$(which vi)
        knife client edit <node_name>

   Change admin as true.

3. Into the some files must be created or changed:

        /root/.chef/knife.rb:

        log_level                :info
        log_location             STDOUT
        node_name                'softwaretester.novalocal'
        client_key               '/etc/chef/client.pem'
        validation_client_name   'chef-validator'
        validation_key           '/etc/chef/validator.pem'
        chef_server_url          'https://130.206.81.105'

4. Install python and django

        wget http://python.org/ftp/python/2.7.6/Python-2.7.6.tgz
        tar -xvf Python-2.7.6.tgz
        cd Python-2.7.6/
        ./configure PREFIX=$SOMEBASE/python-2.7.6
        ./configure --prefix=/wherever/python-2.7.6
        make
        ./configure
        apt-get install build-essential libreadline-gplv2-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev subversion
        ./configure
        make
        make altinstall
        vi get.pip.py  #El fcihero está en https://raw.github.com/pypa/pip/master/contrib/get-pip.py
        python get.pip.py
        apt-get install python-pip
        pip install Django
        pip install mockito
        pip install python-keystoneclient

5. It's necessary install some python modules:
    These are some ways to install it. You should choose which work into your operating system.

        pip install PySvn
        apt-get install subversion python-svn
        pip install PyGit
        pip install PyChef
        apt-get install python-paramkio

6. In the properties.txt file you have

To run the server
-----------------
    python manage.py runserver 0.0.0.0:8000 &

    Actualmente la maquina esta en el portal de la 61, en el tenant tidcloud.
    Usuario propietario beatriz.munoz, y con IP 130.206.81.66.

    Las peticiones por tanto se realizar'an a la direcci'on:
    http://130.206.81.66:8000/

    Se utiliza autenticaci'on con cabeceras (con en el resto de casos)

