# -*- coding: utf-8 -*-
#------------------------------------------------------------
# Regex de Pordede para PalcoTV
# Version 0.1 (29/12/2015)
#------------------------------------------------------------
# License: GPL (http://www.gnu.org/licenses/gpl-3.0.html)
# Librerías Plugintools por Jesús (www.mimediacenter.info)
# By Aquilesserr
# Creditos a juarrox y Quequino

import urlparse,urllib2,urllib,re
import os, sys

import xbmc
import xbmcgui
import xbmcaddon
import xbmcplugin

import plugintools
import requests

import traceback
from resources.tools.resolvers import *

web = "http://www.pordede.com"
referer = "http://www.pordede.com/"
fanart = 'http://1.bp.blogspot.com/-KyT4YY-bcUY/VLf3_liTSWI/AAAAAAAABSI/mHgCLqONXfc/s1600/apertura-pordede.jpg'
thumbnail = 'http://www.pordede.com/images/logo.png' 
post = "LoginForm[username]="+plugintools.get_setting("pordede_user")+"&LoginForm[password]="+plugintools.get_setting("pordede_pwd")
DEFAULT_HEADERS = []
DEFAULT_HEADERS.append( ["User-Agent","Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; es-ES; rv:1.9.2.12) Gecko/20101026 Firefox/3.6.12"] )
DEFAULT_HEADERS.append( ["Referer","http://www.pordede.com"] )

sc = "[COLOR white]";ec = "[/COLOR]"
sc2 = "[COLOR palegreen]";ec2 = "[/COLOR]"
sc3 = "[COLOR green]";ec3 = "[/COLOR]"
sc4 = "[COLOR red]";ec4 = "[/COLOR]"
sc5 = "[COLOR gold]";ec5 = "[/COLOR]"

def pdd_findvideos(params):
    plugintools.log("[%s %s] Parser Pordede %s" % (addonName, addonVersion, repr(params)))

    page_url = params.get("page")
    plugintools.log("URL= "+page_url)

    if plugintools.get_setting("pordede_user") == "":
        plugintools.add_item(action="", title="Habilita tu cuenta de pordede en la configuración", folder=False, isPlayable=False)
    else:
        url = "http://www.pordede.com/site/login"
        post = "LoginForm[username]="+plugintools.get_setting("pordede_user")+"&LoginForm[password]="+plugintools.get_setting("pordede_pwd")
        headers = DEFAULT_HEADERS[:]
       
        body,response_headers = plugintools.read_body_and_headers(url, post=post)
        
        try:
            if os.path.exists(temp+'pordede.com') is True:
                print "Eliminando carpeta caché..."
                os.remove(temp+'pordede.com')
        except: pass
        
        headers = DEFAULT_HEADERS[:]
        #headers.append(["X-Requested-With","XMLHttpRequest"])
        body,response_headers = plugintools.read_body_and_headers(page_url,headers=headers)
        #print body
        try:
            info_user = plugintools.find_single_match(body,'<div class="userinfo">(.*?)</div>')
            usuario = plugintools.find_single_match(info_user,'<div class="friendMini shadow" title="(.*?)"')
            avatar = plugintools.find_single_match(info_user,'src="(.*?)"')

            bloq_fich = plugintools.find_single_match(body,'<div class="sidebar">(.*?)<h2 class="info">Más información</h2>')
            logo = plugintools.find_single_match(bloq_fich,'onerror="this.src=\'/images/logo.png\'" src="(.*?)"')
            if logo =="":
                logo = thumbnail
            fondo = plugintools.find_single_match(body,'onerror="controller.noBigCover.*?src="(.*?)"')
            if fondo =="":
                fondo = fanart
            info_vid = plugintools.find_single_match(body,'<div class="main">(.*?)<div class="centered">')
            sinopsis = plugintools.find_single_match(info_vid,'style="max-height: 140px;overflow:hidden">(.*?)</div>').strip()
            datamovie = {}
            datamovie["Plot"] = sinopsis
            if "peli" in page_url:
                title = plugintools.find_single_match(info_vid,'<h1>(.*?)</h1>').replace("&amp;","&").upper()
            elif "serie" in page_url:
                title = plugintools.find_single_match(info_vid,'<h1>(.*?)<span class="titleStatus">').replace("&amp;","&").upper()
            
            punt = plugintools.find_single_match(bloq_fich,'<span class="puntuationValue" data-value="(.*?)"')
            year_duration = plugintools.find_single_match(bloq_fich,'<p class="info">(.*?)</p>.*?<p class="info">(.*?)</p>')
            bloq_repart = plugintools.find_single_match(body,'<h2>reparto</h2>(.*?)class="viewmore"><span>')
            url_links = plugintools.find_single_match(info_vid,'<button class="defaultPopup big" href="(.*?)"')
            url_linksfull = web + url_links
            
            plugintools.add_item(action="",url="",title="[COLOR lightblue][B]Regex Pordede [/B][COLOR lightblue]"+sc4+"[I]*** By Palco Tv Team ***[/I]"+ec4,thumbnail=thumbnail,fanart=fanart,folder=False,isPlayable=False)
            plugintools.add_item(action="",url="",title=sc2+"Usuario: "+usuario+ec2,thumbnail=avatar,fanart=fanart,folder=False,isPlayable=False)
            plugintools.add_item(action="",url="",title="",thumbnail=logo,fanart=fondo,folder=False,isPlayable=False)
            plugintools.addPeli(action="",title=sc5+"[B]"+title+"[/B]"+ec5,plot="",url="",thumbnail=logo,fanart=fondo,info_labels=datamovie, isPlayable=False,folder=False)
            if url_links !="":
                plugintools.add_item(action="pordede_peli",url=url_linksfull,title=sc5+"Ir a los Enlaces >>"+ec5,thumbnail=logo,fanart=fondo,folder=True,isPlayable=False)
            else:
                plugintools.add_item(action="pordede_serie",url=page_url,title=sc5+"Ir a los Episodios >>"+ec5,thumbnail=logo,fanart=fondo,folder=True,isPlayable=False)

            plugintools.add_item(action="",url="",title=sc+"Puntuacion Usuarios Pordede: "+ec+sc3+punt+ec3,thumbnail=logo,fanart=fondo,folder=False,isPlayable=False)
            plugintools.add_item(action="",url="",title=sc+"Año: "+ec+sc3+year_duration[0]+ec3+"  "+sc+"Duracion: "+ec+sc3+year_duration[1]+ec3,thumbnail=logo,fanart=fondo,folder=False,isPlayable=False)
            plugintools.add_item(action="",url="",title=sc5+"Reparto: "+ec5,thumbnail=logo,fanart=fondo,folder=False,isPlayable=False)
            repart = plugintools.find_multiple_matches(bloq_repart,'<div class="starThumbnail">(.*?)<div class="star">')

            for item in repart:
                info = plugintools.find_single_match(item,'<a class="ellipsis defaultLink" href="([^"]+)">([^<]+)</a><br/><span>([^<]+)</span>')
                info1 = info[1].replace("&nbsp;",sc5+"No Hay Datos"+ec5).replace("&quot;"," ").replace("#","") 
                info2 = info[2].replace("&nbsp;",sc5+"No Hay Datos"+ec5).replace("&quot;"," ").replace("#","") 
                plugintools.add_item(action="",url="",title=sc+info1+": "+ec+sc3+info2+ec3,thumbnail=logo,fanart=fondo,folder=False,isPlayable=False)      
        except:
            pass
            errormsg = plugintools.message("Palco Tv",sc4+"!!!!Atención"+ec4+"[CR]Revise la url del video si persiste el Error[CR] el regex dejo de funcionar[CR]Palco Tv no puede cargar los datos.")
        
    params["thumbnail"] = logo
    params["fanart"] = fondo
    
                                                          
def pordede_peli(params):
    plugintools.log("[%s %s] Parser Pordede %s" % (addonName, addonVersion, repr(params)))

    url = params.get("url")
    logo = params.get("thumbnail")
    #post=user  #params.get("extra")
    plugintools.add_item(action="",url="",title="[COLOR lightblue][B]Regex Pordede [/B][COLOR lightblue]"+sc4+"[I]*** By Palco Tv Team ***[/I]"+ec4,thumbnail=thumbnail,fanart=fanart,folder=False,isPlayable=False)
    body,response_headers = plugintools.read_body_and_headers(url) 
    bloq_aport = plugintools.find_single_match(body,'<ul class="linksList">(.*?)<ul class="linksList">')
    aport = plugintools.find_multiple_matches(bloq_aport, '<a target="_blank" class="a aporteLink done"(.*?)</a>')

    for item in aport:
        link_ok = plugintools.find_single_match(item,'class="num green"><span data-num="(.*?)"')
        #print link_ok
        link_ko = plugintools.find_single_match(item,'class="num red"><span data-num="(.*?)"')
        #print link_ko
        if int(link_ok) >= int(link_ko):

            name_server = plugintools.find_single_match(item,'popup_(.*?)">').replace(".png","").capitalize()
            url = plugintools.find_single_match(item,'href="(.*?)"')
            url_aport = web+url
    
            idiomas = re.compile('<div class="flag([^"]+)">([^<]+)</div>',re.DOTALL).findall(item)
            idioma_0 = (idiomas[0][0].replace("&nbsp;","").strip() + " " + idiomas[0][1].replace("&nbsp;","").strip()).strip()
            if len(idiomas) > 1:
                idioma_1 = (idiomas[1][0].replace("&nbsp;","").strip() + " " + idiomas[1][1].replace("&nbsp;","").strip()).strip()
                idioma = idioma_0+" - "+idioma_1
            else:
                idioma_1 = ''
                idioma = idioma_0
            idioma=idioma.replace("spanish", "Esp").replace("english", "Eng").replace("spanish SUB", "Sub-Esp").replace("english SUB", "Sub-Eng").replace("german", "Ger")
            calidad_video = plugintools.find_single_match(item,'<div class="linkInfo quality"><i class="icon-facetime-video"></i>([^<]+)</div>').strip()
            calidad_audio = plugintools.find_single_match(item,'<div class="linkInfo qualityaudio"><i class="icon-headphones"></i>([^<]+)</div>').strip()
            title = sc+name_server+ec+" "+sc2+" ["+idioma+"] "+ec2+" "+sc3+"(OK: "+link_ok+") "+ec3+" "+sc4+"(KO: "+link_ko+") "+ec4+sc+"Video: "+ec+sc5+calidad_video+ec5+sc+"  Audio: "+ec+sc5+calidad_audio+ec5

            plugintools.add_item(action="pordede_link",url=url_aport,title=title,thumbnail=logo,fanart=fanart,extra=name_server,folder=False,isPlayable=True)

            params["url"] = url_aport
            params["title"] = sc+name_server+ec+" "+sc2+" ["+idioma+"] "+ec2+" "+sc3+"(OK: "+link_ok+") "+ec3+" "+sc4+"(KO: "+link_ko+") "+ec4+sc2+"Video: "+calidad_video+"  Audio: "+calidad_audio+ec2 
            params["extra"] = name_server

def pordede_serie(params):
    plugintools.log("[%s %s] Parser Pordede %s" % (addonName, addonVersion, repr(params)))

    url = params.get("url")
    logo = params.get("thumbnail")
    fondo = params.get("fanart")

    plugintools.add_item(action="",url="",title="[COLOR lightblue][B]Regex Pordede [/B][COLOR lightblue]"+sc4+"[I]*** By Palco Tv Team ***[/I]"+ec4,thumbnail=thumbnail,fanart=fanart,folder=False,isPlayable=False)
    headers = DEFAULT_HEADERS[:]
    body,response_headers = plugintools.read_body_and_headers(url,headers=headers)

    temporada = '<div class="checkSeason"[^>]+>([^<]+)<div class="right" onclick="controller.checkSeason(.*?)\s+</div></div>'
    itemtemporadas = re.compile(temporada,re.DOTALL).findall(body)

    for nombre_temporada,bloque_episodios in itemtemporadas:
        patron  = '<span class="title defaultPopup" href="([^"]+)"><span class="number">([^<]+)</span>([^<]+)</span>(\s*</div>\s*<span[^>]*><span[^>]*>[^<]*</span><span[^>]*>[^<]*</span></span><div[^>]*><button[^>]*><span[^>]*>[^<]*</span><span[^>]*>[^<]*</span></button><div class="action([^"]*)" data-action="seen">)?'
        matches = re.compile(patron,re.DOTALL).findall(bloque_episodios)
        num_temp = nombre_temporada.replace("Temporada","").replace("Extras","Extras 0")
        plugintools.add_item(action="",url="",title=sc2+"-- "+nombre_temporada+" --"+ec2,thumbnail=logo,fanart=fondo,folder=True,isPlayable=False)
        for item in matches:
            #print item
            title = item[2]
            titlefull = sc+num_temp+"x"+item[1]+" -- "+title+ec
            url = web+item[0]
            plugintools.add_item(action="pordede_peli",url=url,title=sc+titlefull+ec,thumbnail=logo,fanart=fondo,folder=True,isPlayable=False)
         
def pordede_link(params):
   
    name_server = params.get("extra")
    plugintools.log("Server= "+name_server)
    link = params.get("url")
    title = params.get("title")
    
    body,response_headers = plugintools.read_body_and_headers(link) #, post=post)
    goto = plugintools.find_single_match(body,'<p class="links">(.*?)target="_blank"')
    link_redirect = plugintools.find_single_match(goto,'<a href="(.*?)"')
    link_redirect = web + link_redirect
	
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0","Referer": link}
        body,response_headers = plugintools.read_body_and_headers(link_redirect) 
        #print body
        for i in response_headers:
		 if i[0]=='location':location=i[1]
        if location:print '$'*35,location,'$'*35
    
        if name_server =="Allmyvideos":
            media_url = location
            params["url"]=media_url
            allmyvideos(params)

        elif name_server =="Flashx":
            media_url = location
            params["url"]=media_url
            flashx(params)

        elif name_server =="Gamovideo":
            media_url = location
            params["url"]=media_url
            gamovideo(params)

        elif name_server =="Moevideos":
            media_url = location
            params["url"]=media_url
            moevideos(params)
        
        elif name_server =="Netutv":
            media_url = location
            params["url"]=media_url
            netu(params)   
               
        elif name_server =="Nowvideo":
            media_url = location
            params["url"]=media_url
            nowvideo(params)

        elif name_server =="Okru":
            media_url = location
            params["url"]=media_url
            okru(params)

        elif name_server =="Playedto":
            media_url = location
            params["url"]=media_url
            playedto(params)
                 
        elif name_server =="Powvideo":
           media_url = location
           params["url"]=media_url
           powvideo(params)

        elif name_server =="Rocvideo":
            media_url = location
            params["url"]=media_url
            rocvideo(params)

        elif name_server =="Streamable":
            media_url = location
            params["url"]=media_url
            streamable(params)
                      
        elif name_server =="Streamcloud":
            media_url = location
            params["url"]=media_url
            streamcloud(params)

        elif name_server =="Streaminto":
            media_url = location
            params["url"]=media_url
            streaminto(params)
                
        elif name_server =="Videomega":
            media_url = location
            params["url"]=media_url
            videomega(params)

        elif name_server =="Videott":
            media_url = location
            params["url"]=media_url
            videott(params)

        elif name_server =="Videoweed":
            media_url = location
            params["url"]=media_url
            videoweed(params)
            
        elif name_server =="Vidspot":
            media_url = location
            params["url"]=media_url
            vidspot(params)

        elif name_server =="Vidtome":
            media_url = location
            params["url"]=media_url
            vidtome(params)

        elif name_server =="Vk":
            media_url = location
            params["url"]=media_url
            vk(params)
                
    except: pass

# ------------------------------------------------------- @ By Aquilesserr PalcoTv Team ---------------------------------------------------


   
    
   


   
    


    
