#!/usr/bin/env python
import os
import re
import math
import ConfigParser
import json
import requests
import pprint

from flask import Flask, render_template, redirect, request, Response, send_from_directory
#import flask

from cmauth import CMAuth, CMAuthOS, CMAuthLDAP, CMIdpNotSupportedError

from functools import wraps, update_wrapper


app = Flask(__name__)
DEBUG = True
app.config.from_object(__name__)
app.debug = True
        
@app.route('/')
def itsworking():
    return 'Flask is working!'

@app.route('/services/pubhelloworld', methods=['GET'])
def pubhelloworld_anon():
    msg = {}
    msg['msg'] = "Hello World Anonymous!"
    resp = Response(response=json.dumps(msg),
                    status=200,
                    mimetype="application/json")
    return resp
       
@app.route('/services/pubhelloworld/<name>', methods=['GET'])
def pubhelloworld(name=None):
    msg = {}
    msg['msg'] = "Hello World %s!" % name
    resp = Response(response=json.dumps(msg),
                    status=200,
                    mimetype="application/json")
    return resp

def fgauth_token(f):
    def impl(*args, **kwargs):
        #print "in decorator def..start.."
        #print request.headers
        if request is None:
            return f(*args, **kwargs)
        else:
            reqheaders = request.headers
            authed = False
            msg = {}
            emsg = ''
            retstatus = 401
            if 'CM-Auth-Provider' in reqheaders:
                idptype = reqheaders['CM-Auth-Provider']
                idpendpoint = reqheaders['CM-Auth-Endpoint']
                token = reqheaders['CM-Auth-Token']

                if idptype in ('LDAP'):
                    if idptype == 'LDAP':
                        authobj = CMAuth()
                        authed = authobj.auth(idptype, idpendpoint, token)
                    if authed:
                        retstatus = 200
                    else:
                        emsg = 'Invalid Token'    
                else:   
                    emsg = "Auth IDP not supported!"
                if emsg != '':
                    msg['error'] = 'Not Authorized - %s' % emsg
            else:
                msg['error'] = 'Not Authorized - Authentication required'

        if retstatus == 200:
            return f(*args, **kwargs)
        else:
            resp = Response(response=json.dumps(msg),
                status=retstatus,
                mimetype="application/json")
            return resp
    return update_wrapper(impl, f)

@app.route('/services/helloworldtest/<name>', methods=['GET'])
@fgauth_token
def helloworldtest(name=None):
    #print "in service url call"
    msg = {}
    msg['msg'] = "Hello World %s!" % name
    resp = Response(response=json.dumps(msg),
                    status=200,
                    mimetype="application/json")
    return resp

@app.route('/services/helloworld/<name>', methods=['GET'])
def helloworld(name=None):
    reqheaders = request.headers
    idptype = reqheaders['CM-Auth-Provider']
    idpendpoint = reqheaders['CM-Auth-Endpoint']
    token = reqheaders['CM-Auth-Token']
    authed = False
    msg = {}
    emsg = ''
    retstatus = 401
    if idptype in ('LDAP'):
        if idptype == 'LDAP':
            authobj = CMAuth()
            authed = authobj.auth(idptype, idpendpoint, token)
        if authed:
            msg['msg'] = "Hello World %s!" % name
            retstatus = 200
        else:
            emsg = 'Invalid Token'    
    else:   
        emsg = "Auth IDP not supported!"
    
    if emsg != '':    
        msg['error'] = 'Not Authorized - %s' % emsg
    resp = Response(response=json.dumps(msg),
                    status=retstatus,
                    mimetype="application/json")
    return resp
        
@app.route('/services/pubpost', methods=['POST'])
def pubpost():
    msg = {}
    if not request.json or not 'name' in request.json:
        msg['error'] = "Expecting data in json format {'name':'foobar'}"
        retstatus = 404
    else:
        msg['msg'] = 'I got your message, %s' % request.json['name']
        retstatus = 200
    resp = Response(response=json.dumps(msg),
                    status=retstatus,
                    mimetype="application/json")
    return resp
    
if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=6088)
    
