cmrest
======


LDAP on OSX
-------------------------------------------------------------

In case you have used LDAP before make sure to make a backup of the
file in `/etc/openldap/slapd.conf`

create SHA passwd::

  slappasswd -s YOURPASSWORD

Copy the file slapd.conf file::

	cp ./slapd.conf /etc/openldap/slapd.conf

Edit the file and adapt. e.g. put the password in the password
location. copy everyying including the {SSHA}

Start the server with::

	cd /etc/openldap
	/usr/libexec/slapd -d 255


ldapadd -x -D "cn=Manager,dc=mycloudmesh,dc=org" -f users.ldif -W

ldapdelete -x -D "cn=Manager,dc=mycloudmesh,dc=org"  -W "cn=Fugang Wang,ou=people,dc=mycloudmesh,dc=org"

ldapsearch -D "cn=Manager,dc=mycloudmesh,dc=org" -W -b "dc=mycloudmesh,dc=org" -s sub "(objectclass=*)"



python server/restapp.py



python client/restcli.py



echo -n password | shasum -a 1 | awk '{print toupper($1)}'


https://community.openproject.org/projects/openproject/wiki/Setting_up_an_OpenLDAP_server_for_testing
