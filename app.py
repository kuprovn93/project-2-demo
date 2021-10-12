import os
from flask import Flask, render_template,request,flash,redirect,url_for,session
from spotifyAPI import get_artist, get_song, get_songs
from geniusAPI import get_lyric_link, get_artist_info
import sqlite3
import random

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.secret_key="tnguyen410"

con=sqlite3.connect("database.db")
con.execute("CREATE TABLE IF NOT EXISTS users(id integer primary key, username text unique, password text, email text)")
con.execute("CREATE TABLE IF NOT EXISTS artists(id integer primary key, artistID text, user text)")
con.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login',methods=["GET","POST"])
def login():
    if request.method=='POST':
        uname=request.form['name']
        password=request.form['password']
        con=sqlite3.connect("database.db")
        con.row_factory=sqlite3.Row
        cur=con.cursor()
        cur.execute("SELECT * FROM users WHERE username=? AND password=?",(uname,password))
        data=cur.fetchone()

        if data:
            session["name"]=data["username"]
            session["password"]=data["password"]
            return redirect("home")
        else:
            flash("Username and Password Mismatch","danger")
    return redirect(url_for("index"))


@app.route('/home',methods=["GET","POST"])
def home():
    uname=session["name"]
    con=sqlite3.connect("database.db")
    con.row_factory=sqlite3.Row
    cur=con.cursor()
    
    for row in cur.execute("SELECT artistID FROM artists WHERE user=?",(uname,)):
        a = random.randint(1,len(row))
        data = row[a-1]
    if data:
        text = data
        return redirect(url_for('random_song',artist_name=text))
    else:
        flash("Please save some artists!","info")
        text = "Anna Marie" ##set default artist ID
        return redirect(url_for('random_song',artist_name=text))            

@app.route('/save',methods=["GET","POST"])         
def save():
    ##Save artists
    if request.method=='POST':
        try:
            aname=request.form['artistID']
            uname=session["name"]
            con=sqlite3.connect("database.db")
            con.row_factory=sqlite3.Row
            cur=con.cursor()
            
            cur.execute("INSERT INTO artists(artistID,user)VALUES(?,?)",(aname,uname))
            con.commit()
            flash("Artist saved successfully","success")

        except:
            flash("Error, Failed to save artist!","danger")
            con.rollback()
        finally:
            return redirect(url_for("home"))
            con.close()
    return render_template('home.html')    

@app.route('/home/<artist_name>',methods=['POST',"GET"])
def random_song(artist_name):
    '''Displays a random song, and info from the given artist'''
    if request.method =='POST':
        text=request.form['text']
        return redirect(url_for('random_song',artist_name=text))
    artist,name = get_artist(artist_name)
    songs = get_songs(artist)
    song = get_song(songs)
    lyric_link = get_lyric_link(song["name"],name)
    info = get_artist_info(name)
    return render_template(
        "home.html", songs=songs,
        song = song,name = name,
        lyric=lyric_link,info=info)

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=='POST':
        try:
            Uname=request.form['name']
            passwd=request.form['password']
            mail=request.form['mail']
            con=sqlite3.connect("database.db")
            cur=con.cursor()
            
            cur.execute("INSERT INTO users(username,password,email)VALUES(?,?,?)",(Uname,passwd,mail))
            con.commit()
            flash("Account created  successfully","success")

        except:
            flash("Error, username already taken!","danger")
            con.rollback()
        finally:
            return redirect(url_for("index"))
            con.close()

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("index"))

if __name__ == '__main__':
    app.run(
        debug=True  
    )
