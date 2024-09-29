import os
import jwt
import uuid
import stripe
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from brokers.oanda import oanda_import
import xlrd
import requests
import locale
from os import remove

load_dotenv()

app = Flask(__name__, static_folder='./build')
SECRET_KEY = os.environ.get("SECRET_KEY")
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
# print(SECRET_KEY)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True


db = SQLAlchemy(app)


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50))
    firstname = db.Column(db.String(50))
    lastname = db.Column(db.String(50))
    email = db.Column(db.String(50))
    password = db.Column(db.String(200))
    membership = db.Column(db.String(10))
    paydate = db.Column(db.DateTime, default=datetime.utcnow())
    
class siigo_connections(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.String(50))
    user = db.Column(db.String(500))
    password = db.Column(db.String(500))
   

class Trades(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50))
    account_id = db.Column(db.String(30))
    broker = db.Column(db.String(20))
    trade_id = db.Column(db.String(20))
    status = db.Column(db.String(5))
    open_date = db.Column(db.String(50))
    symbol = db.Column(db.String(20))
    entry = db.Column(db.String(20))
    exit = db.Column(db.String(20))
    size = db.Column(db.String(20))
    pips = db.Column(db.String(20))
    ret_pips = db.Column(db.String(30))
    ret = db.Column(db.String(20))
    ret_percent = db.Column(db.String(20))
    ret_net = db.Column(db.String(20))
    side = db.Column(db.String(10))
    setups = db.Column(db.String(100))
    mistakes = db.Column(db.String(100))

class Reports_filters(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50))
    saldos = db.Column(db.String(1000))
    costoV= db.Column(db.String(1000))
    costoM= db.Column(db.String(1000))
    utilidad=db.Column(db.String(1000))
    gastosAdmon=db.Column(db.String(1000))
    gastosPer=db.Column(db.String(1000))
    gastosHono=db.Column(db.String(1000))
    gastosImp=db.Column(db.String(1000))
    gastosArrend=db.Column(db.String(1000))
    gastosServ=db.Column(db.String(1000))
    gastosLegales=db.Column(db.String(1000))
    gastosViaje=db.Column(db.String(1000))
    gastosDiver=db.Column(db.String(1000))
    margenBruto=db.Column(db.String(1000))
    Año=db.Column(db.String(1000))
    margenOperacional=db.Column(db.String(1000))
    margenNeto=db.Column(db.String(1000))
    gastosVentas=db.Column(db.String(1000))
    roa=db.Column(db.String(1000))
    roe=db.Column(db.String(1000))
    last_date= db.Column(db.String(50))
    
class Reports(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50))
    AÑO_2021= db.Column(db.String(50))
    AÑO_2022= db.Column(db.String(50))
    AÑO_2023= db.Column(db.String(50))
    AÑO_2024= db.Column(db.String(50))
    last_date= db.Column(db.String(50))
    

class SubTrades(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50))
    trade_id = db.Column(db.String(20))
    action = db.Column(db.String(10))
    spread = db.Column(db.String(10))
    type = db.Column(db.String(10))
    date = db.Column(db.String(50))
    size = db.Column(db.String(20))
    position = db.Column(db.String(20))
    price = db.Column(db.String(20))


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]
        if not token:
            return jsonify({'error': 'a valid token is missing'})
        try:
            data = jwt.decode(
                token, app.config["SECRET_KEY"], algorithms=["HS256"])
            current_user = Users.query.filter_by(
                public_id=data['public_id']).first()
            if current_user is None:
                return jsonify({'error': 'Unauthorized'})
        except:
            return jsonify({'message': 'token is invalid'})
        return f(current_user, *args, **kwargs)
    return decorated


def sort_by_date(dic):
    return dic.open_date


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')


@app.route("/api/user/register", methods=["POST"])
def register_user():
    data = request.json
    check_email = Users.query.filter_by(email=data['email']).first()
    if check_email:
        return jsonify({"email": "Email already exists"}), 400
    hashed_password = generate_password_hash(
        data['password'], method='pbkdf2:sha256')
    new_user = Users(public_id=str(uuid.uuid4(
    )), firstname=data['firstname'], lastname=data['lastname'], password=hashed_password, email=data['email'], membership='trial')
    db.session.add(new_user)
    db.session.commit()
    token = jwt.encode({'public_id': new_user.public_id, 'name': new_user.firstname + " " + new_user.lastname, 'email': new_user.email, 'membership': 'trial', 'expired': 0, 'iat': datetime.utcnow(), 'exp': datetime.utcnow(
    ) + timedelta(minutes=30)}, app.config['SECRET_KEY'], "HS256")
    return jsonify({"success": True, "token": "Bearer " + str(token)})


@app.route("/api/user/login", methods=["POST"])
def login_user():
    data = request.json
    user = Users.query.filter_by(email=data['email']).first()
    if not user:
        return jsonify({"email": "User not found"}), 400
    if check_password_hash(user.password, data['password']):
        if user.membership == 'trial':
            expireday = 7
        else:
            expireday = 30
        if user.paydate + timedelta(days=expireday) > datetime.utcnow():
            expired = 0
        else:
            expired = 1
        token = jwt.encode({'public_id': user.public_id,  'name': user.firstname + " " + user.lastname, 'email': user.email, 'membership': user.membership, 'expired': expired, 'iat': datetime.utcnow(), 'exp': datetime.utcnow(
        ) + timedelta(hours=12)}, app.config['SECRET_KEY'], "HS256")
        return jsonify({"success": True, "token": "Bearer " + str(token)})
    else:
        return jsonify({"password": "Incorrect password"}), 400


@app.route("/api/user/current", methods=["GET"])
@token_required
def get_current_user(current_user):
    user = Users.query.filter_by(email=current_user.email).first()
    return jsonify({"id": user.public_id, "email": user.email, "firstname": user.firstname, "lastname": user.lastname, "membership": user.membership, "paydate": user.paydate})

# oanda import
@app.route("/api/import_trades", methods=["POST"])
def import_trades():
    tokens = request.json
    broker = tokens["broker"]
    if broker == "Oanda":
        imported_trades = oanda_import(tokens["key"], tokens["id"])
    # if broker == "Metatrader":
    #     imported_trades = metatrader_import(
    #         tokens["id"], tokens["password"], tokens["mtType"], tokens["passphrase"])
    if 'trades' in imported_trades:
        userid = tokens["user"]
        for trade_data in imported_trades['trades']:
            check_trade = Trades.query.filter_by(user_id=userid,
                                                 account_id=trade_data["account_id"], broker=trade_data["broker"], trade_id=trade_data["trade_id"]).first()
            if check_trade:
                continue
            new_trade = Trades(user_id=userid, account_id=trade_data["account_id"], broker=trade_data["broker"], trade_id=trade_data["trade_id"], status=trade_data["status"], open_date=trade_data["open_date"],
                               symbol=trade_data["symbol"], entry=trade_data["entry"], exit=trade_data["exit"], size=trade_data["size"], pips=trade_data["pips"], ret_pips=trade_data["ret_pips"], ret=trade_data["ret"], ret_percent=trade_data["ret_percent"], ret_net=trade_data["ret_net"], side=trade_data["side"], setups=trade_data["setups"], mistakes=trade_data["mistakes"])
            db.session.add(new_trade)
            for sub in trade_data["subs"]:
                new_sub = SubTrades(user_id=userid, trade_id=trade_data["trade_id"], action=sub["action"], spread=sub["spread"],
                                    type=sub["type"], date=sub["date"], size=sub["size"], position=sub["position"], price=sub["price"])
                db.session.add(new_sub)
            db.session.commit()
        return jsonify({"success": True})
    else:
        return jsonify({"error": "Error occured"}), 500

@app.route("/api/siigo_validate_credentials", methods=["POST"])
def siigo_validate_credentials():
    tokens = request.json
    user=tokens['user']    
    accountid=''
    user_siigo=''
    password_siigo=''
    new_report=siigo_connections.query.filter_by(userid=user).first()
    if new_report!=None and new_report!=[]:
        user_siigo=str(new_report.user)
        password_siigo=str(new_report.password)
        value= False   
    else:
        value= True
    return jsonify({"tieneData": value,"user_siigo":user_siigo,"password_siigo":password_siigo})

@app.route("/api/siigo_account", methods=["POST"])
def siigo_account_anual():    
    tokens = request.json   
    params={
    "username": tokens['id'],
    "access_key": tokens['pass']
    }
    try:
        response = requests.request("POST", "https://api.siigo.com/auth",json=params).json()
        
        access_token=response["access_token"]
    except:
        return jsonify({"success": False})
    
    
    headers ={
               "Content-Type":"application/json",
               "Authorization" :response["access_token"],
               "Partner-Id":"sigo"
             }
    user=tokens['user']
    token=tokens["id"]
    new_report=siigo_connections.query.filter_by(userid=user).first()
    if new_report==None or new_report==[]:
        try:   
            new_report = siigo_connections(userid=user,user=tokens['id'],password=tokens['pass'])
            db.session.add(new_report)
            db.session.commit()
        except Exception as err:
            pass
    now = datetime.now()
    endDate = now.strftime('%Y-%m-%d')
    presentYear=int(now.strftime('%Y'))
    years=[2021,2022,2023,2024]
    update=False
    new_report=Reports.query.filter_by(user_id=user).first()
    if new_report!=None and new_report!=[]:
        last_date=new_report.last_date
        last_date = datetime.strptime(last_date, '%Y-%m-%d')
        yearLastDate=int(last_date.strftime('%Y'))
        monthUltimoSync=int(last_date.strftime('%m'))
        years=[]
        while yearLastDate<=presentYear:
               years.append(yearLastDate)
               yearLastDate=yearLastDate+1
        update=True
    monthStart=1
    monthEnd=3
    saldo=[]
    ventas=[]
    materia_prima=[]
    utilidad=[]
    gastosAdmon=[]
    gastosPer=[]
    gastosHono=[]
    gastosImp=[]
    gastosArrend=[]
    gastosServ=[]
    gastosLegales=[]
    gastosViaje=[]
    gastosDiver=[]
    margenBrut=[]
    lista_años=[]
    for year in years:
        lista=[]
        params={
          "account_start": "",
          "account_end": "",
          "year": year,
          "month_start": 1,
          "month_end": 12,
          "includes_tax_difference": False
        }
        #monthStart=monthEnd
        #monthEnd+=3
        try:
            response = requests.request("POST", "https://api.siigo.com/v1/test-balance-report", headers=headers,json=params).json()
            urlArchivo=response['file_url']  
            print(urlArchivo)
            response = requests.get(urlArchivo)
            archivo=user+'.xlsx'
            #remove("balance_general.xlsx")
            with open(archivo, 'wb') as file:
                 file.write(response.content)
            #webbrowser.get(chrome_path).open(urlArchivo)
            print("exito")
        except Exception as err:
            return jsonify({"success": False})
        
        try:
            df = pd.read_excel(archivo,header=4,engine='openpyxl')
        except Exception as err:
            print(err)
            lista.append(0.0)
            lista.append(0.0)
            lista.append(0.0)
            lista.append(0.0)
            lista.append(0.0)
            lista.append(0.0)
            lista.append(0.0)
            lista.append(0.0)
            lista.append(0.0)
            lista.append(0.0)
            lista.append(0.0)
            lista.append(0.0)
            lista.append(0.0)
            lista.append(0.0)
            lista.append(0.0)
            lista.append(0.0)
            lista.append(0.0)
            lista.append(0.0)
            lista.append(0.0)
            lista_años.append(lista)
            continue
        df.columns = ['Nivel',
                     'Transaccional','Codigo','Nombre','Saldo','Movimiento','Movimiento cred','Saldo final']
        df[df=='Saldo final']=np.nan
        df = df.fillna(0)
        df['Saldo final']=df['Saldo final'].astype(str)
        print(df['Saldo final'])
        df[df=='Codigo']=np.nan
        df = df.fillna(0)
        print(df['Codigo'])
        df['Codigo']=df['Codigo'].astype(int)
        print(df['Codigo'])
        cont = df[df['Codigo'] == 41]
        try:
            costoVentas= df[df['Codigo'] == 7]
        except:
            costoVentas= df[df['Codigo'] == 6]
        try:
            costoMateria= df[df['Codigo'] == 61]
        except:
            pass
        try:
            ingresos_no_operac=abs(float(df[df['Codigo'] == 42]['Saldo final']))
        except:
            ingresos_no_operac=0.0
        try:
            gastos_administracion=abs(float(df[df['Codigo'] == 51]['Saldo final']))
        except:
            gastos_administracion=0.0
        try:
            gastos_ventas=abs(float(df[df['Codigo'] == 52]['Saldo final']))
        except:
            gastos_ventas=0.0            
        try:
            gastos_no_operacionales=abs(float(df[df['Codigo'] == 53]['Saldo final']))
        except:
            gastos_no_operacionales=0.0
        try:
            impuestos=abs(float(df[df['Codigo'] == 54]['Saldo final']))
        except:
            impuestos=0.0
        try:
            gastos_personal=abs(float(df[df['Codigo'] == 5105]['Saldo final']))
        except:
            gastos_personal=0.0
        try:
            gastos_honorarios=abs(float(df[df['Codigo'] == 5110]['Saldo final']))
        except:
            gastos_honorarios=0.0
        try:
            gastos_impuestos=abs(float(df[df['Codigo'] == 5115]['Saldo final']))
        except:
            gastos_impuestos=0.0
        try:
            gastos_arrendamientos=abs(float(df[df['Codigo'] == 5120]['Saldo final']))
        except:
            gastos_arrendamientos=0.0
        try:
            gastos_servicios=abs(float(df[df['Codigo'] == 5135]['Saldo final']))
        except:
            gastos_servicios=0.0
        try:
            gastos_legales=abs(float(df[df['Codigo'] == 5140]['Saldo final']))
        except:
            gastos_legales=0.0
        try:
            gastos_viajes=abs(float(df[df['Codigo'] == 5155]['Saldo final']))
        except:
            gastos_viajes=0.0
        try:
            gastos_diversos=abs(float(df[df['Codigo'] == 5195]['Saldo final']))
        except:
            gastos_diversos=0.0
        print(cont['Saldo final'])
        try:
           numero=abs(float(cont['Saldo final']))
        except:
           numero=0.0 
        try:
           numeroCosto=abs(float(costoVentas['Saldo final']))
           numeroCosto=numeroCosto*-1
        except:
           numeroCosto=0.0
        utilidadBruta=numero+numeroCosto
        utilidad_operacional=utilidadBruta-gastos_administracion-gastos_ventas
        try:
            margen_operacional=utilidad_operacional/numero
            margen_operacional=round((utilidad_operacional/numero)*100,0)
        except:
            margen_operacional=0.0
        utilidad_neta=utilidad_operacional-gastos_no_operacionales+ingresos_no_operac-impuestos
        try:
            margen_neto=round((utilidad_neta/numero)*100,0)
        except:
            margen_neto=0.0
        try:
            margenBruto=round((utilidadBruta/numero)*100,0)
        except Exception as err:
            margenBruto=0.0
        try:
            numeroCostoMateria=abs(float(costoMateria['Saldo final']))
        except:
            numeroCostoMateria=0.0
        try:
            activos=abs(float(df[df['Codigo'] == 1]['Saldo final']))
        except Exception as err:
            activos=0.0
        try:
            patrimonio=abs(float(df[df['Codigo'] == 3]['Saldo final']))
        except:
            patrimonio=0.0
        try:
            roa=abs(round((utilidad_operacional/activos)*100,0))
        except:
            roa=0.0
        try:
            roe=abs(round((utilidad_neta/patrimonio)*100,0))
        except:
            roe=0.0
        """
        saldo.append(numero)
        ventas.append(numeroCosto)
        materia_prima.append(numeroCostoMateria)
        utilidad.append(utilidadBruta)
        gastosAdmon.append(gastos_administracion)
        gastosPer.append(gastos_personal)
        gastosHono.append(gastos_honorarios)
        gastosImp.append(gastos_impuestos)
        gastosArrend.append(gastos_arrendamientos)
        gastosServ.append(gastos_servicios)
        gastosLegales.append(gastos_legales)
        gastosViaje.append(gastos_viajes)
        gastosDiver.append(gastos_diversos)
        margenBrut.append(margenBruto)
        """
        lista.append(numero)
        lista.append(numeroCosto)
        lista.append(numeroCostoMateria)
        lista.append(utilidadBruta)
        lista.append(gastos_administracion)
        lista.append(gastos_personal)
        lista.append(gastos_honorarios)
        lista.append(gastos_impuestos)
        lista.append(gastos_arrendamientos)
        lista.append(gastos_servicios)
        lista.append(gastos_legales)
        lista.append(gastos_viajes)
        lista.append(gastos_diversos)
        lista.append(margenBruto)
        lista.append(margen_operacional)
        lista.append(margen_neto)
        lista.append(gastos_ventas)
        lista.append(roa)
        lista.append(roe)
        lista_años.append(lista)
    if not update:
                try:   
                    new_report = Reports(user_id=user,AÑO_2021=str(lista_años[0]),AÑO_2022=str(lista_años[1]),AÑO_2023=str(lista_años[2]),AÑO_2024=str(lista_años[3]),last_date=str(endDate))
                    db.session.add(new_report)
                    db.session.commit()
                    db.session.close()
                except Exception as err:
                    pass
    else:
                try:   
                    new_report.AÑO_2024=str(lista_años[0])
                    if len(lista_años)>1:
                        new_report.AÑO_2025=str(lista_años[1])
                    new_report.last_date=str(endDate)
                    db.session.commit()
                    db.session.close()
                except:
                    pass            
    "guardar en reports los campos de todos los años"
    siigo_account_trimestral(user,access_token)
    print("los saldos de los años son estos ",saldo)
    return jsonify({"success": True})
    #return jsonify({"success": True,"saldo":saldo,"costoV":ventas,"costoM":materia_prima,"utilidad":utilidad,"gastosAdmon":gastosAdmon,"gastosPer":gastosPer,"gastosHono":gastosHono,"gastosImp":gastosImp,"gastosArrend":gastosArrend,"gastosServ":gastosServ,"gastosLegales":gastosLegales,"gastosViaje":gastosViaje,"gastosDiver":gastosDiver,"margenBruto":margenBrut})


def siigo_account_trimestral(user,token):
    headers ={
               "Content-Type":"application/json",
               "Authorization" :token,
               "Partner-Id":"sigo"
             }
    lista_trimestral=[]
    now = datetime.now()
    endDate = now.strftime('%Y-%m-%d')
    presentYear=int(now.strftime('%Y'))
    years=[presentYear-3,presentYear-2,presentYear-1,presentYear]
    monthActual=int(now.strftime('%m'))
    monthStart=1
    monthEnd=1
    update=False
    new_report=Reports_filters.query.filter_by(user_id=user).order_by(Reports_filters.id.desc()).first()
    if new_report!=None and new_report!=[]:
        update_saldos=eval(new_report.saldos)
        update_costoV=eval(new_report.costoV)
        update_costoM=eval(new_report.costoM)
        update_utilidad=eval(new_report.utilidad)
        update_gastosAdmon=eval(new_report.gastosAdmon)
        update_gastosPer=eval(new_report.gastosPer)
        update_gastosHono=eval(new_report.gastosHono)
        update_gastosImp=eval(new_report.gastosImp)
        update_gastosArrend=eval(new_report.gastosArrend)
        update_gastosServ=eval(new_report.gastosServ)
        update_gastosLegales=eval(new_report.gastosLegales)
        update_gastosViaje=eval(new_report.gastosViaje)
        update_gastosDiver=eval(new_report.gastosDiver)
        update_margenBruto=eval(new_report.margenBruto)
        update_margenOperacional=eval(new_report.margenOperacional)
        update_margenNeto=eval(new_report.margenNeto)
        update_gastosVentas=eval(new_report.gastosVentas)
        update_roa=eval(new_report.roa)
        update_roe=eval(new_report.roe)
        last_date=new_report.last_date
        last_date = datetime.strptime(last_date, '%Y-%m-%d')
        yearLastDate=int(last_date.strftime('%Y'))
        monthUltimoSync=int(last_date.strftime('%m'))
        monthStart=monthUltimoSync
        monthEnd=monthUltimoSync
        years=[]
        while yearLastDate<=presentYear:
               years.append(yearLastDate)
               yearLastDate=yearLastDate+1
        update=True
    years=[2024]
    monthStart=8
    monthEnd=8
    for year in years:
      saldo=[]
      ventas=[]
      materia_prima=[]
      utilidad=[]
      gastosAdmon=[]
      gastosVent=[]
      gastosPer=[]
      gastosHono=[]
      gastosImp=[]
      gastosArrend=[]
      gastosServ=[]
      gastosLegales=[]
      gastosViaje=[]
      gastosDiver=[]
      margenBrut=[]
      margenOperacional=[]
      margenNeto=[]
      roa_list=[]
      roe_list=[]
      while monthStart <= 12:
        if(year==presentYear and monthStart>=monthActual):
           break
        params={
          "account_start": "",
          "account_end": "",
          "year": year,
          "month_start": monthStart,
          "month_end": monthEnd,
          "includes_tax_difference": False
        }
        monthStart=monthEnd+1
        monthEnd=monthStart
        try:
            response = requests.request("POST", "https://api.siigo.com/v1/test-balance-report", headers=headers,json=params).json()
            urlArchivo=response['file_url']  
            print(urlArchivo)
            response = requests.get(urlArchivo)
            archivo=user+'.xlsx'
            #remove('balance_general.xlsx')
            with open(archivo, 'wb') as file:
                 file.write(response.content)
            #webbrowser.get(chrome_path).open(urlArchivo)
            print("exito")
        except Exception as err:
            return jsonify({"success": False})
        
        try:
            df = pd.read_excel(archivo,header=4,engine='openpyxl')
        except Exception as err:
            print(err)
            saldo.append(0.0)
            ventas.append(0.0)
            materia_prima.append(0.0)
            utilidad.append(0.0)
            gastosAdmon.append(0.0)
            gastosPer.append(0.0)
            gastosHono.append(0.0)
            gastosImp.append(0.0)
            gastosArrend.append(0.0)
            gastosServ.append(0.0)
            gastosLegales.append(0.0)
            gastosViaje.append(0.0)
            gastosDiver.append(0.0)
            margenBrut.append(0.0)
            margenOperacional.append(0.0)
            margenNeto.append(0.0)
            gastosVent.append(0.0)
            roa.append(0.0)
            roe.append(0.0)
            continue
        df.columns = ['Nivel',
                     'Transaccional','Codigo','Nombre','Saldo','Movimiento','Movimiento cred','Saldo final']
        df[df=='Saldo final']=np.nan
        df = df.fillna(0)
        df['Saldo final']=df['Saldo final'].astype(str)
        print(df['Saldo final'])
        df[df=='Codigo']=np.nan
        df = df.fillna(0)
        print(df['Codigo'])
        df['Codigo']=df['Codigo'].astype(int)
        print(df['Codigo'])
        cont = df[df['Codigo'] == 41]
        try:
            costoVentas= df[df['Codigo'] == 7]
        except:
            costoVentas= df[df['Codigo'] == 6]
        costoMateria= df[df['Codigo'] == 61]
        try:
            ingresos_no_operac=abs(float(df[df['Codigo'] == 42]['Saldo final']))
        except:
            ingresos_no_operac=0.0
        try:
            gastos_administracion=abs(float(df[df['Codigo'] == 51]['Saldo final']))
        except:
            gastos_administracion=0.0
        try:
            gastos_ventas=abs(float(df[df['Codigo'] == 52]['Saldo final']))
        except:
            gastos_ventas=0.0
        try:
            gastos_no_operacionales=abs(float(df[df['Codigo'] == 53]['Saldo final']))
        except:
            gastos_no_operacionales=0.0
        try:
            impuestos=abs(float(df[df['Codigo'] == 54]['Saldo final']))
        except:
            impuestos=0.0
        try:
            gastos_personal=abs(float(df[df['Codigo'] == 5105]['Saldo final']))
        except:
            gastos_personal=0.0
        try:
            gastos_honorarios=abs(float(df[df['Codigo'] == 5110]['Saldo final']))
        except:
            gastos_honorarios=0.0
        try:
            gastos_impuestos=abs(float(df[df['Codigo'] == 5115]['Saldo final']))
        except:
            gastos_impuestos=0.0
        try:
            gastos_arrendamientos=abs(float(df[df['Codigo'] == 5120]['Saldo final']))
        except:
            gastos_arrendamientos=0.0
        try:
            gastos_servicios=abs(float(df[df['Codigo'] == 5135]['Saldo final']))
        except:
            gastos_servicios=0.0
        try:
            gastos_legales=abs(float(df[df['Codigo'] == 5140]['Saldo final']))
        except:
            gastos_legales=0.0
        try:
            gastos_viajes=abs(float(df[df['Codigo'] == 5155]['Saldo final']))
        except:
            gastos_viajes=0.0
        try:
            gastos_diversos=abs(float(df[df['Codigo'] == 5195]['Saldo final']))
        except:
            gastos_diversos=0.0
        print(cont['Saldo final'])
        try:
            numero=abs(float(cont['Saldo final']))
        except:
            numero=0.0
        try:
            numeroCosto=abs(float(costoVentas['Saldo final']))
            numeroCosto=numeroCosto*-1
        except:
            numeroCosto=0.0
        utilidadBruta=numero+numeroCosto
        utilidad_operacional=utilidadBruta-gastos_administracion-gastos_ventas
        try:
            margen_operacional=round((utilidad_operacional/numero)*100,0)
        except:
            margen_operacional=0.0
        utilidad_neta=utilidad_operacional-gastos_no_operacionales+ingresos_no_operac-impuestos
        try:
            margen_neto=round((utilidad_neta/numero)*100,0)
        except:
            margen_neto=0.0
        try:
            margenBruto=round((utilidadBruta/numero)*100,0)
        except Exception as err:
            margenBruto=0.0
        try:
            numeroCostoMateria=abs(float(costoMateria['Saldo final']))
        except:
            numeroCostoMateria=0.0
        try:
            activos=abs(float(df[df['Codigo'] == 1]['Saldo final']))
        except Exception as err:
            activos=0.0
        try:
            patrimonio=abs(float(df[df['Codigo'] == 3]['Saldo final']))
        except:
            patrimonio=0.0
            
        try:
            roa=abs(round((utilidad_operacional/activos)*100,0))
        except:
            roa=0.0
        try:
            roe=abs(round((utilidad_neta/patrimonio)*100,0))
        except:
            roe=0.0
        if not update:
            saldo.append(numero)
            ventas.append(numeroCosto)
            materia_prima.append(numeroCostoMateria)
            utilidad.append(utilidadBruta)
            gastosAdmon.append(gastos_administracion)
            gastosPer.append(gastos_personal)
            gastosHono.append(gastos_honorarios)
            gastosImp.append(gastos_impuestos)
            gastosArrend.append(gastos_arrendamientos)
            gastosServ.append(gastos_servicios)
            gastosLegales.append(gastos_legales)
            gastosViaje.append(gastos_viajes)
            gastosDiver.append(gastos_diversos)
            margenBrut.append(margenBruto)
            margenOperacional.append(margen_operacional)
            margenNeto.append(margen_neto)
            gastosVent.append(gastos_ventas)
            roa_list.append(roa)
            roe_list.append(roe)
        else:
            update_saldos.append(numero)
            update_costoV.append(numeroCosto)
            update_costoM.append(numeroCostoMateria)
            update_utilidad.append(utilidadBruta)
            update_gastosAdmon.append(gastos_administracion)
            update_gastosPer.append(gastos_personal)
            update_gastosHono.append(gastos_honorarios)
            update_gastosImp.append(gastos_impuestos)
            update_gastosArrend.append(gastos_arrendamientos)
            update_gastosServ.append(gastos_servicios)
            update_gastosLegales.append(gastos_legales)
            update_gastosViaje.append(gastos_viajes)
            update_gastosDiver.append(gastos_diversos)
            update_margenBruto.append(margenBruto)
            update_margenOperacional.append(margen_operacional)
            update_margenNeto.append(margen_neto)
            update_gastosVentas.append(gastos_ventas)
            update_roa.append(roa)
            update_roe.append(roe)
      if not update and saldo!=[]:
          try:         
            new_report = Reports_filters(user_id=user,Año=str(year),saldos=str(saldo),costoV=str(ventas),costoM=str(materia_prima),utilidad=str(utilidad),gastosAdmon=str(gastosAdmon),gastosPer=str(gastosPer),gastosHono=str(gastosHono),gastosImp=str(gastosImp),gastosArrend=str(gastosArrend),gastosServ=str(gastosServ),gastosLegales=str(gastosLegales),gastosViaje=str(gastosViaje),gastosDiver=str(gastosDiver),margenBruto=str(margenBrut),margenOperacional=str(margenOperacional),margenNeto=str(margenNeto),gastosVentas=str(gastosVent),roa=str(roa_list),roe=str(roe_list),last_date=str(endDate))
            db.session.add(new_report)
            db.session.commit()
            db.session.close()
          except:
            pass
      elif update:
            new_report.saldos=str(update_saldos)
            new_report.costoV=str(update_costoV)
            new_report.costoM=str(update_costoM)
            new_report.utilidad=str(update_utilidad)
            new_report.gastosAdmon=str(update_gastosAdmon)
            new_report.gastosPer=str(update_gastosPer)
            new_report.gastosHono=str(update_gastosHono)
            new_report.gastosImp=str(update_gastosImp)
            new_report.gastosArrend=str(update_gastosArrend)
            new_report.gastosServ=str(update_gastosServ)
            new_report.gastosLegales=str(update_gastosLegales)
            new_report.gastosViaje=str(update_gastosViaje)
            new_report.gastosDiver=str(update_gastosDiver)
            new_report.margenBruto=str(update_margenBruto)
            new_report.margenOperacional=str(update_margenOperacional)
            new_report.margenNeto=str(update_margenNeto)
            new_report.gastosVentas=str(update_gastosVentas)
            new_report.roa=str(update_roa)
            new_report.roe=str(update_roe)
            new_report.last_date=str(endDate)
            db.session.commit()
      monthStart=1
      monthEnd=1
      update=False
      "guardar la informacion trimestral por c/año en la tabla reports_filters"

@app.route("/api/import_reports_siigo", methods=["POST"])
def import_reports_siigo():
    data = request.json
    user=data['user']
    saldo=data['saldo']
    costoV=data['costoV']
    costoM=data['costoM']
    utilidad=data['utilidad']
    gastosAdmon=data['gastosAdmon']
    gastosPer=data['gastosPer']
    gastosHono=data['gastosHono']
    gastosImp=data['gastosImp']
    gastosArrend=data['gastosArrend']
    gastosServ=data['gastosServ']
    gastosLegales=data['gastosLegales']
    gastosViaje=data['gastosViaje']
    gastosDiver=data['gastosDiver']
    margenBruto=data['margenBruto']
    check_trade = Reports.query.filter_by(user_id=user).first()
    if check_trade:
        return False
    new_report = Reports(user_id=user,saldos=str(saldo),costoV=str(costoV),costoM=str(costoM),utilidad=str(utilidad),gastosAdmon=str(gastosAdmon),gastosPer=str(gastosPer),gastosHono=str(gastosHono),gastosImp=str(gastosImp),gastosArrend=str(gastosArrend),gastosServ=str(gastosServ),gastosLegales=str(gastosLegales),gastosViaje=str(gastosViaje),gastosDiver=str(gastosDiver),margenBruto=str(margenBruto))
    db.session.add(new_report)
    db.session.commit()
    return jsonify({"success": True})
       
    
       
# metatrader import
@app.route("/api/import-metatrader/account", methods=["POST"])
def import_metatrader_account():
    tokens = request.json
    result = metatrader_import(tokens["id"], tokens["password"], tokens["mtType"], tokens["passphrase"])
    return jsonify(result)
@app.route("/api/import-metatrader/orders", methods=["POST"])
def import_metatrader_orders():
    tokens = request.json
    orders = get_metatrader_orders(tokens["id"])
    return jsonify(orders)
@app.route("/api/import-metatrader/extract", methods=["POST"])
def extract_metatrader_data():
    params = request.json
    imported_trades = extract_data(params["order"], params["login"], params["contract"])
    userid = params["user"]
    for trade_data in imported_trades:
        check_trade = Trades.query.filter_by(user_id=userid,
                                                account_id=trade_data["account_id"], broker=trade_data["broker"], trade_id=trade_data["trade_id"]).first()
        if check_trade:
            continue
        new_trade = Trades(user_id=userid, account_id=trade_data["account_id"], broker=trade_data["broker"], trade_id=trade_data["trade_id"], status=trade_data["status"], open_date=trade_data["open_date"],
                            symbol=trade_data["symbol"], entry=trade_data["entry"], exit=trade_data["exit"], size=trade_data["size"], pips=trade_data["pips"], ret_pips=trade_data["ret_pips"], ret=trade_data["ret"], ret_percent=trade_data["ret_percent"], ret_net=trade_data["ret_net"], side=trade_data["side"], setups=trade_data["setups"], mistakes=trade_data["mistakes"])
        db.session.add(new_trade)
        for sub in trade_data["subs"]:
            new_sub = SubTrades(user_id=userid, trade_id=trade_data["trade_id"], action=sub["action"], spread=sub["spread"],
                                type=sub["type"], date=sub["date"], size=sub["size"], position=sub["position"], price=sub["price"])
            db.session.add(new_sub)
        db.session.commit()
    return jsonify({"success": True, "count": len(imported_trades)})

@app.route("/api/get_trades", methods=["POST"])
def get_trade_data():
    rdata = request.json
    userid = rdata["user"]
    data_display = Trades.query.filter_by(
        user_id=userid).all()
    data_array = []
    for data in data_display:
        subdata_display = SubTrades.query.filter_by(
            trade_id=data.trade_id, user_id=userid).all()
        subs = []
        for sub in subdata_display:
            subs.append({"action": sub.action, "spread": sub.spread, "type": sub.type,
                        "date": sub.date, "size": sub.size, "position": sub.position, "price": sub.price, })
        data_array.append({"id": data.trade_id, "accountId": data.account_id, "broker": data.broker, "status": data.status, "openDate": data.open_date, "symbol": data.symbol,
                          "entry": data.entry, "exit": data.exit, "size": data.size, "pips": data.pips, "returnPips": data.ret_pips, "return": data.ret, "returnPercent": data.ret_percent, "returnNet": data.ret_net, "side": data.side, "setups": data.setups, "mistakes": data.mistakes, "subs": subs})
    return jsonify(data_array)



@app.route("/api/get_reports_validate", methods=["POST"])
def get_reports_validate():
    rdata = request.json
    userid = rdata["user"]
    data_display = Reports.query.filter_by(
        user_id=userid).all()
    data_array = []
    if data_display !=[]:
        for data in data_display:
            data_array.append(data.AÑO_2021)
            data_array.append(data.AÑO_2022)
            data_array.append(data.AÑO_2023)
            data_array.append(data.AÑO_2024)
    return jsonify(data_array)


@app.route("/api/delete_trades", methods=["POST"])
def delete_trade_data():
    params = request.json
    user_id = params["userId"]
    trade_ids = params["tradeId"]
    trades = Trades.query.filter_by(user_id=user_id).all()
    for trade in trades:
        if trade.trade_id in trade_ids:
            db.session.delete(trade)
            subtrades = SubTrades.query.filter_by(
                user_id=user_id, trade_id=trade.trade_id).all()
            for subtrade in subtrades:
                db.session.delete(subtrade)
    db.session.commit()
    return "succeed"


@app.route("/create-payment-intent", methods=["POST"])
def create_payment():
    try:
        stripe_keys = {
            "secret_key": os.environ.get("STRIPE_SECRET_KEY"),
            "publishable_key": os.environ.get("STRIPE_PUBLISHABLE_KEY"),
        }
        stripe.api_key = stripe_keys["secret_key"]
        data = request.json
        intent = stripe.PaymentIntent.create(
            amount=data["price"],
            currency="usd",
            # automatic_payment_methods={
            #     'enabled': True,
            # },
            payment_method_types=["card"],
        )
        return jsonify({'clientSecret': intent['client_secret']})
    except Exception as e:
        return jsonify(error=str(e)), 403


@app.route("/api/payment-success", methods=["POST"])
def payment_success():
    data = request.json
    user = Users.query.filter_by(email=data["email"]).first()
    user.membership = data["membership"]
    user.paydate = datetime.utcnow()
    db.session.commit()
    token = jwt.encode({'public_id': user.public_id, 'name': user.firstname + " " + user.lastname, 'email': user.email, 'membership': user.membership, 'expired': 0, 'iat': datetime.utcnow(), 'exp': datetime.utcnow(
    ) + timedelta(minutes=30)}, app.config['SECRET_KEY'], "HS256")
    return jsonify({"success": True, "token": "Bearer " + token})


@app.route("/api/get-chart", methods=["POST"])
def get_chartdata():
    data = request.json
    trades = Trades.query.filter_by(user_id=data["userId"]).all()
    trades.sort(key=sort_by_date)
    xvalue_all = []
    trade_count = 0
    accumulative_return = []
    accumulative_return_total = 0
    profit_factor = []
    total_profit_factor = 0
    avg_return = []
    avg_return_total = 0
    win_count = 0
    pnl_total = 0
    pnl_change = 0
    volume_total = 0
    pnl_day = 0
    volume_day = 0
    total_pnl = []
    daily_pnl = []
    daily_volume = []
    total_win_rate = []
    daily_win_rate = []
    total_win_or_loss_score = []
    win_or_loss_score = 0
    for trade in trades:
        trade_count += 1
        xvalue_all.append(trade.open_date[0:10])
        accumulative_return_total += float(trade.ret)
        accumulative_return.append(accumulative_return_total)
        profit_factor.append(abs(float(trade.ret)) / float(trade.entry))
        total_profit_factor += abs(float(trade.ret)) / float(trade.entry)
        avg_return_total += float(trade.ret)
        avg_return.append(avg_return_total / trade_count)
        if trade.status == "WIN":
            win_count += 1
            daily_win_rate.append(100)
            win_or_loss_score += 3
        else:
            daily_win_rate.append(0)
            win_or_loss_score -= 2
        volume_total += float(trade.entry)
        total_pnl.append(round(accumulative_return_total, 2))
        daily_pnl.append(round(float(trade.ret), 2))
        daily_volume.append(round(float(trade.entry)))
        total_win_rate.append(round(100 * win_count / trade_count, 2))
        total_win_or_loss_score.append(win_or_loss_score)
    pnl_total = accumulative_return_total
    pnl_change = pnl_total / volume_total * 100
    pnl_day = pnl_total / len(trades)
    volume_day = volume_total / len(trades)
    return jsonify({"accumulative_return": accumulative_return, "accumulative_return_total": accumulative_return_total, "xvalue_all": xvalue_all, "profit_factor": profit_factor, "avg_profit_factor": total_profit_factor / len(profit_factor), "avg_return": avg_return, "avg_return_total": avg_return_total / len(trades), "win_ratio": {"total": len(trades), "winning": win_count}, "pnl_total": pnl_total, "pnl_change": pnl_change, "pnl_day": pnl_day, "volume_day": volume_day, "total_pnl": total_pnl, "daily_pnl": daily_pnl, "daily_volume": daily_volume, "total_win_rate": total_win_rate, "daily_win_rate": daily_win_rate, "total_win_or_loss_score": total_win_or_loss_score})

@app.route("/api/get-reports_siigo", methods=["POST"])
def get_reports_siigo():
    data = request.json
    filters=data['filters']
    labels_roaroe=[]
    if filters['brokers']!=[]:
        reports = Reports_filters.query.filter_by(user_id=data["userId"],Año=str(filters['brokers'][0])).first()
        if reports==None:
            no_hay_data=True
            return jsonify({"saldo": [],"costoV":[],"costoM":[],"utilidad":[],"gastosAdmon":[],"gastosPer":[],"gastosHono":[],"gastosImp":[],"gastosArrend":[],"gastosServ":[],"gastosLegales":[],"gastosViaje":[],"gastosDiver":[],"margenBruto":[],"totalMargen":0.0,"labels":[],"crecimiento":[],"margenOperacional":[],"margenNeto":[],"porcentCostVentas":[],"gastosVentas":[],"porcentCostGastos":[],"crecimiento_ventas":0.0,"crecimiento_ventas2":0.0,"textoRadiaBarUltimo":"","textoRadiaBarAnterior":"","no_hay_data":no_hay_data})
        else:
            no_hay_data=False
        total_saldo = []
        total_saldo=eval(reports.saldos)
        ultimo_ingreso=len(total_saldo)-1
        total_costoV=eval(reports.costoV)
        n=0
        for i in total_costoV:
            total_costoV[n]=abs(i)
            n+=1
        total_costoM=eval(reports.costoM)
        total_utilidad=eval(reports.utilidad)
        gastosAdmon=eval(reports.gastosAdmon)
        gastosPer=eval(reports.gastosPer)
        gastosHono=eval(reports.gastosHono)
        gastosImp=eval(reports.gastosImp)
        gastosArrend=eval(reports.gastosArrend)
        gastosServ=eval(reports.gastosServ)
        gastosLegales=eval(reports.gastosLegales)
        gastosViaje=eval(reports.gastosViaje)
        gastosDiver=eval(reports.gastosDiver)
        margenBruto=eval(reports.margenBruto)
        margenOperacional=eval(reports.margenOperacional)
        margenNeto=eval(reports.margenNeto)
        gastosVentas=eval(reports.gastosVentas)
        roa=eval(reports.roa)
        roe=eval(reports.roe)
        #i=len(total_saldo)-1
        i=1
        crecimiento=[]
        crecimiento.append(0.0)
        try:
            while i<len(total_saldo):
                valorCrecim=round(float(((total_saldo[i]/total_saldo[i-1])-1)*100))
                crecimiento.append(valorCrecim)
                i=i+1
        except Exception as err:
            crecimiento.append(0.0)
        """
        try:
            valorCrecim1=int(((total_saldo[3]/total_saldo[2])-1)*100)
        except:
            valorCrecim1=0.0
        try:
            valorCrecim2=int(((total_saldo[2]/total_saldo[1])-1)*100)
        except:
            valorCrecim2=0.0
        try:
            valorCrecim3=int(((total_saldo[1]/total_saldo[0])-1)*100)
        except:
            valorCrecim3=0.0
        """
        i=0
        porcentCostVentas=[]
        try:
            while i<len(total_saldo):
                procentCostVentas=abs(round(float((total_costoV[i]/total_saldo[i])*100)))
                porcentCostVentas.append(procentCostVentas)
                i=i+1
        except Exception as err:
            porcentCostVentas.append(0.0)
        """
        try:
            procentCostVentas1=abs(int((total_costoV[0]/total_saldo[0])*100))
        except:
            procentCostVentas1=0.0
        try:
            procentCostVentas2=abs(int((total_costoV[1]/total_saldo[1])*100))
        except:
            procentCostVentas2=0.0
        try:
            procentCostVentas3=abs(int((total_costoV[2]/total_saldo[2])*100))
        except:
            procentCostVentas3=0.0 
        try:
            procentCostVentas4=abs(int((total_costoV[3]/total_saldo[3])*100))
        except:
            procentCostVentas4=0.0   
        """
        i=0
        porcentCostGastos=[]
        try:
            while i<len(gastosAdmon):
                procentCostGastos_=round(float(((gastosAdmon[i]+gastosVentas[i])/total_saldo[i])*100))
                porcentCostGastos.append(procentCostGastos_)
                i=i+1
        except Exception as err:
             porcentCostGastos.append(0.0)
        """
        try:
            procentCostGastos1=int(((gastosAdmon[0]+gastosVentas[0])/total_saldo[0])*100)
        except:
            procentCostGastos1=0.0
        try:
            procentCostGastos2=int(((gastosAdmon[1]+gastosVentas[1])/total_saldo[0])*100)
        except:
            procentCostGastos2=0.0
        try:
            procentCostGastos3=int(((gastosAdmon[2]+gastosVentas[2])/total_saldo[0])*100)
        except:
            procentCostGastos3=0.0 
        try:
            procentCostGastos4=int(((gastosAdmon[3]+gastosVentas[3])/total_saldo[0])*100)
        except:
            procentCostGastos4=0.0   
        """
        try:
            crecimiento_ventas=round((total_saldo[ultimo_ingreso]/total_saldo[ultimo_ingreso-1])*100,2)
        except:
            crecimiento_ventas=0.0
        try:
            crecimiento_ventas2=round((total_saldo[ultimo_ingreso-1]/total_saldo[ultimo_ingreso-2])*100,2)
        except:
            crecimiento_ventas2=0.0
        #crecimiento.append(0.0)
        """
        if valorCrecim1!=0.0:
            crecimiento.append(valorCrecim1)
        if valorCrecim2!=0.0:
            crecimiento.append(valorCrecim2)
        if valorCrecim3!=0.0:
            crecimiento.append(valorCrecim3)
        """
        """
        if procentCostVentas1!=0.0:
            porcentCostVentas.append(procentCostVentas1)
        if procentCostVentas2!=0.0:
            porcentCostVentas.append(procentCostVentas2)
        if procentCostVentas3!=0.0:
            porcentCostVentas.append(procentCostVentas3)
        if procentCostVentas4!=0.0:
            porcentCostVentas.append(procentCostVentas4)
        """    
        """
        if procentCostGastos1!=0.0:
            porcentCostGastos.append(procentCostGastos1)
        if procentCostGastos2!=0.0:
            porcentCostGastos.append(procentCostGastos2)
        if procentCostGastos3!=0.0:
            porcentCostGastos.append(procentCostGastos3)
        if procentCostGastos4!=0.0:
            porcentCostGastos.append(procentCostGastos4)
        """
       
        max_gastosVentas=max(gastosVentas)
        max_gastosAdmon=max(gastosAdmon)+max_gastosVentas
        max_saldo=max(total_saldo)+max_gastosAdmon
        
        max_costosVentas=max(total_costoV)
        max_saldoCostos=max(total_saldo)+max_costosVentas
        textoRadiaBarUltimo="4-3"
        textoRadiaBarAnterior="3-2"
        labels=['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']
        mes=0
        while mes<len(roa):
         labels_roaroe.append(labels[mes])
         mes+=1
        #total_margen_bruto=float(margenBruto[0])+float(margenBruto[1])+float(margenBruto[2])+float(margenBruto[3])
        total_margen_bruto=0.0
    else:
        reports = Reports.query.filter_by(user_id=data["userId"]).first()
        if reports==None:
            no_hay_data=True
            return jsonify({"saldo": [],"costoV":[],"costoM":[],"utilidad":[],"gastosAdmon":[],"gastosPer":[],"gastosHono":[],"gastosImp":[],"gastosArrend":[],"gastosServ":[],"gastosLegales":[],"gastosViaje":[],"gastosDiver":[],"margenBruto":[],"totalMargen":0.0,"labels":[],"crecimiento":[],"margenOperacional":[],"margenNeto":[],"porcentCostVentas":[],"gastosVentas":[],"porcentCostGastos":[],"crecimiento_ventas":0.0,"crecimiento_ventas2":0.0,"textoRadiaBarUltimo":"","textoRadiaBarAnterior":"","no_hay_data":no_hay_data})
        else:
            no_hay_data=False
        AÑO_2021=eval(reports.AÑO_2021)
        AÑO_2022=eval(reports.AÑO_2022)
        AÑO_2023=eval(reports.AÑO_2023)
        AÑO_2024=eval(reports.AÑO_2024)
        costov1=AÑO_2021[1]*-1
        costov2=AÑO_2022[1]*-1
        costov3=AÑO_2023[1]*-1
        costov4=AÑO_2024[1]*-1
        total_saldo=[AÑO_2021[0],AÑO_2022[0],AÑO_2023[0],AÑO_2024[0]]
        total_costoV=[costov1,costov2,costov3,costov4]
        total_costoM=[AÑO_2021[2],AÑO_2022[2],AÑO_2023[2],AÑO_2024[2]]
        total_utilidad=[AÑO_2021[3],AÑO_2022[3],AÑO_2023[3],AÑO_2024[3]]
        gastosAdmon=[AÑO_2021[4],AÑO_2022[4],AÑO_2023[4],AÑO_2024[4]]
        gastosPer=[AÑO_2021[5],AÑO_2022[5],AÑO_2023[5],AÑO_2024[5]]
        gastosHono=[AÑO_2021[6],AÑO_2022[6],AÑO_2023[6],AÑO_2024[6]]
        gastosImp=[AÑO_2021[7],AÑO_2022[7],AÑO_2023[7],AÑO_2024[7]]
        gastosArrend=[AÑO_2021[8],AÑO_2022[8],AÑO_2023[8],AÑO_2024[8]]
        gastosServ=[AÑO_2021[9],AÑO_2022[9],AÑO_2023[9],AÑO_2024[9]]
        gastosLegales=[AÑO_2021[10],AÑO_2022[10],AÑO_2023[10],AÑO_2024[10]]
        gastosViaje=[AÑO_2021[11],AÑO_2022[11],AÑO_2023[11],AÑO_2024[11]]
        gastosDiver=[AÑO_2021[12],AÑO_2022[12],AÑO_2023[12],AÑO_2024[12]]
        margenBruto=[AÑO_2021[13],AÑO_2022[13],AÑO_2023[13],AÑO_2024[13]]
        margenOperacional=[AÑO_2021[14],AÑO_2022[14],AÑO_2023[14],AÑO_2024[14]]
        margenNeto=[AÑO_2021[15],AÑO_2022[15],AÑO_2023[15],AÑO_2024[15]]
        gastosVentas=[AÑO_2021[16],AÑO_2022[16],AÑO_2023[16],AÑO_2024[16]]
        roa=[AÑO_2021[17],AÑO_2022[17],AÑO_2023[17],AÑO_2024[17]]
        roe=[AÑO_2021[18],AÑO_2022[18],AÑO_2023[18],AÑO_2024[18]]
        try:
            valorCrecim1=round(float(((AÑO_2022[0]/AÑO_2021[0])-1)*100))
        except:
            valorCrecim1=0.0
        try:
            valorCrecim2=round(float(((AÑO_2023[0]/AÑO_2022[0])-1)*100))
        except:
            valorCrecim2=0.0
        try:
            valorrCrecim3=round(float(((AÑO_2024[0]/AÑO_2023[0])-1)*100))
        except:
            valorrCrecim3=0.0
        try:
            procentCostVentas1=abs(round(float((AÑO_2021[1]/AÑO_2021[0])*100)))
        except:
            procentCostVentas1=0.0
        try:
            procentCostVentas2=abs(round(float((AÑO_2022[1]/AÑO_2022[0])*100)))
        except:
            procentCostVentas2=0.0
        try:
            procentCostVentas3=abs(round(float((AÑO_2023[1]/AÑO_2023[0])*100)))
        except:
            procentCostVentas3=0.0 
        try:
            procentCostVentas4=abs(round(float((AÑO_2024[1]/AÑO_2024[0])*100)))
        except:
            procentCostVentas4=0.0   
            
            
        try:
            procentCostGastos1=round(float(((AÑO_2021[4]+AÑO_2021[16])/AÑO_2021[0])*100))
        except:
            procentCostGastos1=0.0
        try:
            procentCostGastos2=round(float(((AÑO_2022[4]+AÑO_2022[16])/AÑO_2022[0])*100))
        except:
            procentCostGastos2=0.0
        try:
            procentCostGastos3=round(float(((AÑO_2023[4]+AÑO_2023[16])/AÑO_2023[0])*100))
        except:
            procentCostGastos3=0.0 
        try:
            procentCostGastos4=round(float(((AÑO_2024[4]+AÑO_2024[16])/AÑO_2024[0])*100))
        except:
            procentCostGastos4=0.0   
        try:
            crecimiento_ventas=round((AÑO_2024[0]/AÑO_2023[0])*100,2)
        except:
            crecimiento_ventas=0.0
        try:
            crecimiento_ventas2=round((AÑO_2023[0]/AÑO_2022[0])*100,2)
        except Exception as err:
            crecimiento_ventas2=0.0
        textoRadiaBarUltimo="2024-2023"
        textoRadiaBarAnterior="2023-2022"
        crecimiento=[0.0,valorCrecim1,valorCrecim2,valorrCrecim3]
        porcentCostVentas=[procentCostVentas1,procentCostVentas2,procentCostVentas3,procentCostVentas4]
        porcentCostGastos=[procentCostGastos1,procentCostGastos2,procentCostGastos3,procentCostGastos4]
        labels=['2021','2022','2023','2024']
        año=0
        while año<len(roa):
         labels_roaroe.append(labels[año])
         año+=1
        
        max_gastosVentas=max(gastosVentas)
        max_gastosAdmon=max(gastosAdmon)+max_gastosVentas
        max_saldo=max(total_saldo)+max_gastosAdmon
        
        max_costosVentas=max(total_costoV)
        max_saldoCostos=max(total_saldo)+max_costosVentas
        #total_margen_bruto=float(margenBruto[0])+float(margenBruto[1])+float(margenBruto[2])+float(margenBruto[3])
        total_margen_bruto=0.0
    return jsonify({"saldo": total_saldo,"costoV":total_costoV,"costoM":total_costoM,"utilidad":total_utilidad,"gastosAdmon":gastosAdmon,"gastosPer":gastosPer,"gastosHono":gastosHono,"gastosImp":gastosImp,"gastosArrend":gastosArrend,"gastosServ":gastosServ,"gastosLegales":gastosLegales,"gastosViaje":gastosViaje,"gastosDiver":gastosDiver,"margenBruto":margenBruto,"totalMargen":total_margen_bruto,"labels":labels,"crecimiento":crecimiento,"margenOperacional":margenOperacional,"margenNeto":margenNeto,"porcentCostVentas":porcentCostVentas,"gastosVentas":gastosVentas,"porcentCostGastos":porcentCostGastos,"crecimiento_ventas":crecimiento_ventas,"crecimiento_ventas2":crecimiento_ventas2,"textoRadiaBarUltimo":textoRadiaBarUltimo,"textoRadiaBarAnterior":textoRadiaBarAnterior,"no_hay_data":no_hay_data,'max_saldo':max_saldo,"max_gastosVentas":max_gastosVentas,"max_gastosAdmon":max_gastosAdmon,"max_saldoCostos":max_saldoCostos,"roa":roa,"roe":roe,"labels_roaroe":labels_roaroe})
    
@app.route("/api/get-reports", methods=["POST"])
def get_reports():
    data = request.json
    trades = Trades.query.filter_by(user_id=data["userId"]).all()
    selectedIds = data["selected"]
    brokers = data["broker"]
    accountIds = data["accountId"]
    symbols = data["symbol"]
    status = data["status"]
    trades.sort(key=sort_by_date)
    total_return_x = []
    total_return_y = []
    total_return = 0
    total_return_net = 0
    total_return_net_array = []
    total_dates = []
    daily_return = []
    temp_date = ""
    return_winner = []
    return_winner_total = 0
    return_loser = []
    return_loser_total = 0
    return_long = []
    return_short = []
    return_long_total = 0
    return_short_total = 0
    biggestProfit = 0
    biggestLose = 0
    biggestPercentProfit = 0
    percentProfits = []
    percentLoses = []
    biggestPercentLose = 0
    closed_trades = []
    closed_trades_total = 0
    open_trades = []
    open_trades_total = 0
    daily_trades = []
    win_count = 0
    loss_count = 0
    win_total = []
    loss_total = []
    be_count = 0
    be_total = []
    return_percent_series = []   
    return_percent_total = 0
    ordenes=[]
    for trade in trades:
        ordenesDict={'open_date':trade.open_date,'status':trade.status}
        ordenes.append(ordenesDict)
        print(trade.status)
        if len(selectedIds) > 0 and not trade.trade_id in selectedIds:
            continue
        if len(brokers) > 0 and not trade.broker in brokers:
            continue
        if len(accountIds) > 0 and not trade.account_id in accountIds:
            continue
        if len(symbols) > 0 and not trade.symbol in symbols:
            continue
        if len(status) > 0 and not trade.status in status:
            continue
        total_return_x.append(trade.open_date[0:10])
        total_return += float(trade.ret)
        total_return_y.append(total_return)
        total_return_net += float(trade.ret_net)
        total_return_net_array.append(total_return_net)
        return_percent_total += float(trade.ret_percent)
        return_percent_series.append(return_percent_total)
        if trade.open_date[0:10] == temp_date:
            daily_return[-1] += float(trade.ret)
            daily_trades[-1] += 1
            if float(trade.ret) == 0:
                be_total[-1] += 1
                be_count += 1
            if trade.status == "WIN" or trade.status == "LOSS":
                closed_trades[-1] += 1
                closed_trades_total += 1
                if trade.status == "WIN":
                    win_total[-1] += 1
                    win_count += 1
                else:
                    loss_total[-1] += 1
                    loss_count += 1
            else:
                open_trades[-1] += 1
                open_trades_total += 1
        else:
            total_dates.append(trade.open_date[0:10])
            daily_return.append(float(trade.ret))
            daily_trades.append(1)
            if trade.status == "WIN" or trade.status == "LOSS":
                closed_trades.append(1)
                closed_trades_total += 1
                open_trades.append(0)
                if trade.status == "WIN":
                    win_count += 1
                    win_total.append(1)
                    loss_total.append(0)
                else:
                    loss_count += 1
                    win_total.append(0)
                    loss_total.append(1)
            else:
                closed_trades.append(0)
                open_trades.append(1)
                open_trades_total += 1
            if float(trade.ret) == 0:
                be_total.append(1)
                be_count += 1
            else:
                be_total.append(0)
            temp_date = trade.open_date[0:10]
        if trade.status == "WIN":
            return_winner.append(float(trade.ret))
            return_winner_total += float(trade.ret)
            percentProfits.append(float(trade.ret_percent))
        else:
            return_loser.append(float(trade.ret))
            return_loser_total += float(trade.ret)
            percentLoses.append(float(trade.ret_percent))
        if trade.side == "LONG":
            return_long.append(float(trade.ret))
            return_long_total += float(trade.ret)
        else:
            return_short.append(float(trade.ret))
            return_short_total += float(trade.ret)
        if float(trade.ret) > biggestProfit:
            biggestProfit = float(trade.ret)
        if float(trade.ret) < biggestLose:
            biggestLose = float(trade.ret)
        if float(trade.ret_percent) > biggestPercentProfit:
            biggestPercentProfit = float(trade.ret_percent)
        if float(trade.ret_percent) < biggestPercentLose:
            biggestPercentLose = float(trade.ret_percent)
    saldo=data_ai(ordenes)
    return jsonify({"totalReturnY": total_return_y, "totalReturnX": total_return_x, "totalReturn": total_return, "totalReturnNet": total_return_net, "totalReturnNetArray": total_return_net_array, "totalDates": total_dates, "dailyReturn": daily_return, "returnWin": return_winner, "returnWinTotal": return_winner_total, "returnLose": return_loser, "returnLoseTotal": return_loser_total, "returnLong": return_long, "returnLongTotal": return_long_total, "returnShort": return_short, "returnShortTotal": return_short_total, "biggestProfit": biggestProfit, "biggestLose": biggestLose, "totalClosedTrades": closed_trades_total, "closedTrades": closed_trades, "totalOpenTrades": open_trades_total, "openTrades": open_trades, "totalTrades": len(total_return_x), "dailyTrades": daily_trades, "totalWinner": win_count, "totalLoser": loss_count, "dailyWinners": win_total, "dailyLosers": loss_total, "beCount": be_count, "dailyBe": be_total, "returnPercentSeries": return_percent_series, "returnPercentTotal": return_percent_total, "biggestPercentProfit": biggestPercentProfit, "biggestPercentLose": biggestPercentLose, "percentProfits": percentProfits, "percentLoses": percentLoses, "saldo":saldo})

def pie_chart(df,col, title):
    """
    Parametros:
    ----------
    df : pandas dataframe
    col (string): nombre de la columna del dataframe 
    title (string): título del gráfico 
    
    Resultado:
    -------
    Despliega un gráfico de torta con las etiquetas y la proporción 
    (%) de los datos
    """
    counts = df[col].value_counts()
    counts.plot(kind='pie',autopct='%.0f%%',fontsize=20, figsize=(6, 6))
    plt.title(title)
    plt.show() 
    

def data_ai(orders):
    headers ={
               "Content-Type":"application/json",
               "Authorization":"eyJhbGciOiJSUzI1NiIsImtpZCI6IjExNDQzRDg2OUYxMzgwODlEREUwOTdENTNBN0YxNzVCNkQwNzIxNzdSUzI1NiIsInR5cCI6ImF0K2p3dCIsIng1dCI6IkVVUTlocDhUZ0luZDRKZlZPbjhYVzIwSElYYyJ9.eyJuYmYiOjE3MTg5Mzk0MjksImV4cCI6MTcyMTUzMTQyOSwiaXNzIjoiaHR0cDovL21zLXNlY3VyaXR5OjUwMDAiLCJhdWQiOiJodHRwOi8vbXMtc2VjdXJpdHk6NTAwMC9yZXNvdXJjZXMiLCJjbGllbnRfaWQiOiJTaWlnb0FQSSIsInN1YiI6Ijk1MjA5OSIsImF1dGhfdGltZSI6MTcxODkzOTQyOSwiaWRwIjoibG9jYWwiLCJuYW1lIjoic2VydmljaW9hbGNsaWVudGVAc29hZ3JvLm5ldCIsIm1haWxfc2lpZ28iOiJzZXJ2aWNpb2FsY2xpZW50ZUBzb2Fncm8ubmV0IiwiY2xvdWRfdGVuYW50X2NvbXBhbnlfa2V5IjoiU09BR1JPU09MVUNJT05FU0FHUk9QRUNVQVJJQVNTQVMiLCJ1c2Vyc19pZCI6IjM3NCIsInRlbmFudF9pZCI6IjB4MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAzNjc4NTUiLCJ1c2VyX2xpY2Vuc2VfdHlwZSI6IjAiLCJwbGFuX3R5cGUiOiIxNCIsInRlbmFudF9zdGF0ZSI6IjEiLCJtdWx0aXRlbmFudF9pZCI6IjM3MSIsImNvbXBhbmllcyI6IjAiLCJhcGlfc3Vic2NyaXB0aW9uX2tleSI6IjA5OTU1NDkwMGY4MjQxNDU5YzU0YzJhZTQwZmJmYjgwIiwiYXBpX3VzZXJfY3JlYXRlZF9hdCI6IjE3MTI2OTQ4NTciLCJhY2NvdW50YW50IjoiZmFsc2UiLCJqdGkiOiJEMUYzRDAxMDIyMTA2MkRFQTc2MTVENTNGMTA0NkM3QiIsImlhdCI6MTcxODkzOTQyOSwic2NvcGUiOlsiU2lpZ29BUEkiXSwiYW1yIjpbImN1c3RvbSJdfQ.HQ6ac2a5Xg_hl6VXb1Lox564fnmX_qBh74rWaGsN68ULyXSXsG6Vs5ysu_Qp1Y2skqUxqg7czWwW18tLzCUwRxRRHIsmDmjr76p1eANzjvT7sdrov3rHXWbRGSL21uQ08RoF9nymcHZ_aJaGvSf9tfBfqkkfWreENDyjOQv548A_-RaPdUZ5bKhXCFBvXIUdA17CkhUA90G4QtAVdc4SCVj8o4DROkFd29_LyRHQCW4Ij_3RBAmG0VmArjlthdaPCJk2swUzllT8lYUvvxvXwZboM1ffbt0XSHx52F_BRQ8cClRlE5qz1ue3YsQMIwva62eOPlFWiUxq2zUNOrpvrw",
               "Partner-Id":"sigo"
             }
    year=[2021,2022,2023,2024]
    monthStart=1
    monthEnd=3
    saldo=[]
    while monthStart < 12:
        params={
          "account_start": "",
          "account_end": "",
          "year": 2023,
          "month_start": monthStart,
          "month_end": monthEnd,
          "includes_tax_difference": False
        }
        monthStart=monthEnd
        monthEnd+=3
        try:
            response = requests.request("POST", "https://api.siigo.com/v1/test-balance-report", headers=headers,json=params).json()
            urlArchivo=response['file_url']  
            print(urlArchivo)
            response = requests.get(urlArchivo)
            
            
            with open('balance_general.xlsx', 'wb') as file:
                 file.write(response.content)
            #webbrowser.get(chrome_path).open(urlArchivo)
            print("exito")
        except Exception as err:
            print("error")  
        
        
        df = pd.read_excel('balance_general.xlsx',header=8,engine='openpyxl')
        df.columns = ['Nivel',
                     'Transaccional','Codigo','Nombre','Saldo','Movimiento','Movimiento cred','Saldo final']
        df[df=='Saldo final']=np.nan
        df = df.fillna(0)
        df['Saldo final']=df['Saldo final'].astype(str)
        print(df['Saldo final'])
        df[df=='Codigo']=np.nan
        df = df.fillna(0)
        print(df['Codigo'])
        df['Codigo']=df['Codigo'].astype(int)
        print(df['Codigo'])
        cont = df[df['Codigo'] == 41]
        print(cont['Saldo final'])
        numero=abs(float(cont['Saldo final']))
        saldo.append(numero)
    
    print("los saldos de los años son ",saldo)
    return saldo

@app.route("/create")
def createdb():
    db.create_all()
    return "db created"


@app.route("/get-filter-item", methods=["POST"])
def getfilteritem():
    data = request.json
    trades = Trades.query.filter_by(user_id=data["userId"]).all()
    available_brokers = []
    available_symbols = []
    broker_account = []
    for trade in trades:
        if not trade.broker in available_brokers:
            available_brokers.append(trade.broker)
        temp = {"broker": trade.broker, "account": trade.account_id, "symbol": trade.symbol}
        if not temp in available_symbols:
            available_symbols.append(temp)
    if len(available_brokers) > 0:
        for broker in available_brokers:
            available_accounts = []
            trades_broker = Trades.query.filter_by(user_id=data["userId"], broker=broker).all()
            for trade_broker in trades_broker:
                if not trade_broker.account_id in available_accounts:
                    available_accounts.append(trade_broker.account_id)
                    broker_account.append(
                        broker + " " + available_accounts[-1])
    return jsonify({"brokers": ['2022','2023','2024'], "symbols": available_symbols, "status": ["WIN", "LOSS"]})


if __name__ == '__main__':
    if os.environ.get("DEBUG_MODE") == "TRUE":
        app.run(debug=True)
    else:
        app.run()
