"# foodapp" 
Always run activate virtual enviroment by running from Git bash
source appenv/scripts/activate

if you dont run the the collectstatic command on PROD; static files will not work;
python manage.py collectstatic

#for locale install

sudo apt-get install language-pack-en-base

sudo dpkg-reconfigure locales