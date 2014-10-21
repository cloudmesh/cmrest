#!/usr/bin/env python
import os
import sys
import re
import string
import random
import math
import ConfigParser
import json
import requests
import ldap
import pprint

class CMAuthOS(object):
    def __init__(self, cred):
        self.admin_credential = cred
        self.auth_token = None
        
    def auth(self, cred):
        if not self.auth_token:
            self.auth_token = self.getAdminToken()['access']['token']['id']
        headers = {'X-Auth-Token': self.auth_token}
        endpoint = cred['endpoint']
        token = cred['token']
        url = "%s/tokens/%s" % (endpoint, token)
        #print url
        #print headers
        r = requests.get(url,headers=headers,verify=False).json()
        #pprint.pprint(r)
        if r.has_key('access'):
            ret = True
        else:
            ret = False
        return ret
    
    def getAdminToken(self, credential=None):
        #print "get_token is being invoked"
        if credential is None:
            credential = self.admin_credential
        param = None
        if 'OS_TENANT_NAME' in credential:
            param = {"auth": { "passwordCredentials": {
                                    "username": credential['OS_USERNAME'],
                                    "password": credential['OS_PASSWORD'],
                                },
                               "tenantName":credential['OS_TENANT_NAME']
                            }
                 }
        elif 'OS_TENANT_ID' in credential:
            param = {"auth": { "passwordCredentials": {
                                    "username": credential['OS_USERNAME'],
                                    "password": credential['OS_PASSWORD'],
                                },
                               "tenantId":credential['OS_TENANT_ID']
                            }
                 }
        url = "{0}/tokens".format(credential['OS_AUTH_URL'])

        #print "URL", url

        headers = {'content-type': 'application/json'}

        r = requests.post(url,
                          data=json.dumps(param),
                          headers=headers,
                          verify=False)
        #self.auth_token = r.json()['access']['token']['id']
        return r.json()#['access']['token']['id']

class CMAuthLDAP(object):
    def __init__(self):
        self.host = 'REMOVED'
        self.basedn = 'dc=futuregrid,dc=org'
        self.groupou = 'ou=Groups'
        self.tokenstore = CMTokenStoreRAM()
        
    def getToken(self, username, password):
        userdn = "uid=" + username + ",ou=People,dc=futuregrid,dc=org"
        #print userdn
        ldap.set_option(ldap.OPT_X_TLS_CACERTFILE, os.path.expanduser("~/.futuregrid/FGLdapCacert.pem"))
        ldapconn = ldap.initialize("ldap://" + self.host)
        token = None
        print "Initializing the LDAP connection to server: "
        try:
            ldapconn.start_tls_s()
            print "tls started..."
            ldapconn.bind_s(userdn, password)
            ret = True
        except ldap.INVALID_CREDENTIALS:
            print "%s - username or password is incorrect. Cannot bind." % username
            ret = False
        except ldap.LDAPError:
            print "User %s failed to authenticate due to LDAP error.\nTrace: %s" % (username, str(sys.exc_info()))
            ret = False
        except:
            ret = False
            print "User %s failed to authenticate due to unknown error.\nTrace: %s" % (username, str(sys.exc_info()))
        finally:
            print "Unbinding from the LDAP."
            ldapconn.unbind()
        if ret:
            token = randomToken(size=32)
            self.tokenstore.addToken(username, token)
        return token
    
    def auth(self, token):
        return self.tokenstore.validateToken(token)
        
def randomToken(chars=string.ascii_uppercase + string.digits, size=6):
    return ''.join(random.choice(chars) for x in range(size))

class CMTokenStoreRAM(object):
    def __init__(self):
        self.tokens = {}
    
    def addToken(self, user, token):
        self.tokens[token] = user
    
    def removeToken(self, token):
        self.tokens.pop(token, None)
        
    def validateToken(self, token):
        msg = {'error': 'Invalid token'}
        if token in self.tokens:
            msg = {'user': self.tokens[token]}
        return msg
    
class CMAuth(object):
    def auth(self, idptype, idpendpoint, token):
        ret = False
        print "%s-%s-%s" % (idptype, idpendpoint, token)
        if token=='dummytoken%correct':
            ret = True
        return ret

class CMIdpNotSupportedError(Exception):
    def __init__(self, expr, msg):
        self.expr = expr
        self.msg = msg

if __name__ == '__main__':
    cred = {'OS_AUTH_URL':'URL_REMOVED',
            'OS_PASSWORD': 'REMOVED',
            'OS_TENANT_NAME': 'fgXX',
            'OS_USERNAME': 'REMOVED'
            }
    admincred = {'OS_AUTH_URL':'URL_REMOVED',
            'OS_PASSWORD': 'REMOVED',
            'OS_TENANT_NAME': 'PROJ',
            'OS_USERNAME': 'REMOVED'
            }
    
    keystone = CMAuthOS(admincred)
    token = keystone.getAdminToken()
    #pprint.pprint(token['access']['token']['id'])
    newtoken = keystone.getAdminToken(cred)['access']['token']['id']
    clientcred = {'endpoint':'URL_REMOVED',
                  'token': '%s' % newtoken}
    print keystone.auth(clientcred)
    
    fgldap = CMAuthLDAP()
    username = 'REMOVED'
    password = 'REMOVED'
    fgtoken = fgldap.getToken(username, password)
    print fgtoken
    print fgldap.auth(fgtoken)
    print fgldap.auth('nonexisttoken')
    
