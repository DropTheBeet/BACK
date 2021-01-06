from setuptools import setup, find_packages

install_packages = [
    'flask==1.1.2',
    'flask_script==2.0.6',
    'sqlalchemy==1.3.22',
    'flask-sqlalchemy==2.4.4',
    'flask-cors==3.0.9',
    'mysql-connector-python==8.0.22',
    'jwt==1.1.0',
    'bcrypt==3.2.0',
    'boto3==1.16.47',
    'image==1.5.33'
]

setup(name="drop_the_bit",
      version='0.1',
      description='',
      url='https://github.com/DropTheBeet/BACK',
      author='yg9677',
      author_email='yg9677@gmail.com',
      install_requires=install_packages,
      packages=find_packages(),
      zip_safe=False)

'''
python setup.py install
'''