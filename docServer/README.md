# INSTALLATION STEPS #
```
cd docServer
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

# CONNECT TO DATABASE #
* ssh at redcloud server
```
psql -h localhost -p 5430 -d postgres -U postgres --password
```

# DEPLOYMENT STEPS #
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
fab prod deploy
```
* deploy with migrations using
```
fab prod deploy migrations
```

# DUMP DATABASE INTO A FILE #
```
python manage.py dumpdata auth.User docServer --indent=4 --natural --natural-primary --natural-foreign -e contenttypes -e docServer.UserProfile > init.json
```

# RESET DATA #
```
python manage.py flush
```

# LOAD DATA FROM FILE #
```
python manage.py loaddata init.json
```

# MIGRATE DATABASE #
* change a model
* generate migration files
```
python manage.py makemigrations
```
* apply migrations
```
python manage.py migrate
```

# ROLLBACK MIGRATION #
```
python manage.py docServer migrate {migration_file_name}
```

# RUN INTEGRATION TESTS #
* all tests:
```
python manage.py test bdd_tests --testrunner=django_behave.runner.DjangoBehaveTestSuiteRunner
```
* (wip only):
```
python manage.py test bdd_tests --testrunner=django_behave.runner.DjangoBehaveTestSuiteRunner --behave_tags @wip
```

# CHECK ERROR LOGS #
```
tail -f /var/log/supervisor/app-uwsgi-stderr---supervisor-UcTG0o.log
tail -f /var/log/nginx/error.log
```

# RESTART UWSGI #
```
sudo supervisorctl
restart app-uwsgi
```

# DEPLOY SERVER CONTAINER #
Use the ServerDockerfile
```
fab prod build
fab prod push:{message}
```

# STRESS TESTING #
```
ab -k -c 100 -n 1000 -A admin:admin redcloud.compute.dtu.dk/projects/3/load
```

# BACKUPS #
[https://itswiki.compute.dtu.dk/index.php/Backup_on_Linux_/_OSX](https://itswiki.compute.dtu.dk/index.php/Backup_on_Linux_/_OSX)

# PRODUCTION #
[redcloud.compute.dtu.dk](redcloud.compute.dtu.dk)

# SUPPORT #
[johnnyecon@gmail.com](johnnyecon@gmail.com)
