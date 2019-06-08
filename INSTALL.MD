# Installation Instructions
Our long term goal is to simplify this process. If you have tips on how to expedite deployment please let us know.

If you are a beginner user, don't get intimated by this process. Although it uses the command line, it shouldn't be complicated. And you may learn a thing or two.  
#### Choose your path:
 - Quick installation: *Just follow the commands*
- Step-by-Step instructions: *detailed explanations*

# Quick Installation
_This assumes you have Python, pip, virtualenv and git already installed. If you don't, follow the step-by-step guide._

Open Terminal, navigate to where you want to store the CryptoBlotter folder and type the following:
```bash
git clone https://github.com/pxsocs/cryptoblotter.git
cd cryptoblotter
virtualenv cb_env
source cb_env/bin/activate
pip install -r requirements.txt
```
Then setup the environment variables. The ones below are suggestions. You should probably change them (see instructions in the detailed step-by-step installation).

Still at the terminal window type:
```bash
export ALPHAVANTAGE_API_KEY=YUI9BS0MIBOPWRVR
export SECRET_KEY=44600d69123eb71e1338e47587fec5fb
export SQLALCHEMY_DATABASE_URI=sqlite:///alpha.db
```
To start the application just execute:
```bash
python run.py
```
Finally, open a browser window and navigate to:
[http://127.0.0.1:5000/](http://127.0.0.1:5000/)

To exit just hit <kbd>ctrl</kbd>+<kbd>c</kbd> at the terminal window.

Done!

# Step-by-Step Instructions

## Mac OS/X
#### Step 1 - Create a folder to store the source code
  * Open Terminal (press &#x2318; + <kbd>spacebar</kbd>, then type `terminal`&#x23ce;)

  * At the terminal window, create a folder to store the source code. _`~/git_clones/` is the default but feel free to change this to your preferred folder and location._
  ```
  $ mkdir ~\git_clones
  $ cd ~\git_clones
  ```

#### Step 2 - Install Git command line (skip if installed)
  * check if git is already installed:
  ```
  $ git --status
  ```
  If you don't have Git installed, MacOs will prompt you to install.
  Click **Install** and follow the instructions.

  If the process above fails, try downloading Git [here](https://git-scm.com/download/mac) and follow the installation instructions.

#### Step 3 - Download the source code
```
$ git clone https://github.com/pxsocs/cryptoblotter.git
```
This will create a folder named `cryptoblotter` and store the source code there.
Now you can review and modify the code freely. We recommend [Atom Editor](https://atom.io/) as a good alternative but feel free to use whatever you prefer.

#### Step 4 - Make sure you have Python 3.6 or higher installed (skip if installed)

Make sure you have Python and that the expected version is available from your command line. You can check this by running:

`$ python --version`

You should get some output like  `Python 3.6.3`. If you do not have Python, please install the latest 3.x version from  [python.org](https://python.org/)  or refer to the  [Installing Python](http://docs.python-guide.org/en/latest/starting/installation/)  section of the Hitchhiker’s Guide to Python.

#### Step 5 - Ensure you can run `pip` (skip if pip is installed)

Pip manages Python's libraries. These are like add-ins.  You can check if it's installed by running:

`$ pip --version`

If you installed Python from source, with an installer from  [python.org](https://python.org/), or via  [Homebrew](https://brew.sh/)you should already have pip. If you’re on Linux and installed using your OS package manager, you may have to install pip separately, see  [Installing pip/setuptools/wheel with Linux Package Managers](https://packaging.python.org/guides/installing-using-linux-tools/).

If  `pip`  isn’t already installed, then first try to bootstrap it from the standard library:

python -m ensurepip --default-pip

If that still doesn’t allow you to run  `pip`:

> -   Securely Download  [get-pip.py](https://bootstrap.pypa.io/get-pip.py)  [[1]](https://packaging.python.org/tutorials/installing-packages/#id7)
>     
> -   Run  `python  get-pip.py`.  [[2]](https://packaging.python.org/tutorials/installing-packages/#id8)  This will install or upgrade pip. Additionally, it will install  [setuptools](https://packaging.python.org/key_projects/#setuptools)  and  [wheel](https://packaging.python.org/key_projects/#wheel)  if they’re not installed already.

#### Step 6 - Create a virtual environment

#### Install the virtualenv package

The virtualenv package is required to create virtual environments. You can install it with pip:

```bash
$ pip install virtualenv
```

#### Create the virtual environment

To create a virtual environment, you must specify a path. For example to create one in the local directory called ‘mypython’, type the following:

```bash
$ virtualenv cb_env
```

#### Activate the virtual environment

You can activate the python environment by running the following command:
```bash
$ source cb_env/bin/activate
```
You should see the name of your virtual environment in brackets on your terminal line e.g. (cb_env).

Later, to deactivate the virtual environment and use your original Python environment, simply type ‘deactivate’.
```bash
$ deactivate
```
#### Step 7 - Install the PIP packages
The list of required packages is stored on a file named `requirements.txt`. To install all the packages just type at the terminal:
`$ pip install -r requirements.txt`

#### Step 8 - Declare environment variables
Cryptoblotter will look for a few environment variables before running. You need to set these up only once. These are:

__Database Location__
This is default and no need to change unless you want to use a different database than the one already provided. Type:
`$ export SQLALCHEMY_DATABASE_URI=sqlite:///alpha.db`

__Alphavantage API Key__
Cryptoblotter uses Alphavantage to download pricing data. An API key is needed to use Alphavantage - [get one here](https://www.alphavantage.co/support/#api-key). It's super easy and quick.
When done, you can replace the _YUI9BS0MIBOPWRVR_ key below with your own and type at Terminal:
`$ export ALPHAVANTAGE_API_KEY=YUI9BS0MIBOPWRVR`

__Secret Key__
You should generate your own key. This is used to encrypt your data.
To generate a random key:
```bash
$ python
```
	Python 3.7.3 (v3.7.3:ef4ec6ed12, Mar 25 2019, 16:39:00)**
	[GCC 4.2.1 (Apple Inc. build 5666) (dot 3)] on darwin**
	Type "help", "copyright", "credits" or "license" for more
	information.

```bash
>>> import secrets
>>> secrets.token_hex(16)
   44600d69123eb71e1338e47587fec5fb
>>> exit()
```
Then copy the generated secret above and type at the Terminal, replacing with your own secret key:

`$ export SECRET_KEY=44600d69123eb71e1338e47587fec5fb`

#### Step 9 - Start the application
To start the application just execute:
```bash
python run.py
```
Finally, open a browser window and navigate to:
[http://127.0.0.1:5000/](http://127.0.0.1:5000/)

To exit just hit <kbd>ctrl</kbd>+<kbd>c</kbd> at the terminal window.

Done!
