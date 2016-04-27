## Deploying the Order Quality Tool
This guide will take you through the process of installing the tool on a server 
running Ubuntu Trusty 14.04.
There is a an ansible playbook available to automate this entire process. You can view the playbook [here](./deploy.yml).

### Recommended Server Specifications
* 4GB Ram
* Ubuntu Trusty 14.04

### Installation Steps
* Create a user account for the application

		sudo adduser
* Setup apt source for nodejs 

		sudo apt-get update
		sudo apt-get install curl
		curl -sL https://deb.nodesource.com/setup_5.x | sudo -E bash -
		
* Install required packages
	
		sudo apt-get update
		sudo apt-get install postgresql-9.3, postgresql-client-9.3,  postgresql-contrib-9.3 git libpq-dev, build-essential, python-pip, python-dev, supervisor, redis-server, nginx, nodejs
		
* Create a database and user
		
		sudo su postgres
		createuser qdb
		createdb qdb

* Checkout the code to a folder

		mkdir -p /src/qdb
		git clone https://github.com/CHAIUganda/OrderQualityTool.git /src/qdb

* Install the python dependencies

		cd /src/qdb
		pip install -r requirements.txt
		
* Install bower dependencies
		
		npm install -g bower
		cd /src/qdb
		bower install

* Create local settings file
			
  * Create a file at the path /src/qdb/orderqualitytool/local_settings.py, the file should look like
  
	  		DEBUG = False
			DATABASES = {
			    'default': {
			        'ENGINE': 'django.db.backends.postgresql_psycopg2',
			        'NAME': 'qdb',
			        'USER': 'qdb',
			        'PASSWORD': 'qdb',
			        'HOST': '',
			        'PORT': ''
			    }
			}
			ALLOWED_HOSTS = ['*']
			BROKER_URL = 'redis://localhost:6379/0'
			CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
			MEDIA_ROOT = "/media/"
	
	Feel free to change the values to reflect your database connection settings
	
* Run the migrations and setup the static files

		cd /src/qdb
		python manage.py migrate
		python manage.py collectstatic --noinput
		
* Setup the application server and worker processes with supervisor

	* Setup the celery process, create a file at the path /etc/supervisor/conf.d/celery.conf with contents:

			[program:qdb_worker]
			command=celery -A orderqualitytool.celery worker --concurrency=3
			directory=/src/qdb
			autostart=true
			autorestart=true
			stderr_logfile=/var/log/qdb_worker.err.log
			stdout_logfile=/var/log/qdb_worker.out.log
			user=qdb
	* Setup the gunicorn process, create a file at the path /etc/supervisor/conf.d/gunicorn.conf with contents:

			[program:qdb_app_server]
			command=gunicorn orderqualitytool.wsgi:application -w 2 -b :5000
			directory=/src/qdb
			autostart=true
			autorestart=true
			stderr_logfile=/var/log/qdb_app_server.err.log
			stdout_logfile=/var/log/qdb_app_server.out.log
			user=qdb
	* Reload the supervisor config
			
			sudo supervisorctl reload
	
* Setup nginx webserver
	* Change nginx webserver config, change the settings file /etc/nginx/nginx.conf to match the contents below:(mainly the client_max_body_size and the Gzip settings)
		
		
			user www-data;
			worker_processes 4;
			pid /run/nginx.pid;
			events {
				worker_connections 768;
				# multi_accept on;
			}
			
			http {
			
				##
				# Basic Settings
				##
			
				sendfile on;
				tcp_nopush on;
				tcp_nodelay on;
				keepalive_timeout 65;
				types_hash_max_size 2048;
			   client_max_body_size 100M;
				# server_tokens off;
			
				# server_names_hash_bucket_size 64;
				# server_name_in_redirect off;
			
				include /etc/nginx/mime.types;
				default_type application/octet-stream;
			
				##
				# Logging Settings
				##
			
				access_log /var/log/nginx/access.log;
				error_log /var/log/nginx/error.log;
			
				##
				# Gzip Settings
				##
			
				gzip on;
				gzip_disable "msie6";
			
				gzip_vary on;
				gzip_proxied any;
				gzip_comp_level 6;
				gzip_buffers 16 8k;
				# gzip_http_version 1.1;
				gzip_types text/plain text/css application/json application/x-javascript text/xml application/xml application/xml+rss text/javascript;
			
			
			
				include /etc/nginx/conf.d/*.conf;
				include /etc/nginx/sites-enabled/*;
			}

	* Disable the default nginx site
			
			sudo rm /etc/nginx/sites-enabled/default
	
	* Create an nginx site for the tool at the path /etc/nginx/sites-enabled/qdb.conf and updates the contents to:
			
			server {
			  listen   80;
			  location / {
			    proxy_set_header X-Real-IP  $remote_addr;
			    proxy_set_header X-Forwarded-For $remote_addr;
			    proxy_set_header Host $host;
			    proxy_pass http://127.0.0.1:5000;
			  }
			  location /static {
			    alias   /src/qdb/asset_files;
			  }
			}
	
	* Reload nginx

			sudo service nginx reload
			



`If all these steps work the application should be available on port 80 on the server`

			

