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
	sudo("docker exec -t redcloud python3 manage.py dumpdata --natural --indent=4 -e sessions -e contenttypes -e auth.Permission -e profus -e account > init.json")

def db_reset():
    sudo("docker stop redcloud-postgres")
    sudo("docker rm redcloud-postgres")
    sudo("docker run --name redcloud-postgres -e POSTGRES_PASSWORD=root -p 5430:5432 -d postgres:9.4.1")
    deploy()
    migrate()
    sudo("docker exec -t redcloud python3 manage.py loaddata init.json")

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
	local("sudo docker run --name redcloud_server -v /srv/redcloud/media:/home/code/media -p 443:443 -p 80:80 -d redcloud_server")
	local("sudo docker tag -f redcloud_server dtured/redcloud_server")

def connect():
    sudo("docker exec -i -t redcloud bash")

def access_log():
    sudo("docker exec -t redcloud tail -f /var/log/nginx/access.log")

def push(m):
	local("sudo docker commit -m '%s' redcloud_server" % (m))
	local("sudo docker push dtured/redcloud_server")
