"""
This script runs the FlaskWebProject application using a development server.
"""

from os import environ
from FlaskWebProject import app

if __name__ == '__main__':
    HOST = environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(environ.get('SERVER_PORT', '5556'))
    except ValueError:
        PORT = 5556
    app.run(HOST, PORT)

view.py

#!/usr/bin/env python
import os
from flask import current_app, Flask, redirect, url_for, flash
from pymongo import MongoClient
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from bson.binary import Binary
import gridfs
import base64
import sys
from FlaskWebProject import app

# database connection
def db_conn():
    client = MongoClient("")
    db = client.mydatabase
    collection = db.user
    return db

print("connected")


@app.route('/', methods=['POST', 'GET'])
def run():
    return render_template('first.html')



@app.route('/register',methods=['POST', 'GET'])
def register():

    print("inside new user")
    db=db_conn()
    print(db)
    username = request.form['username']
    password = request.form['password']

    var={
        'username':username,
        'password':password
    }
    db.user.insert(var)
    output = """<h1> Sucessfully inserted, go back to login</h1>"""
    return output

@app.route('/login',methods=['POST', 'GET'])
def login():
    global usern
    db = db_conn()
    print ("inside login")

    username = request.form['user']
    password = request.form['pass']
    count = db.user.find({'username': username, 'password':password}).count()>0
    print(count)
    usern=username
    if count:
        text1="successfully logged in"
        return render_template("loginoutput.html",text=text1)
    else:
        text="username/password mismatch"

        output1="""<h1>%s</h1>"""%(text)
        return output1

@app.route('/uploadimage',methods=['POST', 'GET'])
def uploadimage():
    global usern
    db = db_conn()
    try:
        out = "Successfully uploaded image!!"
        image_file = request.files['pic']
        #text_file=request.files['file']
        #print(text_file)
        #text=text_file.read()
        #print(text)
        print(image_file.filename)
        file_name = image_file.filename
        #text_file1=text_file.filename
        target = image_file.read()
        size=len(target)
        comm = request.form['comments']
        pri =  request.form ['priority']
        print(size)
        count = 0
        for item in db.fs.files.find({"user":usern}):
            print(item)
            count += 1
            print(count)
        if size<5000000:
            if count<100:
                # encoded_string=base64.b64encode(target)
                print ("inside if")
                fs = gridfs.GridFS(db)
                stored = fs.put(target, filename=file_name, user=usern, comment=comm,file_type="image", priority=pri)
                #stored1 = fs.put(text,filename=text_file1)
                print stored
            else:
                raise ValueError('count crossed')
        else:
            raise ValueError('size crossed')

    except:
        out = "upload failed"

    return render_template("insert.html", output=out)

@app.route('/uploadtext',methods=['POST', 'GET'])
def uploadtext():
    global usern
    db = db_conn()
    try:
        out = "Successfully uploaded text file!!"
        text_file=request.files['file']
        print(text_file)
        text=text_file.read()
        print(text)
        file_name = text_file.filename
        print file_name
        #size=len(text)
        comm = request.form['comments']
        pri = request.form['priority']
        #print(size)
        count = 0
        for item in db.fs.files.find({"user":usern}):
            print(item)
            count += 1
            print(count)
        if count<100:
            # encoded_string=base64.b64encode(target)
            print ("inside if")
            fs = gridfs.GridFS(db)
            stored = fs.put(text, filename=file_name, user=usern, comment=comm,file_type="text", priority=pri)
            #stored1 = fs.put(text,filename=text_file1)
            print(stored)
        else:
            raise ValueError('count crossed')

    except ValueError as e:
        out = e

    return render_template("insert.html", output=out)

@app.route('/fetchmine', methods=['POST', 'GET'])
def fetchmine():
    db = db_conn()
    fs = gridfs.GridFS(db)
    diclist = []
    global text

    for item in db.fs.files.find({"user":usern}):
        com = None
        date= None
        file_name = item['filename']
        textfile_name=item['filename']
        file_type = item['file_type']
        priority = item['priority']


        print("getting text file name")
        print(textfile_name)
        print priority
        if 'comment' in item.keys():
            com = item['comment']
        if 'uploadDate' in item.keys():
            date = item['uploadDate']
        if file_type == "image":
            picture = fs.find_one({"filename": file_name}).read()
            data = "data:image/jpeg;base64," + base64.b64encode(picture)
        if file_type == "text":
            data=fs.find_one({"filename": textfile_name}).read()

        dicvar = {}
        dicvar['file_type'] = file_type
        dicvar['file_name'] = file_name
        dicvar['uploadDate'] = date
        dicvar['com'] = com
        dicvar['image'] = data
        dicvar['priority'] = priority
        # print dicvar
        diclist.append(dicvar)
        # print diclist

    return render_template("display.html",lists=diclist)

@app.route('/fetch', methods=['POST', 'GET'])
def fetch():
    global usern
    db = db_conn()
    fs = gridfs.GridFS(db)

    diclist=[]


    for item in db.fs.files.find():
        com = None
        user_name = None
        file_name=item['filename']
        file_type=item['file_type']
        priority = item['priority']
        if 'user' in item.keys():
            user_name=item['user']
        if 'comment' in item.keys():
            com=item['comment']
        if 'uploadDate' in item.keys():
            date = item['uploadDate']
        if file_type=="image":
            picture=fs.find_one({"filename" : file_name }).read()
            data="data:image/jpeg;base64," + base64.b64encode(picture)

        if file_type=="text":
            data=fs.find_one({"filename" : file_name }).read()
        dicvar={}
        dicvar['file_type']=file_type
        dicvar['user']=user_name
        dicvar['file_name']=file_name
        dicvar['com']=com
        dicvar['uploadDate'] = date
        dicvar['image']=data
        dicvar['priority'] =  priority
        print data
        # print dicvar
        diclist.append(dicvar)
        # print diclist

    return render_template("displayall.html", lists=diclist)


@app.route('/delete', methods=['POST', 'GET'])
def delete():
    global usern
    db = db_conn()
    name=request.form['images']
    c = db.fs.files
    try:
        print("going inside try")
        c.delete_one({"filename": name})
        return redirect(url_for('fetchmine'))
    except:
        return "could not delete"
