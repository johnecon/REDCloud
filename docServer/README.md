This django project is deployed using nginx and uwsgi with fab and docker.

# Installation Steps #
```
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

# Connect to Database #
* ssh at redcloud server
```
psql -h localhost -p 5430 -d postgres -U postgres --password
```

# Deployment Steps #
* install [openvpn](https://itswiki.compute.dtu.dk/index.php/OpenVPN)
* connect to vpn using
```
sudo openvpn --config client.conf
```
* if static files (js or css) are modified you need to run
```
python manage.py collectstatic
``` 
* deploy using
```
fab deploy
```
* deploy with migrations using
```
fab deploy migrate
```

# Dump Database #
```
python manage.py dumpdata auth.User docServer --indent=4 --natural --natural-primary --natural-foreign -e contenttypes -e docServer.UserProfile > init.json
```

# Reset Data #
```
python manage.py flush
```

# Load Data From File #
```
python manage.py loaddata init.json
```

# Migrate Database #
* change a model
* generate migration files
```
python manage.py makemigrations
```
* apply migrations
```
python manage.py migrate
```

# Run Integration Tests #
* all tests:
```
python manage.py test bdd_tests --testrunner=django_behave.runner.DjangoBehaveTestSuiteRunner
```
* (wip only):
```
python manage.py test bdd_tests --testrunner=django_behave.runner.DjangoBehaveTestSuiteRunner --behave_tags @wip
```

# Check Error Logs #
```
tail -f /var/log/supervisor/app-uwsgi-stderr---supervisor-UcTG0o.log
tail -f /var/log/nginx/error.log
```

# Restart UWSGI #
```
sudo supervisorctl
restart app-uwsgi
```

# Deploy Server Container #
Use the ServerDockerfile
```
fab prod build
fab push:{message}
```

# Stress testing #
```
ab -k -c 100 -n 1000 -A admin:admin redcloud.compute.dtu.dk/projects/3/load
```

# Backups #
[https://itswiki.compute.dtu.dk/index.php/Backup_on_Linux_/_OSX](https://itswiki.compute.dtu.dk/index.php/Backup_on_Linux_/_OSX)

# Production #
[redcloud.compute.dtu.dk](redcloud.compute.dtu.dk)

# Support #
[johnnyecon@gmail.com](johnnyecon@gmail.com)
