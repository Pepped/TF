from flask import Flask
from pymongo import MongoClient
from bson.objectid import ObjectId

def media_rank(menu,locale,piatto,voto_x):

    voti=menu.find({'locale':ObjectId(locale),'nome_p':piatto}).distinct('voti')
    s1=menu.find({'locale':ObjectId(locale),'nome_p':piatto}).distinct('s1')
    s2=menu.find({'locale':ObjectId(locale),'nome_p':piatto}).distinct('s2')
    s3=menu.find({'locale':ObjectId(locale),'nome_p':piatto}).distinct('s3')
    s4=menu.find({'locale':ObjectId(locale),'nome_p':piatto}).distinct('s4')
    s5=menu.find({'locale':ObjectId(locale),'nome_p':piatto}).distinct('s5')

    num=(float(s1[0])+float(s2[0])*2+float(s3[0])*3+float(s4[0])*4+float(s5[0])*5+voto_x)/(float(voti[0])+1)

    rating="{0:.1f}".format(num)

    return rating

