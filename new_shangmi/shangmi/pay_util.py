# -*- coding: utf-8 -*-
import hashlib
import socket

import datetime
import uuid

import xmltodict


def get_local_ip():
    myname = socket.getfqdn(socket.gethostname())
    myaddr = socket.gethostbyname(myname)
    return myaddr

def sign(params, sign_key):
    params = [(u'%s' % key, u'%s' % val) for key, val in params.iteritems() if val]
    sorted_params_string = '&'.join('='.join(pair) for pair in sorted(params))
    sign_str = '{}&key={}'.format(sorted_params_string.encode('utf-8'), sign_key)
    print("---", sign_str)
    md5 = hashlib.md5()
    md5.update(sign_str)
    return md5.hexdigest().upper()


def create_mch_billno(mch_id):
    now = datetime.datetime.now()
    randuuid = uuid.uuid4()
    mch_billno = '{}{}{}'.format(
        mch_id,
        now.strftime('%Y%m%d'),
        str(randuuid.int)[:10])
    return mch_billno

def xml_response_to_dict(rep):
    d = xmltodict.parse(rep.content)
    return dict(d['xml'])
