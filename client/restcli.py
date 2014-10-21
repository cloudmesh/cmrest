#!/usr/bin/env python
import os
import requests
import json

HEADER = {'content-type': 'application/json'}
HEADERSEC = {'CM-Auth-Token': 'dummytoken%correct', 'CM-Auth-Provider': 'LDAP', 'CM-Auth-Endpoint': 'FG LDAP', 'content-type': 'application/json'}

def pubhelloworld(baseurl):
    apiurl = "%s/pubhelloworld" % baseurl
    return do_get(apiurl)

def helloworld(baseurl,name):
    apiurl = "%s/helloworld/%s" % (baseurl, name)
    return do_secure_get(apiurl)

def helloworldtest(baseurl,name):
    apiurl = "%s/helloworldtest/%s" % (baseurl, name)
    return do_secure_get(apiurl)

def helloworldtestfail(baseurl,name):
    apiurl = "%s/helloworldtest/%s" % (baseurl, name)
    return do_get(apiurl)
             
def pubhelloworld_by_name(baseurl,name):
    apiurl = "%s/pubhelloworld/%s" % (baseurl, name)
    return do_get(apiurl)
    
def pub_post(baseurl,msg):
    apiurl = "%s/pubpost" % baseurl
    data = {'name':msg}
    return do_post(apiurl,data)

def pub_post_wrong(baseurl,msg):
    apiurl = "%s/pubpost" % baseurl
    data = {'unknown_key':msg}
    return do_post(apiurl,data)
        
def do_get(url,header=HEADER,verify=None,injson=True):
    print url
    r = requests.get(url, headers=header, verify=verify)
    if injson:
        r = r.json()
    return r
 
def do_secure_get(url,header=HEADERSEC,verify=None,injson=True):
    print "in secure get..."
    #print header
    return do_get(url,header=header,verify=verify,injson=injson)
    
def do_post(url,data,header=HEADER,verify=None,injson=True):
    print url
    r = requests.post(url, data=json.dumps(data), headers=header, verify=verify )
    content = r.text
    if content and injson:
        content = r.json()
    return content

def main():
    baseurl = "http://localhost:6088/services"
    print pubhelloworld(baseurl)
    print pubhelloworld_by_name(baseurl,'kevin')
    print pub_post(baseurl,'wang')
    print pub_post_wrong(baseurl,'wang')
    print "*"*80
    print "These should pass.."
    print helloworld(baseurl, 'KEVIN')
    print helloworldtest(baseurl, 'KEVIN')
    print "*"*40
    print "This should fail.."
    print helloworldtestfail(baseurl, 'KEVIN')
    
if __name__ == '__main__':
    main()
