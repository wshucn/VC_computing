## Python environment Check
- use **python -V** to check your python version is 3.10 or above,if you don't install python, follow the install documents to python.org
- use **virtualenv --version** *o check if you have installed virtualenv. If you don't install this, use **pip install virtualenv** to install it.

## Install Chrome & Chrome driver
- First use **wget https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm** to download chrome for linux version
- Second use **sudo yum install ./google-chrome-stable_current_x86_64.rpm** to install chrome
- After you install successfully , you should link the executable to another path which chrome driver could use. **ln -s /opt/google/chrome/google-chrome /opt/google/chrome/chrome**
- Download and unzip the chrome driver to a custom path. **wget https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/119.0.6045.105/linux64/chromedriver-linux64.zip**. Notice you must config your chrome driver path in **config.ini** file.
> The chrome driver version must adapt your chrome. you could use --version to check your Chrome version

## Create environment Steps
- use **virtualenv my-env** to create a folder named my-env in the current directory.This folder contains the directories for installing modules and Python executables.
> if your virtualenv version is below 20, use **virtualenv --no-site-packages my-env**. The **no-site-packages** to prevent this virtualenv from “seeing” your global Python “site-packages” directory, so that our experiments aren't confused by any Python packages you happen to already have installed globally.
- enter your env with **cd my-env** command
- use **source bin/activate** to enable this virtual environement
- use **pip install -r requirements.txt** to install dependent librarires. 


## Start your service
- check your **config.ini** to make sure you have the correct chrome driver path.
- use **nohup flask --app app run -h 0.0.0.0 &** to start flask service and listen to address 0.0.0.0 , you also could **specify a port with -p argument** to run on special port. Notice you should **open relative port on your security group on aws console.** 
