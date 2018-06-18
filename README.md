Package Needed :

Python
Python-pam
libpam-python
cryptsetup
dosfstools


How to use :

Put the file 'pamela.py' in /lib/security.
Add at the end of the file of /etc/pam.d/login:
auth sufficient pam_python.so /lib/security/pamela.py
And modify auth optional pam_faildelay.so nodelay
Modify /etc/login.defs the line with umaks to 002
Add user into /lib/security/account and adduser partitions user
All data is in /home/
