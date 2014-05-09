VOER Platform - Repository Component
=======
This is the repository component of the VOER Platform, which provides services for storing/getting/searching materials.

A - Install using Vagrant
--------------------

Before starting with this approach, ensure that you have [Vagrant](http://www.vagrantup.com/downloads.html) installed.

1. **Download all files** inside [`vp.repo/vagrant/`](https://github.com/voer-platform/vp.repo/tree/master/vagrant) directory to a new local directory (e.g. 'vpr')

2. **Initialize and run Vagrant** inside the local directory

    ```
    vagrant up
    ```
    
3. **After huge number of steps running, the site would be ready to serve at address**

    ```
    http://127.0.0.1:8080
    ```

B - Typical Installation
------------------------

1. **Pre-requisites**

    ```
    Python 2.5 to 2.7
    MySQL or PostgreSQL
    
    ```

2. **Install some additional packages (these below commands are for Debian environment with MariaDB)**

    ```
    apt-get install python-virtualenv python-dev mariadbserver libmariadbclient-dev git
    ```

3. **Create database**
    
    ```
    Name: vpr
    User: vpr
    Password: vpr
    ```

4. **Create & activate separate environment**

    ```
    virtualenv vpr
    cd vpr
    source vpr/activate
    ```

5. **Clone the VPR repository from GitHub, using `git`**

    ```
    git clone git://github.com/voer-platform/vp.repo.git
    ```
    
6. **Go to the `vp.repo/` directory, and run the script `install.sh`**
    
    ```
    cd vp.repo/
    bash ./install.sh
    ```
    
7. **Configure the database running with component, inside:**
    
    ```
    vp.repo/vpr/vpr/settings/dev.py    # Development instance
    vp.repo/vpr/vpr/settings/prod.py   # Production instance
    ```

8. **Initialize DB structure**

    ```
    python ./manage.py syncdb
    ```

9. **Running Component**

    ```
    python ./manage.py runserver
    ```
    
