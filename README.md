VOER Platform - Repository Component
=======
This is the repository component of the VOER Platform, which provides services for storing/getting/searching materials.

Installation
------------

* Pre-requisites

    ```
    Python 2.5 to 2.7
    MySQL or PostgreSQL
    
    ```
    
* Create database:
    
    ```
    Name: vpr
    User: vpr
    Password: vpr
    ```

* Create & activate separate environment

    ```
    virtualenv vpr
    cd vpr
    source vpr/activate
    ```

* Clone the VPR repository from GitHub, using `git`

    ```
    git clone git://github.com/voer-platform/vp.repo.git
    ```
    
* Go to the `vp.repo/` directory, and run the script `install.sh`
    
    ```
    cd vp.repo/
    bash ./install.sh
    ```
    
* Configure the database running with component, inside:
    
    ```
    vp.repo/vpr/vpr/settings/dev.py    # Development instance
    vp.repo/vpr/vpr/settings/prod.py   # Production instance
    ```

* Initialize DB structure:

    ```
    python ./manage.py syncdb
    ```

Running Component
-----------------

* Go to the 'vp.repo/vpr/' directory, and run the Python script:
    
    ```
    python ./manage.py runserver
    ```
    
