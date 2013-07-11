Tulip examples
==============

First install Python 3.3.x:

wget http://www.python.org/ftp/python/3.3.1/Python-3.3.1.tar.xz
tar xvf Python-3.3.1.tar.xz
cd Python-3.3.1
./configure
make
make install

Python 3 will be installed in /usr/local/bin/python3

Full instructions can be found at http://askubuntu.com/questions/244544/how-to-install-python-3-3.


Create a virtualenv for Python 3:

  mkvirtualenv py3 --python=/usr/local/bin/python3

Tulip is not yet in the Cheeseshop. Install it directly from its repository:

  pip install hg+https://code.google.com/p/tulip/  <- why doesn't this work?

  pip install -e hg+https://tulip.googlecode.com/hg/#egg=tulip

  pip install -e git+https://github.com/twisted/twisted.git#egg=Twisted


Todo
====
- two tasks downloading from a common queue

