from __future__ import with_statement
from fabric.api import *
from fabric.contrib.console import confirm
# globals
# environments
env.hosts = ['redcloud.compute.dtu.dk']
env.user = "s083928"

def dev():
    env.APP_ENV = "dev"

def prod():
    env.APP_ENV = "prod"

from fabric.api import sudo, warn_only

def _force_reset():
    with cd("/home/s083928/redcloud/"):
        run("git fetch")
        run("git reset --hard origin/master")

def _pull():
    with cd("/home/s083928/redcloud/"):
        run("git pull --rebase")

def deploy():
    import time
    print("Executing deploy() on %s as %s, %s" % (env.host, env.user, time.strftime('%Y%m%d%H%M%S')))
    _pull()
    sudo("docker stop redcloud")
    sudo("docker rm redcloud")
    with cd("/home/s083928/redcloud/docServer"):
        #sudo("docker run --name redcloud-postgres -e POSTGRES_PASSWORD=root -p 5430:5432 -d postgres:9.4.1")
        #sudo("docker run --name redcloud-redis -d redis")
        sudo("docker build -t redcloud_server .")
        sudo("docker run -e APPLICATION_ENV=prod --link redcloud-redis:redis --link redcloud-postgres:db --name redcloud -v /srv/redcloud/media:/home/code/media  -p 443:443 -p 80:80 -d redcloud_server")
        sudo("docker tag -f redcloud_server dtured/redcloud_server")
    print("Done with deployment, %s" % (time.strftime('%Y%m%d%H%M%S')))

def init():
    import time
    print("Executing deploy() on %s as %s, %s" % (env.host, env.user, time.strftime('%Y%m%d%H%M%S')))
    _pull()
    sudo("service apache2 stop")
    with cd("/home/s083928/redcloud/docServer"):
        sudo("docker build -t redcloud_server .")
        sudo("docker run -e APPLICATION_ENV=prod --link redcloud-redis:redis --link redcloud-postgres:db --name redcloud -v /srv/redcloud/media:/home/code/media  -p 443:443 -p 80:80 -d redcloud_server")
        sudo("docker tag -f redcloud_server dtured/redcloud_server")
        migrate()
        loaddata()
    print("Done init, %s" % (time.strftime('%Y%m%d%H%M%S')))

def deploy_local():
    import time
    print("Executing deploy() on %s as %s, %s" % (env.host, env.user, time.strftime('%Y%m%d%H%M%S')))
    local("sudo docker stop redcloud-postgres")
    local("sudo docker rm redcloud-postgres")
    local("sudo docker run --name redcloud-postgres -e POSTGRES_PASSWORD=root -p 5430:5432 -d postgres:9.4.1")
    local("sudo docker stop redcloud-redis")
    local("sudo docker rm redcloud-redis")
    local("sudo docker run --name redcloud-redis -d redis")
    local("sudo docker stop redcloud")
    local("sudo docker rm redcloud")
    local("sudo docker build -t redcloud_server .")
    local("sudo docker run -e APPLICATION_ENV=prod --link redcloud-redis:redis --link redcloud-postgres:db --name redcloud -v /srv/redcloud/media:/home/code/media  -p 443:443 -p 80:80 -d redcloud_server")
    local("sudo docker tag -f redcloud_server dtured/redcloud_server")
    print("Done with deployment, %s" % (time.strftime('%Y%m%d%H%M%S')))

def collect_static():
    local("python manage.py collectstatic")

def migrate():
	sudo("docker run -e APPLICATION_ENV=prod --link redcloud-redis:redis --link redcloud-postgres:db -it dtured/redcloud_server:latest python3 manage.py migrate")

def ip():
	sudo("docker inspect redcloud | grep IPAddress | cut -d '\"' -f 4")

def loaddata():
	sudo("docker exec -t redcloud python3 manage.py loaddata init.json")

def dump():
	sudo("docker run -e APPLICATION_ENV=prod --link redcloud-redis:redis --link redcloud-postgres:db -it dtured/redcloud_server:latest python3 manage.py dumpdata --natural --indent=4 -e sessions -e contenttypes -e auth.Permission -e profus -e account > init.json")

def db_reset():
    sudo("docker stop redcloud-postgres")
    sudo("docker rm redcloud-postgres")
    sudo("docker run --name redcloud-postgres -e POSTGRES_PASSWORD=root -p 5430:5432 -d postgres:9.4.1")
    deploy()
    migrate()
    sudo("docker run -e APPLICATION_ENV=prod --link redcloud-redis:redis --link redcloud-postgres:db -it redcloud_server python3 manage.py loaddata init.json")

def build():
	arg = "-e APPLICATION_ENV=" + env.APP_ENV
	if (env.APP_ENV == "prod"):
		arg += " --link redcloud-redis:redis --link redcloud-postgres:db"
	local("sudo docker stop redcloud-postgres")
	local("sudo docker rm redcloud-postgres")
	local("sudo docker run --name redcloud-postgres -e POSTGRES_PASSWORD=root -p 5430:5432 -d postgres:9.4.1")
	local("sudo docker build -t redcloud_server .")
	local("sudo docker stop redcloud_server")
	local("sudo docker rm redcloud_server")
	# local("sudo docker run " + arg + " -it docserver-" + env.APP_ENV + " python3 manage.py migrate")
	# local("sudo docker run " + arg + " -it docserver-" + env.APP_ENV + " python3 manage.py flush")
	# local("sudo docker run " + arg + " -it docserver-" + env.APP_ENV + " python3 manage.py loaddata init.json")
	# local("sudo docker run " + arg + " --name docserver-db-" + env.APP_ENV + " -v /srv/redcloud/media:/home/code/media  -p 443:443 -p 80:80 -d redcloud_server")
	local("sudo docker run --name redcloud_server -v /srv/redcloud/media:/home/code/media -p 443:443 -p 80:80 -d redcloud_server")
	local("sudo docker tag -f redcloud_server dtured/redcloud_server")


def test():
	sudo("docker run -e APPLICATION_ENV=prod --link redcloud-redis:redis --link redcloud-postgres:db dtured/redcloud_server python3 manage.py test bdd_tests")

def connect():
    sudo("docker exec -i -t redcloud bash")

def access_log():
    sudo("docker exec -t redcloud tail -f /var/log/nginx/access.log")

def push(m):
	local("sudo docker commit -m '%s' redcloud_server" % (m))
	local("sudo docker push dtured/redcloud_server")
#     "Use the local virtual server"
#     config.hosts = ['172.16.142.130']
#     config.path = '/path/to/project_name'
#     config.user = 'garethr'
#     config.virtualhost_path = "/"
# # tasks
# def test():
#     "Run the test suite and bail out if it fails"
#     local("cd $(project_name); python manage.py test", fail="abort")
# def setup():
#     """
#     Setup a fresh virtualenv as well as a few useful directories, then run
#     a full deployment
#     """
#     require('hosts', provided_by=[local])
#     require('path')
#     sudo('aptitude install -y python-setuptools')
#     sudo('easy_install pip')
#     sudo('pip install virtualenv')
#     sudo('aptitude install -y apache2')
#     sudo('aptitude install -y libapache2-mod-wsgi')
#     # we want rid of the defult apache config
#     sudo('cd /etc/apache2/sites-available/; a2dissite default;')
#     run('mkdir -p $(path); cd $(path); virtualenv .;')
#     run('cd $(path); mkdir releases; mkdir shared; mkdir packages;', fail='ignore')
#     deploy()
# def deploy():
#     """
#     Deploy the latest version of the site to the servers, install any
#     required third party modules, install the virtual host and 
#     then restart the webserver
#     """
#     require('hosts', provided_by=[local])
#     require('path')
#     import time
#     config.release = time.strftime('%Y%m%d%H%M%S')
#     upload_tar_from_git()
#     install_requirements()
#     install_site()
#     symlink_current_release()
#     migrate()
#     restart_webserver()
# def deploy_version(version):
#     "Specify a specific version to be made live"
#     require('hosts', provided_by=[local])
#     require('path')
#     config.version = version
#     run('cd $(path); rm releases/previous; mv releases/current releases/previous;')
#     run('cd $(path); ln -s $(version) releases/current')
#     restart_webserver()
# def rollback():
#     """
#     Limited rollback capability. Simple loads the previously current
#     version of the code. Rolling back again will swap between the two.
#     """
#     require('hosts', provided_by=[local])
#     require('path')
#     run('cd $(path); mv releases/current releases/_previous;')
#     run('cd $(path); mv releases/previous releases/current;')
#     run('cd $(path); mv releases/_previous releases/previous;')
#     restart_webserver()    
# # Helpers. These are called by other functions rather than directly
# def upload_tar_from_git():
#     require('release', provided_by=[deploy, setup])
#     "Create an archive from the current Git master branch and upload it"
#     local('git archive --format=tar master | gzip > $(release).tar.gz')
#     run('mkdir $(path)/releases/$(release)')
#     put('$(release).tar.gz', '$(path)/packages/')
#     run('cd $(path)/releases/$(release) && tar zxf ../../packages/$(release).tar.gz')
#     local('rm $(release).tar.gz')
# def install_site():
#     "Add the virtualhost file to apache"
#     require('release', provided_by=[deploy, setup])
#     sudo('cd $(path)/releases/$(release); cp $(project_name)$(virtualhost_path)$(project_name) /etc/apache2/sites-available/')
#     sudo('cd /etc/apache2/sites-available/; a2ensite $(project_name)') 
# def install_requirements():
#     "Install the required packages from the requirements file using pip"
#     require('release', provided_by=[deploy, setup])
#     run('cd $(path); pip install -E . -r ./releases/$(release)/requirements.txt')
# def symlink_current_release():
#     "Symlink our current release"
#     require('release', provided_by=[deploy, setup])
#     run('cd $(path); rm releases/previous; mv releases/current releases/previous;', fail='ignore')
#     run('cd $(path); ln -s $(release) releases/current')
# def migrate():
#     "Update the database"
#     require('project_name')
#     run('cd $(path)/releases/current/$(project_name);  ../../../bin/python manage.py syncdb --noinput')
# def restart_webserver():
#     "Restart the web server"
#     sudo('/etc/init.d/apache2 restart')