# -*- coding: utf-8 -*-
#------------------------------------------------------------
# Parser de SeriesYonkis para PalcoTV
# Version 0.1 (22.04.2015)
#------------------------------------------------------------
# License: GPL (http://www.gnu.org/licenses/gpl-3.0.html)
# Gracias a las librerías de pelisalacarta de Jesús (www.mimediacenter.info)


import os
import sys
import urllib
import urllib2
import re

import xbmc
import xbmcgui
import xbmcaddon
import xbmcplugin

import re,urllib,urllib2,sys

import plugintools
from resources.tools.resolvers import *
from resources.tools.bers_sy import *

thumbnail = 'http://oi58.tinypic.com/1jwwo6.jpg'
fanart = 'http://st-listas.20minutos.es/images/2012-06/335200/list_640px.jpg?1368294762'
referer = 'http://www.seriesflv.com/'



def serie_capis(params):
    plugintools.log('[%s %s] serie_capis %s' % (addonName, addonVersion, repr(params)))

    bers_sy_on = plugintools.get_setting("bers_sy_on")
    bers_sy_level = plugintools.get_setting("bers_sy_level")
    plugintools.log("bers_sy_on= "+bers_sy_on)
    plugintools.log("bers_sy_level= "+bers_sy_level)
	
    if bers_sy_on == "true" and bers_sy_level == "1":  # Control para ejecutar el BERS para toda la serie
        bers_sy0(params)
    else:    
        datamovie={}
        if params.get("plot") != "":
                datamovie["Plot"]=params.get("plot")  # Cargamos sinopsis de la serie... (si existe)
        else:
                datamovie["Plot"]="."
       
        url = params.get("url")
        referer = 'http://www.seriesyonkis.sx/'
        request_headers=[]
        request_headers.append(["User-Agent","Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.65 Safari/537.31"])
        request_headers.append(["Referer", referer])
        data,response_headers = plugintools.read_body_and_headers(url, headers=request_headers)   

        #Carátula
        cover = plugintools.find_single_match(data, '<img src="([^"]+)')
        match_temporadas = plugintools.find_single_match(data, '<div id="section-content">(.*?)</ul>')
        temps = plugintools.find_multiple_matches(match_temporadas, '<h3 class="season"(.*?)</li>')
        
        for entry in temps:
            capis = plugintools.find_multiple_matches(entry, '<td class="episode-title">(.*?)</td>')
            for entri in capis:
                #plugintools.log("entri= "+entri)
                url_cap = plugintools.find_single_match(entri, 'href="([^"]+)')
                url_cap = 'http://www.seriesyonkis.sx'+url_cap
                #plugintools.log("url_cap= "+url_cap)
                num_cap = plugintools.find_single_match(entri, '<strong>(.*?)</strong>')
                num_cap = num_cap.strip()
                #plugintools.log("num_cap= "+num_cap)
                title_cap = plugintools.find_single_match(entri, '</strong>(.*?)</a>')
                title_cap = title_cap.strip()
                #plugintools.log("title_cap= "+title_cap)
                title_capi = '[COLOR orange][B]'+num_cap+'[/B][COLOR white]'+title_cap+'[/COLOR]'.strip()
                title_fixed = num_cap + title_cap
                title_fixed = title_fixed.strip()
                plugintools.add_item(action="enlaces_capi", title=title_capi, url = url_cap, thumbnail = cover , plot = datamovie["Plot"], info_labels = datamovie , fanart = fanart, folder = True, extra = title_fixed , isPlayable = False)


def enlaces_capi(params):
    plugintools.log('[%s %s] enlaces_capi %s' % (addonName, addonVersion, repr(params)))

    datamovie = {}
    datamovie["Plot"] = params.get("plot")

    url = params.get("url");print url
    title_fixed = params.get("extra")
    referer = 'http://www.seriesyonkis.sx/'
    request_headers=[]
    request_headers.append(["User-Agent","Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.65 Safari/537.31"])
    request_headers.append(["Referer", referer])    
    data,response_headers = plugintools.read_body_and_headers(url, headers=request_headers)   
    #plugintools.log("data= "+data)
    matches = plugintools.find_single_match(data, '<h2 class="header-subtitle veronline">(.*?)</table>')
    match_veronline = plugintools.find_single_match(matches, '<tbody>(.*?)</tbody>')
    match_links = plugintools.find_multiple_matches(match_veronline, '<tr>(.*?)</tr>')
    for entry in match_links:
        #plugintools.log("entry= "+entry)
        title_url = plugintools.find_single_match(entry, 'title="([^"]+)')
        page_url = plugintools.find_single_match(entry, '<a href="([^"]+)')
        server = plugintools.find_single_match(entry, 'watch via([^"]+)')
        #plugintools.log("server= "+server)
        idioma_capi = plugintools.find_single_match(entry, '<span class="flags(.*?)</span></td>')
        idioma_capi_fixed = idioma_capi.split(">")
        if len(idioma_capi_fixed) >= 2:
            idioma_capi = idioma_capi_fixed[1]
        #plugintools.log("idioma_capi= "+idioma_capi)
        if idioma_capi == "English":
            idioma_capi = ' [ENG]'
        elif idioma_capi == "english":
            idioma_capi = ' [ENG]'            
        elif idioma_capi == "Español":
            idioma_capi = ' [ESP]'
        elif idioma_capi == "Latino":
            idioma_capi = ' [LAT]'
        elif idioma_capi.find("English-Spanish SUBS") >= 0:
            idioma_capi = ' [VOSE]'
        elif idioma_capi.find("Japanese-Spanish SUBS") >= 0:
            idioma_capi = ' [VOSE]'
        else:
            idioma_capi = " [N/D]"
        #plugintools.log("idioma_capi= "+idioma_capi)        
        page_url = 'http://www.seriesyonkis.sx'+page_url
        #plugintools.log("page_url= "+page_url)        
        plot = datamovie["Plot"]
        source_web="seriesyonkis"
        bers_sy_on = plugintools.get_setting("bers_sy_on")  # Control para activar BERS para el capítulo
        
        if server.find("tumi.tv") >= 0:
            desc = '[Tumi]'
            title = title_fixed + ' [COLOR orange][I]'+desc+'[/I][/COLOR] [COLOR lightyellow][I]'+idioma_capi+'[/I][/COLOR]'
            plugintools.add_item(action="getlink", title = title , url = page_url , info_labels = datamovie , thumbnail = thumbnail , fanart = fanart, folder = False, isPlayable = True)
            if bers_sy_on == 1:
                bers_sy1(plot, title_fixed, title, title_serie, page_url, thumbnail, fanart, source_web)
                        
        elif server.find("streamin.to") >= 0:
            desc = '[Streamin.to]'
            title = title_fixed + ' [COLOR orange][I]'+desc+'[/I][/COLOR] [COLOR lightyellow][I]'+idioma_capi+'[/I][/COLOR]'
            plugintools.add_item(action="getlink", title = title , url = page_url , info_labels = datamovie, thumbnail = thumbnail , fanart = fanart, folder = False, isPlayable = True)
            if bers_sy_on == 1:  # Control para ejecutar BERS a nivel de capítulo
                bers_sy1(plot, title_fixed, title, title_serie, page_url, thumbnail, fanart, source_web)
                           
        elif server.find("vidspot") >= 0:
            desc = '[Vidspot]'
            title = title_fixed + ' [COLOR orange][I]'+desc+'[/I][/COLOR] [COLOR lightyellow][I]'+idioma_capi+'[/I][/COLOR]'
            plugintools.add_item(action="getlink", title = title , url = page_url , info_labels = datamovie, thumbnail = thumbnail , fanart = fanart, folder = False, isPlayable = True)
            if bers_sy_on == 1:  # Control para ejecutar BERS a nivel de capítulo
                bers_sy1(plot, title_fixed, title, title_serie, page_url, thumbnail, fanart, source_web)
                         
        elif server.find("allmyvideos") >= 0:
            desc = '[allmyvideos]'
            title = title_fixed + ' [COLOR orange][I]'+desc+'[/I][/COLOR] [COLOR lightyellow][I]'+idioma_capi+'[/I][/COLOR]'
            plugintools.add_item(action="getlink", title = title , url = page_url , info_labels = datamovie, thumbnail = thumbnail , fanart = fanart, folder = False, isPlayable = True)
            if bers_sy_on == 1:  # Control para ejecutar BERS a nivel de capítulo
                bers_sy1(plot, title_fixed, title, title_serie, page_url, thumbnail, fanart, source_web)
                      
        elif server.find("streamcloud") >= 0:
            desc = '[Streamcloud]'
            title = title_fixed + ' [COLOR orange][I]'+desc+'[/I][/COLOR] [COLOR lightyellow][I]'+idioma_capi+'[/I][/COLOR]'
            plugintools.add_item(action="getlink", title = title , url = page_url , info_labels = datamovie, thumbnail = thumbnail , fanart = fanart, folder = False, isPlayable = True)
            if bers_sy_on == 1:  # Control para ejecutar BERS a nivel de capítulo
                bers_sy1(plot, title_fixed, title, title_serie, page_url, thumbnail, fanart, source_web)
             
        elif server.find("nowvideo.sx") >= 0:
            desc = '[Nowvideo]'
            title = title_fixed + ' [COLOR orange][I]'+desc+'[/I][/COLOR] [COLOR lightyellow][I]'+idioma_capi+'[/I][/COLOR]'
            plugintools.add_item(action="getlink", title = title , url = page_url , info_labels = datamovie, thumbnail = thumbnail , fanart = fanart, folder = False, isPlayable = True)
            if bers_sy_on == 1:  # Control para ejecutar BERS a nivel de capítulo
                bers_sy1(plot, title_fixed, title, title_serie, page_url, thumbnail, fanart, source_web)
                           
        elif server.find("veehd") >= 0:
            desc = '[VeeHD]'
            title = title_fixed + ' [COLOR orange][I]'+desc+'[/I][/COLOR] [COLOR lightyellow][I]'+idioma_capi+'[/I][/COLOR]'
            plugintools.add_item(action="getlink", title =title, url = page_url , info_labels = datamovie, thumbnail = thumbnail , fanart = fanart, folder = False, isPlayable = True)
            if bers_sy_on == 1:  # Control para ejecutar BERS a nivel de capítulo
                bers_sy1(plot, title_fixed, title, title_serie, page_url, thumbnail, fanart, source_web)
            
        if server.find("allmyvideos") >= 0:
            desc = '[Allmyvideos]'
            title = title_fixed + ' [COLOR orange][I]'+desc+'[/I][/COLOR] [COLOR lightyellow][I]'+idioma_capi+'[/I][/COLOR]'            
            plugintools.add_item(action="getlink", title = title , url = page_url , info_labels = datamovie , thumbnail = thumbnail , fanart = fanart, folder = False, isPlayable = True)
            if bers_sy_on == 1:  # Control para ejecutar BERS a nivel de capítulo
                bers_sy1(plot, title_fixed, title, title_serie, page_url, thumbnail, fanart, source_web)
            
        elif server.find("novamov.com") >= 0:
            desc = '[Novamov]'
            title = title_fixed + ' [COLOR orange][I]'+desc+'[/I][/COLOR] [COLOR lightyellow][I]'+idioma_capi+'[/I][/COLOR]'            
            plugintools.add_item(action="getlink", title = title , url = page_url , info_labels = datamovie, thumbnail = thumbnail , fanart = fanart, folder = False, isPlayable = True)
            if bers_sy_on == 1:  # Control para ejecutar BERS a nivel de capítulo
                bers_sy1(plot, title_fixed, title, title_serie, page_url, thumbnail, fanart, source_web)
                           
        elif server.find("Moevideos") >= 0:
            desc = '[Vidspot]'
            title = title_fixed + ' [COLOR orange][I]'+desc+'[/I][/COLOR] [COLOR lightyellow][I]'+idioma_capi+'[/I][/COLOR]'
            plugintools.add_item(action="getlink", title = title , url = page_url , info_labels = datamovie, thumbnail = thumbnail , fanart = fanart, folder = False, isPlayable = True)
            if bers_sy_on == 1:  # Control para ejecutar BERS a nivel de capítulo
                bers_sy1(plot, title_fixed, title, title_serie, page_url, thumbnail, fanart, source_web)
                         
        elif server.find("Gamovideo") >= 0:
            desc = '[allmyvideos]'
            title = title_fixed + ' [COLOR orange][I]'+desc+'[/I][/COLOR] [COLOR lightyellow][I]'+idioma_capi+'[/I][/COLOR]'
            plugintools.add_item(action="getlink", title = title , url = page_url , info_labels = datamovie, thumbnail = thumbnail , fanart = fanart, folder = False, isPlayable = True)
            if bers_sy_on == 1:  # Control para ejecutar BERS a nivel de capítulo
                bers_sy1(plot, title_fixed, title, title_serie, page_url, thumbnail, fanart, source_web)
                      
        elif server.find("movshare.net") >= 0:
            desc = '[Movshare]'
            title = title_fixed + ' [COLOR orange][I]'+desc+'[/I][/COLOR] [COLOR lightyellow][I]'+idioma_capi+'[/I][/COLOR]'
            plugintools.add_item(action="getlink", title = title , url = page_url , info_labels = datamovie, thumbnail = thumbnail , fanart = fanart, folder = False, isPlayable = True)
            if bers_sy_on == 1:  # Control para ejecutar BERS a nivel de capítulo
                bers_sy1(plot, title_fixed, title, title_serie, page_url, thumbnail, fanart, source_web)
                         
        elif server.find("played.to") >= 0:
            desc = '[Played.to]'
            title = title_fixed + ' [COLOR orange][I]'+desc+'[/I][/COLOR] [COLOR lightyellow][I]'+idioma_capi+'[/I][/COLOR]'
            plugintools.add_item(action="getlink", title = title , url = page_url , info_labels = datamovie, thumbnail = thumbnail , fanart = fanart, folder = False, isPlayable = True)
            if bers_sy_on == 1:  # Control para ejecutar BERS a nivel de capítulo
                bers_sy1(plot, title_fixed, title, title_serie, page_url, thumbnail, fanart, source_web)
               
        elif server.find("mail.ru") >= 0:
            desc = '[Mail.ru]'
            title = title_fixed + ' [COLOR orange][I]'+desc+'[/I][/COLOR] [COLOR lightyellow][I]'+idioma_capi+'[/I][/COLOR]'
            plugintools.add_item(action="getlink", title = title , url = page_url , info_labels = datamovie, thumbnail = thumbnail , fanart = fanart, folder = False, isPlayable = True)
            if bers_sy_on == 1:  # Control para ejecutar BERS a nivel de capítulo
                bers_sy1(plot, title_fixed, title, title_serie, page_url, thumbnail, fanart, source_web)

        elif server.find("vk") >= 0:
            desc = '[Vk]'
            title = title_fixed + ' [COLOR orange][I]'+desc+'[/I][/COLOR] [COLOR lightyellow][I]'+idioma_capi+'[/I][/COLOR]'
            plugintools.add_item(action="getlink", title = title , url = page_url , info_labels = datamovie, thumbnail = thumbnail , fanart = fanart, folder = False, isPlayable = True)
            if bers_sy_on == 1:  # Control para ejecutar BERS a nivel de capítulo
                bers_sy1(plot, title_fixed, title, title_serie, page_url, thumbnail, fanart, source_web)
            
        elif server.find("videobam") >= 0:
            desc = '[Videobam]'
            title = title_fixed + ' [COLOR orange][I]'+desc+'[/I][/COLOR] [COLOR lightyellow][I]'+idioma_capi+'[/I][/COLOR]'
            plugintools.add_item(action="getlink", title = title , url = page_url , info_labels = datamovie, thumbnail = thumbnail , fanart = fanart, folder = False, isPlayable = True)
            if bers_sy_on == 1:  # Control para ejecutar BERS a nivel de capítulo
                bers_sy1(plot, title_fixed, title, title_serie, page_url, thumbnail, fanart, source_web)

        elif server.find("powvideo.net") >= 0:
            desc = '[Powvideo]'
            title = title_fixed + ' [COLOR orange][I]'+desc+'[/I][/COLOR] [COLOR lightyellow][I]'+idioma_capi+'[/I][/COLOR]'
            plugintools.add_item(action="getlink", title = title , url = page_url , info_labels = datamovie, thumbnail = thumbnail , fanart = fanart, folder = False, isPlayable = True)
            if bers_sy_on == 1:  # Control para ejecutar BERS a nivel de capítulo
                bers_sy1(plot, title_fixed, title, title_serie, page_url, thumbnail, fanart, source_web)
				
        elif server.find("videoweed") >= 0:
            desc = '[Videoweed]'
            title = title_fixed + ' [COLOR orange][I]'+desc+'[/I][/COLOR] [COLOR lightyellow][I]'+idioma_capi+'[/I][/COLOR]'
            plugintools.add_item(action="getlink", title = title , url = page_url , info_labels = datamovie, thumbnail = thumbnail , fanart = fanart, folder = False, isPlayable = True)
            if bers_sy_on == 1:  # Control para ejecutar BERS a nivel de capítulo
                bers_sy1(plot, title_fixed, title, title_serie, page_url, thumbnail, fanart, source_web)

        elif server.find("streamable") >= 0:
            desc = '[Streamable]'
            title = title_fixed + ' [COLOR orange][I]'+desc+'[/I][/COLOR] [COLOR lightyellow][I]'+idioma_capi+'[/I][/COLOR]'
            plugintools.add_item(action="getlink", title = title , url = page_url , info_labels = datamovie, thumbnail = thumbnail , fanart = fanart, folder = False, isPlayable = True)
            if bers_sy_on == 1:  # Control para ejecutar BERS a nivel de capítulo
                bers_sy1(plot, title_fixed, title, title_serie, page_url, thumbnail, fanart, source_web)		

        elif server.find("rocvideo") >= 0:
            desc = '[Rocvideo]'
            title = title_fixed + ' [COLOR orange][I]'+desc+'[/I][/COLOR] [COLOR lightyellow][I]'+idioma_capi+'[/I][/COLOR]'
            plugintools.add_item(action="getlink", title = title , url = page_url , info_labels = datamovie, thumbnail = thumbnail , fanart = fanart, folder = False, isPlayable = True)
            if bers_sy_on == 1:  # Control para ejecutar BERS a nivel de capítulo
                bers_sy1(plot, title_fixed, title, title_serie, page_url, thumbnail, fanart, source_web)

        elif server.find("realvid") >= 0:
            desc = '[Realvid]'
            title = title_fixed + ' [COLOR orange][I]'+desc+'[/I][/COLOR] [COLOR lightyellow][I]'+idioma_capi+'[/I][/COLOR]'
            plugintools.add_item(action="getlink", title = title , url = page_url , info_labels = datamovie, thumbnail = thumbnail , fanart = fanart, folder = False, isPlayable = True)
            if bers_sy_on == 1:  # Control para ejecutar BERS a nivel de capítulo
                bers_sy1(plot, title_fixed, title, title_serie, page_url, thumbnail, fanart, source_web)
				
        elif server.find("Netu") >= 0:
            desc = '[Netu]'
            title = title_fixed + ' [COLOR orange][I]'+desc+'[/I][/COLOR] [COLOR lightyellow][I]'+idioma_capi+'[/I][/COLOR]'
            plugintools.add_item(action="getlink", title = title , url = page_url , info_labels = datamovie, thumbnail = thumbnail , fanart = fanart, folder = False, isPlayable = True)
            if bers_sy_on == 1:  # Control para ejecutar BERS a nivel de capítulo
                bers_sy1(plot, title_fixed, title, title_serie, page_url, thumbnail, fanart, source_web)

        elif server.find("videomega") >= 0:
            desc = '[Videomega]'
            title = title_fixed + ' [COLOR orange][I]'+desc+'[/I][/COLOR] [COLOR lightyellow][I]'+idioma_capi+'[/I][/COLOR]'
            plugintools.add_item(action="getlink", title = title , url = page_url , info_labels = datamovie, thumbnail = thumbnail , fanart = fanart, folder = False, isPlayable = True)
            if bers_sy_on == 1:  # Control para ejecutar BERS a nivel de capítulo
                bers_sy1(plot, title_fixed, title, title_serie, page_url, thumbnail, fanart, source_web)

        elif server.find("video.tt") >= 0:
            desc = '[Video.tt]'
            title = title_fixed + ' [COLOR orange][I]'+desc+'[/I][/COLOR] [COLOR lightyellow][I]'+idioma_capi+'[/I][/COLOR]'
            plugintools.add_item(action="getlink", title = title , url = page_url , info_labels = datamovie, thumbnail = thumbnail , fanart = fanart, folder = False, isPlayable = True)
            if bers_sy_on == 1:  # Control para ejecutar BERS a nivel de capítulo
                bers_sy1(plot, title_fixed, title, title_serie, page_url, thumbnail, fanart, source_web)

        elif server.find("flashx.tv") >= 0:
            desc = '[Flashx]'
            title = title_fixed + ' [COLOR orange][I]'+desc+'[/I][/COLOR] [COLOR lightyellow][I]'+idioma_capi+'[/I][/COLOR]'
            plugintools.add_item(action="getlink", title = title , url = page_url , info_labels = datamovie, thumbnail = thumbnail , fanart = fanart, folder = False, isPlayable = True)
            if bers_sy_on == 1:  # Control para ejecutar BERS a nivel de capítulo
                bers_sy1(plot, title_fixed, title, title_serie, page_url, thumbnail, fanart, source_web)

        elif server.find("youwatch") >= 0:
            desc = '[YouWatch]'
            title = title_fixed + ' [COLOR orange][I]'+desc+'[/I][/COLOR] [COLOR lightyellow][I]'+idioma_capi+'[/I][/COLOR]'
            plugintools.add_item(action="getlink", title = title , url = page_url , info_labels = datamovie, thumbnail = thumbnail , fanart = fanart, folder = False, isPlayable = True)
            if bers_sy_on == 1:  # Control para ejecutar BERS a nivel de capítulo
                bers_sy1(plot, title_fixed, title, title_serie, page_url, thumbnail, fanart, source_web)

        elif server.find("vidgg.to") >= 0:
            desc = '[Vidgg.to]'
            title = title_fixed + ' [COLOR orange][I]'+desc+'[/I][/COLOR] [COLOR lightyellow][I]'+idioma_capi+'[/I][/COLOR]'
            plugintools.add_item(action="getlink", title = title , url = page_url , info_labels = datamovie, thumbnail = thumbnail , fanart = fanart, folder = False, isPlayable = True)
            if bers_sy_on == 1:  # Control para ejecutar BERS a nivel de capítulo
                bers_sy1(plot, title_fixed, title, title_serie, page_url, thumbnail, fanart, source_web)

        elif server.find("vimple.ru") >= 0:
            desc = '[Vimple]'
            title = title_fixed + ' [COLOR orange][I]'+desc+'[/I][/COLOR] [COLOR lightyellow][I]'+idioma_capi+'[/I][/COLOR]'
            plugintools.add_item(action="getlink", title = title , url = page_url , info_labels = datamovie, thumbnail = thumbnail , fanart = fanart, folder = False, isPlayable = True)
            if bers_sy_on == 1:  # Control para ejecutar BERS a nivel de capítulo
                bers_sy1(plot, title_fixed, title, title_serie, page_url, thumbnail, fanart, source_web)

        elif server.find("idowatch") >= 0:
            desc = '[Idowatch]'
            title = title_fixed + ' [COLOR orange][I]'+desc+'[/I][/COLOR] [COLOR lightyellow][I]'+idioma_capi+'[/I][/COLOR]'
            plugintools.add_item(action="getlink", title = title , url = page_url , info_labels = datamovie, thumbnail = thumbnail , fanart = fanart, folder = False, isPlayable = True)
            if bers_sy_on == 1:  # Control para ejecutar BERS a nivel de capítulo
                bers_sy1(plot, title_fixed, title, title_serie, page_url, thumbnail, fanart, source_web)

        elif server.find("cloudtime") >= 0:
            desc = '[CloudTime]'
            title = title_fixed + ' [COLOR orange][I]'+desc+'[/I][/COLOR] [COLOR lightyellow][I]'+idioma_capi+'[/I][/COLOR]'
            plugintools.add_item(action="getlink", title = title , url = page_url , info_labels = datamovie, thumbnail = thumbnail , fanart = fanart, folder = False, isPlayable = True)
            if bers_sy_on == 1:  # Control para ejecutar BERS a nivel de capítulo
                bers_sy1(plot, title_fixed, title, title_serie, page_url, thumbnail, fanart, source_web)

        elif server.find("vidzi.tv") >= 0:
            desc = '[Vidzi.tv]'
            title = title_fixed + ' [COLOR orange][I]'+desc+'[/I][/COLOR] [COLOR lightyellow][I]'+idioma_capi+'[/I][/COLOR]'
            plugintools.add_item(action="getlink", title = title , url = page_url , info_labels = datamovie, thumbnail = thumbnail , fanart = fanart, folder = False, isPlayable = True)
            if bers_sy_on == 1:  # Control para ejecutar BERS a nivel de capítulo
                bers_sy1(plot, title_fixed, title, title_serie, page_url, thumbnail, fanart, source_web)

        elif server.find("vodlocker.com") >= 0:
            desc = '[VodLocker]'
            title = title_fixed + ' [COLOR orange][I]'+desc+'[/I][/COLOR] [COLOR lightyellow][I]'+idioma_capi+'[/I][/COLOR]'
            plugintools.add_item(action="getlink", title = title , url = page_url , info_labels = datamovie, thumbnail = thumbnail , fanart = fanart, folder = False, isPlayable = True)
            if bers_sy_on == 1:  # Control para ejecutar BERS a nivel de capítulo
                bers_sy1(plot, title_fixed, title, title_serie, page_url, thumbnail, fanart, source_web)

        elif server.find("streame.net") >= 0:
            desc = '[Streame.net]'
            title = title_fixed + ' [COLOR orange][I]'+desc+'[/I][/COLOR] [COLOR lightyellow][I]'+idioma_capi+'[/I][/COLOR]'
            plugintools.add_item(action="getlink", title = title , url = page_url , info_labels = datamovie, thumbnail = thumbnail , fanart = fanart, folder = False, isPlayable = True)
            if bers_sy_on == 1:  # Control para ejecutar BERS a nivel de capítulo
                bers_sy1(plot, title_fixed, title, title_serie, page_url, thumbnail, fanart, source_web)

        elif server.find("watchonline.to") >= 0:
            desc = '[WatchOnline]'
            title = title_fixed + ' [COLOR orange][I]'+desc+'[/I][/COLOR] [COLOR lightyellow][I]'+idioma_capi+'[/I][/COLOR]'
            plugintools.add_item(action="getlink", title = title , url = page_url , info_labels = datamovie, thumbnail = thumbnail , fanart = fanart, folder = False, isPlayable = True)
            if bers_sy_on == 1:  # Control para ejecutar BERS a nivel de capítulo
                bers_sy1(plot, title_fixed, title, title_serie, page_url, thumbnail, fanart, source_web)

        elif server.find("allvid.ch") >= 0:
            desc = '[AllVid]'
            title = title_fixed + ' [COLOR orange][I]'+desc+'[/I][/COLOR] [COLOR lightyellow][I]'+idioma_capi+'[/I][/COLOR]'
            plugintools.add_item(action="getlink", title = title , url = page_url , info_labels = datamovie, thumbnail = thumbnail , fanart = fanart, folder = False, isPlayable = True)
            if bers_sy_on == 1:  # Control para ejecutar BERS a nivel de capítulo
                bers_sy1(plot, title_fixed, title, title_serie, page_url, thumbnail, fanart, source_web)

        elif server.find("streamplay.to") >= 0:
            desc = '[StreamPlay]'
            title = title_fixed + ' [COLOR orange][I]'+desc+'[/I][/COLOR] [COLOR lightyellow][I]'+idioma_capi+'[/I][/COLOR]'
            plugintools.add_item(action="getlink", title = title , url = page_url , info_labels = datamovie, thumbnail = thumbnail , fanart = fanart, folder = False, isPlayable = True)
            if bers_sy_on == 1:  # Control para ejecutar BERS a nivel de capítulo
                bers_sy1(plot, title_fixed, title, title_serie, page_url, thumbnail, fanart, source_web)

        elif server.find("myvideoz.net") >= 0:
            desc = '[MyvideoZ]'
            title = title_fixed + ' [COLOR orange][I]'+desc+'[/I][/COLOR] [COLOR lightyellow][I]'+idioma_capi+'[/I][/COLOR]'
            plugintools.add_item(action="getlink", title = title , url = page_url , info_labels = datamovie, thumbnail = thumbnail , fanart = fanart, folder = False, isPlayable = True)
            if bers_sy_on == 1:  # Control para ejecutar BERS a nivel de capítulo
                bers_sy1(plot, title_fixed, title, title_serie, page_url, thumbnail, fanart, source_web)                  


def getlink(params):
    plugintools.log('[%s %s] getlink %s' % (addonName, addonVersion, repr(params)))  

    page_url = params.get("url")
    referer = 'http://www.seriesyonkis.sx/'
    request_headers=[]
    request_headers.append(["User-Agent","Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.65 Safari/537.31"])
    request_headers.append(["Referer", referer])    
    data,response_headers = plugintools.read_body_and_headers(page_url, headers=request_headers)   
    match = plugintools.find_single_match(data, '<table class="episodes full-width">(.*?)</table>')
    url_final = plugintools.find_single_match(match, '<a class="link p2" href="([^"]+)')
    if url_final.find("allmyvideos") >= 0:
        params["url"]=url_final
        allmyvideos(params)
    elif url_final.find("vidspot") >= 0:
        params["url"]=url_final
        vidspot(params)
    if url_final.find("played.to") >= 0:
        params["url"]=url_final
        playedto(params)        
    elif url_final.find("streamcloud") >= 0:
        params["url"]=url_final
        streamcloud(params)
    elif url_final.find("nowvideo.sx") >= 0:
        params["url"]=url_final
        nowvideo(params)
    elif url_final.find("streamin.to") >= 0:
        params["url"]=url_final
        streaminto(params)        
    elif url_final.find("veehd") >= 0:
        params["url"]=url_final
        veehd(params)
    elif url_final.find("novamov") >= 0:
        params["url"]=url_final
        novamov(params)
    elif url_final.find("gamovideo") >= 0:
        params["url"]=url_final
        gamovideo(params)
    elif url_final.find("moevideos") >= 0:
        params["url"]=url_final
        moevideos(params)
    elif url_final.find("movshare") >= 0:
        params["url"]=url_final
        movshare(params)
    elif url_final.find("movreel") >= 0:
        params["url"]=url_final
        movreel(params)	
    elif url_final.find("powvideo") >= 0:
        params["url"]=url_final
        powvideo(params)			
    elif url_final.find("vk") >= 0:
        params["url"]=url_final
        vk(params)
    elif url_final.find("tumi") >= 0:
        params["url"]=url_final
        tumi(params)
    elif url_final.find("mail.ru") >= 0:
        params["url"]=url_final
        mailru(params)
    elif url_final.find("vk") >= 0:
        params["url"]=url_final
        vk(params)
    elif url_final.find("videobam") >= 0:
        params["url"]=url_final
        videobam(params)        
    elif url_final.find("videoweed") >= 0:
        params["url"]=url_final
        videoweed(params)
    elif url_final.find("streamable") >= 0:
        params["url"]=url_final
        streamable(params)
    elif url_final.find("rocvideo") >= 0:
        params["url"]=url_final
        rocvideo(params)
    elif url_final.find("realvid") >= 0:
        params["url"]=url_final
        realvid(params)
    elif url_final.find("netu") >= 0:
        params["url"]=url_final
        netu(params)	
    elif url_final.find("videomega") >= 0:
        params["url"]=url_final
        videomega(params)
    elif url_final.find("video.tt") >= 0:
        params["url"]=url_final
        videott(params)
    elif url_final.find("flashx.tv") >= 0:
        params["url"]=url_final
        flashx(params)
    elif url_final.find("youwatch") >= 0:
        params["url"]=url_final
        youwatch(params)
    elif url_final.find("vidgg.to") >= 0:
        params["url"]=url_final
        vidggto(params)
    elif url_final.find("vimple.ru") >= 0:
        params["url"]=url_final
        vimple(params)
    elif url_final.find("idowatch") >= 0:
        params["url"]=url_final
        idowatch(params)
    elif url_final.find("cloudtime") >= 0:
        params["url"]=url_final
        cloudtime(params)
    elif url_final.find("vidzi.tv") >= 0:
        params["url"]=url_final
        vidzitv(params)
    elif url_final.find("vodlocker.com") >= 0:
        params["url"]=url_final
        vodlocker(params)
    elif url_final.find("streame.net") >= 0:
        params["url"]=url_final
        streamenet(params)
    elif url_final.find("watchonline.to") >= 0:
        params["url"]=url_final
        watchonline(params)
    elif url_final.find("allvid.ch") >= 0:
        params["url"]=url_final
        allvid(params)
    elif url_final.find("streamplay.to") >= 0:
        params["url"]=url_final
        streamplay(params)
    elif url_final.find("myvideoz.net") >= 0:
        params["url"]=url_final
        myvideoz(params)                                                                  

