from flask import Flask,render_template,url_for,request,session,redirect
import os
from pymongo import MongoClient
from bson.objectid import ObjectId
from media import media_rank
import bcrypt

def connect():
    connection = MongoClient("ds163016.mlab.com",63016)
    handle = connection["my_mongo1"]
    handle.authenticate("peppe","peppe10")
    return handle

app=Flask(__name__)
app.secret_key='onepiece'

mongo = connect()


@app.route('/')
def home():
    if 'username' in session:
        return render_template('home.html',user=session['username'])
    return render_template('home.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login_exe',methods=['POST'])
def login_exe():
    utenti=mongo.utenti
    login_user=utenti.find_one({'username':request.form['username']})
    if login_user:
        if bcrypt.hashpw(request.form['pass'].encode('utf-8'), login_user['password'].encode('utf-8')) == login_user['password'].encode('utf-8'):
            session['username'] = request.form['username']
            return redirect(url_for('home'))
    return render_template('login.html',fail=True)

@app.route('/logout')
def logout():
    session.pop('username',None)
    return redirect(url_for('login'))

@app.route('/register',methods=['POST','GET'])
def register():
    if request.method == 'POST':
        utenti=mongo.utenti
        gia_utente=utenti.find_one({'$or':[{'username':request.form['username']},{'email':request.form['email']}]})

        if gia_utente is None:
            hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())
            utenti.insert({'username' : request.form['username'], 'password' : hashpass, 'email':request.form['email']})
            session['username'] = request.form['username']
            return redirect(url_for('home'))

        return render_template('register.html',fail=True)

    return render_template('register.html')

@app.route('/local',methods=['POST'])
def local():
    city_s=mongo.locali.find_one({'city':request.form['city']})
    city=mongo.locali.find({'city':request.form['city']})

    if city_s is None:
        if 'username' in session:
                return render_template('home.html',user=session['username'],serch=True)
        return render_template('home.html',serch=True)


    if 'username' in session:
        return render_template('locali_geo.html',user=session['username'],locali=city)
    return render_template('locali_geo.html',locali=city)



@app.route('/menu/<path:nome>/<path:locale>',methods=['GET'])
def menu(nome,locale):
    menu_l=mongo.menu.find({'locale':ObjectId(locale)})
    locale=mongo.locali.find({'$or':[{'_id':ObjectId(locale)},{'locale':ObjectId(locale)}]})
    if 'username' in session:
        return render_template('menu.html',menu=menu_l,nome=nome,user=session['username'],locale=locale)

    return render_template('menu.html',menu=menu_l,nome=nome,locale=locale)

@app.route('/voto/<path:nome>/<path:locale>/<path:piatto>',methods=['POST'])
def voto(nome,locale,piatto):
    lista_voti=mongo.voti
    gia_votato=lista_voti.find_one({'utente':session['username'],'nome_p':piatto,'locale':ObjectId(locale)})
    menu=mongo.menu
    menu_l=mongo.menu.find({'locale':ObjectId(locale)})
    vot_piat=menu.find_one({'locale':ObjectId(locale),'nome_p':piatto,'rating':0})
    voto_x=int(request.form['voto'])

    if vot_piat is None and gia_votato is None:
        vol=media_rank(menu,locale,piatto,voto_x)
        lista_voti.insert({'utente':session['username'],'locale':ObjectId(locale),'nome_l':nome,'nome_p':piatto,'voto':int(request.form['voto'])})
        menu.update({'locale':ObjectId(locale),'nome_p':piatto},{'$inc':{'voti':1,'s'+request.form['voto']:1}})
        menu.update({'locale':ObjectId(locale),'nome_p':piatto},{'$set':{'rating':vol}})
        return render_template('menu.html',menu=menu_l,nome=nome,user=session['username'])
    elif gia_votato is None:
        lista_voti.insert({'utente':session['username'],'locale':ObjectId(locale),'nome_l':nome,'nome_p':piatto,'voto':int(request.form['voto'])})
        menu.update({'locale':ObjectId(locale),'nome_p':piatto},{'$inc':{'voti':1,'s'+request.form['voto']:1,'rating':float(request.form['voto'])}})
        return render_template('menu.html',menu=menu_l,nome=nome,user=session['username'])
    else:
        return render_template('menu.html',menu=menu_l,nome=nome,user=session['username'],votato=True)

@app.route('/user')
def user():
    utente=mongo.utenti.find({'username':session['username']})
    voti=mongo.voti.find({'utente':session['username']})

    return render_template('user.html',utente=utente,voti=voti,user=session['username'])

@app.route('/ricerca piatto',methods=['POST'])
def s_piatto():
    menu_s=mongo.menu.find_one({'nome_p':request.form['piatto']})
    menu_x=mongo.menu.find({'nome_p':request.form['piatto']})


    if menu_s is None:
        if 'username' in session:
                return render_template('home.html',user=session['username'],serchF=True)
        return render_template('home.html',serchF=True)


    if 'username' in session:
        return render_template('locali_geo.html',user=session['username'],locali=menu_x,serch_p=True)
    return render_template('locali_geo.html',locali=menu_x,serch_p=True)

if __name__=='__main__':
     app.run(debug=True)
