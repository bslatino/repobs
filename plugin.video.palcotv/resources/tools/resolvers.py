# -*- coding: utf-8 -*-
#------------------------------------------------------------
# PalcoTV - Kodi Add-on by Juarrox (juarrox@gmail.com)
# Conectores multimedia para PalcoTV
#------------------------------------------------------------
# License: GPL (http://www.gnu.org/licenses/gpl-3.0.html)
# Gracias a las librerías de pelisalacarta de Jesús (www.mimediacenter.info)


import os
import sys
import urllib
import urllib2
import re
import string
import shutil
import zipfile
import time
import urlparse
import random
import xbmc
import xbmcgui
import xbmcaddon
import xbmcplugin
import scrapertools, plugintools, unpackerjs, requests, jsunpack, base64, json
import cookielib

addonName           = xbmcaddon.Addon().getAddonInfo("name")
addonVersion        = xbmcaddon.Addon().getAddonInfo("version")
addonId             = xbmcaddon.Addon().getAddonInfo("id")
addonPath           = xbmcaddon.Addon().getAddonInfo("path")

from __main__ import *
'''para UNPACK'''
from wiz import *

art = addonPath + "/art/"
playlists = xbmc.translatePath(os.path.join('special://home/userdata/playlists', ''))
temp = xbmc.translatePath(os.path.join('special://home/userdata/playlists/tmp', ''))




def urlr(url):
    plugintools.log('[%s %s] Probando URLR con... %s' % (addonName, addonVersion, url))

    import urlresolver
    host = urlresolver.HostedMediaFile(url)
    print 'host',host
    if host:
        resolver = urlresolver.resolve(url)
        print 'URLR',resolver
        return resolver
    else:
        xbmc.executebuiltin("Notification(%s,%s,%i,%s)" % ('PalcoTV', "URL Resolver: Servidor no soportado", 3 , art+'icon.png'))

 
   
def allmyvideos(params):
    plugintools.log('[%s %s] Allmyvideos %s' % (addonName, addonVersion, repr(params)))

    page_url = params.get("url")
    url_fixed = page_url.split("/")
    url_fixed = 'http://www.allmyvideos.net/' +  'embed-' + url_fixed[3] +  '.html'
    plugintools.log("url_fixed= "+url_fixed)

    # Leemos el código web
    headers = {'user-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14'}
    r = requests.get(page_url, headers=headers)
    data = r.text    

    if "<b>File Not Found</b>" in data or "<b>Archivo no encontrado</b>" in data or '<b class="err">Deleted' in data or '<b class="err">Removed' in data or '<font class="err">No such' in data:
        xbmc.executebuiltin("Notification(%s,%s,%i,%s)" % ('PalcoTV', "Archivo borrado!", 3 , art+'icon.png'))

    else:
        # Normaliza la URL
        videoid = page_url.replace("http://allmyvideos.net/","").replace("https://allmyvideos.net/","").strip()
        page_url = "http://allmyvideos.net/embed-"+videoid+"-728x400.html"
        r = requests.get(page_url, headers=headers)
        data = r.text

        if "File was banned" in data:
            payload = {'op': 'download1', 'usr_login': '', 'id': videoid, 'fname': '', 'referer': '', 'method_free': '1', 'x': '147', 'y': '25'}
            r = requests.get(page_url, params=payload)
            data = r.text            

        # Extrae la URL
        match = re.compile('"file" : "(.+?)",').findall(data)
        media_url = ""
        if len(match) > 0:
            for tempurl in match:
                if not tempurl.endswith(".png") and not tempurl.endswith(".srt"):
                    media_url = tempurl
                    print media_url

            if media_url == "":
                media_url = match[0]
                print media_url

        if media_url!="":
            media_url+= "&direct=false"
            plugintools.log("media_url= "+media_url)
            plugintools.play_resolved_url(media_url)


def streamcloud(params):
    plugintools.log('[%s %s]Streamcloud %s' % (addonName, addonVersion, repr(params)))

    url = params.get("url")

    request_headers=[]
    request_headers.append(["User-Agent","Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.65 Safari/537.31"])
    body,response_headers = plugintools.read_body_and_headers(url, headers=request_headers)
    plugintools.log("data= "+body)

    # Barra de progreso para la espera de 10 segundos
    progreso = xbmcgui.DialogProgress()
    progreso.create("PalcoTV", "Abriendo Streamcloud..." , url )

    i = 13000
    j = 0
    percent = 0
    while j <= 13000 :
        percent = ((j + ( 13000 / 10.0 )) / i)*100
        xbmc.sleep(i/10)  # 10% = 1,3 segundos
        j = j + ( 13000 / 10.0 )
        msg = "Espera unos segundos, por favor... "
        percent = int(round(percent))
        print percent
        progreso.update(percent, "" , msg, "")
        

    progreso.close()
    
    media_url = plugintools.find_single_match(body , 'file\: "([^"]+)"')
    
    if media_url == "":
        op = plugintools.find_single_match(body,'<input type="hidden" name="op" value="([^"]+)"')
        usr_login = ""
        id = plugintools.find_single_match(body,'<input type="hidden" name="id" value="([^"]+)"')
        fname = plugintools.find_single_match(body,'<input type="hidden" name="fname" value="([^"]+)"')
        referer = plugintools.find_single_match(body,'<input type="hidden" name="referer" value="([^"]*)"')
        hashstring = plugintools.find_single_match(body,'<input type="hidden" name="hash" value="([^"]*)"')
        imhuman = plugintools.find_single_match(body,'<input type="submit" name="imhuman".*?value="([^"]+)">').replace(" ","+")

        post = "op="+op+"&usr_login="+usr_login+"&id="+id+"&fname="+fname+"&referer="+referer+"&hash="+hashstring+"&imhuman="+imhuman
        request_headers.append(["Referer",url])
        body,response_headers = plugintools.read_body_and_headers(url, post=post, headers=request_headers)
        plugintools.log("data= "+body)
        

        # Extrae la URL
        media_url = plugintools.find_single_match( body , 'file\: "([^"]+)"' )
        plugintools.log("media_url= "+media_url)
        plugintools.play_resolved_url(media_url)

        if 'id="justanotice"' in body:
            plugintools.log("[streamcloud.py] data="+body)
            plugintools.log("[streamcloud.py] Ha saltado el detector de adblock")
            return -1

  

def playedto(params):
    plugintools.log('[%s %s] Played.to %s' % (addonName, addonVersion, repr(params)))

    url = params.get("url")
    url = url.split("/")
    url_fixed = "http://played.to/embed-" + url[3] +  "-640x360.html"
    plugintools.log("url_fixed= "+url_fixed)

    request_headers=[]
    request_headers.append(["User-Agent","Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.65 Safari/537.31"])
    body,response_headers = plugintools.read_body_and_headers(url_fixed, headers=request_headers)
    body = body.strip()
    
    if body == "<center>This video has been deleted. We apologize for the inconvenience.</center>":
        xbmc.executebuiltin("Notification(%s,%s,%i,%s)" % ('PalcoTV', "Enlace borrado...", 3 , art+'icon.png'))
    elif body.find("Removed for copyright infringement") >= 0:
        xbmc.executebuiltin("Notification(%s,%s,%i,%s)" % ('PalcoTV', "Removed for copyright infringement", 3 , art+'icon.png'))
    else:
        r = re.findall('file(.+?)\n', body)

        for entry in r:
            entry = entry.replace('",', "")
            entry = entry.replace('"', "")
            entry = entry.replace(': ', "")
            entry = entry.strip()
            plugintools.log("vamos= "+entry)
            if entry.endswith("flv"):
                plugintools.play_resolved_url(entry)
                xbmc.executebuiltin("Notification(%s,%s,%i,%s)" % ('PalcoTV', "Resolviendo enlace...", 3 , art+'icon.png'))
                params["url"]=entry
                plugintools.log("URL= "+entry)



def vidspot(params):
    plugintools.log('[%s %s] Vidspot %s' % (addonName, addonVersion, repr(params)))
    
    url = params.get("url")
    url = url.split("/")
    url_fixed = 'http://www.vidspot.net/' +  'embed-' + url[3] +  '.html'
    plugintools.log("url_fixed= "+url_fixed)

    # Leemos el código web
    headers = {'user-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14'}
    r = requests.get(url_fixed, headers=headers)
    body = r.text

    try:
        if body.find("File was deleted") >= 0:
            xbmc.executebuiltin("Notification(%s,%s,%i,%s)" % ('PalcoTV', "Archivo borrado", 3 , art+'icon.png'))
        else:
            r = re.findall('"file" : "(.+?)"', body)
            for entry in r:
                plugintools.log("vamos= "+entry)
                if entry.endswith("mp4?v2"):
                    url = entry + '&direct=false'
                    params["url"]=url
                    plugintools.log("url= "+url)
                    plugintools.play_resolved_url(url)
                    xbmc.executebuiltin("Notification(%s,%s,%i,%s)" % ('PalcoTV', "Resolviendo enlace...", 3 , art+'icon.png'))
    except:
            pass


				
def vk(params):
    plugintools.log('[%s %s] Vk %s' % (addonName, addonVersion, repr(params)))

    page_url = params.get("url")
    data = plugintools.read(page_url)
    plugintools.log("data= "+data)

    if "This video has been removed from public access" in data:
        xbmc.executebuiltin("Notification(%s,%s,%i,%s)" % ('PalcoTV', "Archivo borrado!", 3 , art+'icon.png'))
    else:
        data = plugintools.read(page_url.replace("amp;",""))
        plugintools.log("data= "+data)
        videourl = ""
        match = plugintools.find_single_match(data, r'vkid=([^\&]+)\&')
        print match
        vkid = ""

        # Lee la página y extrae el ID del vídeo
        data2 = data.replace("\\","")
        patron = '"vkid":"([^"]+)"'
        matches = re.compile(patron,re.DOTALL).findall(data2)
        if len(matches)>0:
            vkid = matches[0]
        else:
            plugintools.log("No encontró vkid")

        plugintools.log("vkid="+vkid)

        # Extrae los parámetros del vídeo y añade las calidades a la lista
        patron  = "var video_host = '([^']+)'.*?"
        patron += "var video_uid = '([^']+)'.*?"
        patron += "var video_vtag = '([^']+)'.*?"
        patron += "var video_no_flv = ([^;]+);.*?"
        patron += "var video_max_hd = '([^']+)'"
        matches = re.compile(patron,re.DOTALL).findall(data)
        print matches

        if len(matches)>0:
            #01:44:52 T:2957156352  NOTICE: video_host=http://cs509601.vk.com/, video_uid=149623387, video_vtag=1108941f4c, video_no_flv=1, video_max_hd=1

            video_host = matches[0][0]
            video_uid = matches[0][1]
            video_vtag = matches[0][2]
            video_no_flv = matches[0][3]
            video_max_hd = matches[0][4]
            
        else:
            #{"uid":"97482389","vid":"161509127\",\"oid\":\"97482389\","host":"507214",\"vtag\":\"99bca9d028\",\"ltag\":\"l_26f55018\",\"vkid\":\"161509127\",\"md_title\":\"El Libro de La Selva - 1967 - tetelx - spanish\",\"md_author\":\"Tetelx Tete\",\"hd\":1,\"no_flv\":1,\"hd_def\":-1,\"dbg_on\":0,\"t\":\"\",\"thumb\":\"http:\\\/\\\/cs507214.vkontakte.ru\\\/u97482389\\\/video\\\/l_26f55018.jpg\",\"hash\":\"3a576695e9f0bfe3093eb21239bd322f\",\"hash2\":\"be750b8971933dd6\",\"is_vk\":\"1\",\"is_ext\":\"0\",\"lang_add\":\"Add to My Videos\",\"lang_share\":\"Share\",\"lang_like\":\"Like\",\"lang_volume_on\":\"Unmute\",\"lang_volume_off\":\"Mute\",\"lang_volume\":\"Volume\",\"lang_hdsd\":\"Change Video Quality\",\"lang_fullscreen\":\"Full Screen\",\"lang_window\":\"Minimize\",\"lang_rotate\":\"Rotate\",\"video_play_hd\":\"Watch in HD\",\"video_stop_loading\":\"Stop Download\",\"video_player_version\":\"VK Video Player\",\"video_player_author\":\"Author - Alexey Kharkov\",\"goto_orig_video\":\"Go to Video\",\"video_get_video_code\":\"Copy vdeo code\",\"video_load_error\":\"The video has not uploaded yet or the server is not available\",\"video_get_current_url\":\"Copy frame link\",\"nologo\":1,\"liked\":0,\"add_hash\":\"67cd39a080ad6e0ad7\",\"added\":1,\"use_p2p\":0,\"p2p_group_id\":\"fb2d8cfdcbea4f3c\"}
            #01:46:05 T:2955558912  NOTICE: video_host=507214, video_uid=97482389, video_vtag=99bca9d028, video_no_flv=1, video_max_hd=1
            data2 = data.replace("\\","")
            video_host = scrapertools.get_match(data2,'"host":"([^"]+)"')
            video_uid = scrapertools.get_match(data2,'"uid":"([^"]+)"')
            video_vtag = scrapertools.get_match(data2,'"vtag":"([^"]+)"')
            video_no_flv = scrapertools.get_match(data2,'"no_flv":([0-9]+)')
            video_max_hd = scrapertools.get_match(data2,'"hd":([0-9]+)')
            
            if not video_host.startswith("http://"):
                video_host = "http://cs"+video_host+".vk.com/"

        plugintools.log("video_host="+video_host+", video_uid="+video_uid+", video_vtag="+video_vtag+", video_no_flv="+video_no_flv+", video_max_hd="+video_max_hd)

        video_urls = []

        if video_no_flv.strip() == "0" and video_uid != "0":
            tipo = "flv"
            if "http://" in video_host:
                videourl = "%s/u%s/video/%s.%s" % (video_host,video_uid,video_vtag,tipo)
            else:
                videourl = "http://%s/u%s/video/%s.%s" % (video_host,video_uid,video_vtag,tipo)
            
            # Lo añade a la lista
            video_urls.append( ["FLV [vk]",videourl])

        elif video_uid== "0" and vkid != "":     #http://447.gt3.vkadre.ru/assets/videos/2638f17ddd39-75081019.vk.flv 
            tipo = "flv"
            if "http://" in video_host:
                videourl = "%s/assets/videos/%s%s.vk.%s" % (video_host,video_vtag,vkid,tipo)
            else:
                videourl = "http://%s/assets/videos/%s%s.vk.%s" % (video_host,video_vtag,vkid,tipo)
            
            # Lo añade a la lista
            video_urls.append( ["FLV [vk]",videourl])
            
        else:                                   #http://cs12385.vkontakte.ru/u88260894/video/d09802a95b.360.mp4
            #Se reproducirá el stream encontrado de mayor calidad
            if video_max_hd=="3":
                plugintools.log("Vamos a por el vídeo 720p")
                if video_host.endswith("/"):
                    videourl = "%su%s/videos/%s.%s" % (video_host,video_uid,video_vtag,"720.mp4")
                else:
                    videourl = "%s/u%s/videos/%s.%s" % (video_host,video_uid,video_vtag,"720.mp4")
                plugintools.log("videourl= "+videourl)
            elif video_max_hd=="2":
                plugintools.log("Vamos a por el vídeo 480p")
                if video_host.endswith("/"):
                    videourl = "%su%s/videos/%s.%s" % (video_host,video_uid,video_vtag,"480.mp4")
                else:
                    videourl = "%s/u%s/videos/%s.%s" % (video_host,video_uid,video_vtag,"480.mp4")
                plugintools.log("videourl= "+videourl)
            elif video_max_hd=="1":
                plugintools.log("Vamos a por el vídeo 360p")
                if video_host.endswith("/"):
                    videourl = "%su%s/videos/%s.%s" % (video_host,video_uid,video_vtag,"360.mp4")
                else:
                    videourl = "%s/u%s/videos/%s.%s" % (video_host,video_uid,video_vtag,"360.mp4")
                plugintools.log("videourl= "+videourl) 
                
        plugintools.play_resolved_url(videourl)
        plugintools.log("videourl= "+videourl)





def nowvideo(params):
    plugintools.log('[%s %s] Nowvideo %s' % (addonName, addonVersion, repr(params)))

    data = plugintools.read(params.get("url"))
    #data = data.replace("amp;", "")
    #print data
    
    stepkey = plugintools.find_single_match(data, 'name="stepkey" value="(.*?)"')
    submit = "submit"
    post = 'stepkey='+stepkey+'&submit='+submit
    headers = {"User-Agent": 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; es-ES; rv:1.9.2.12) Gecko/20101026 Firefox/3.6.12', "Referer": params.get("url")}
    
    body,response_headers = plugintools.read_body_and_headers(params.get("url"),headers=headers, post=post,follow_redirects=True)
    data = body
    
    if "The file is being converted" in data:
        xbmc.executebuiltin("Notification(%s,%s,%i,%s)" % ('PalcoTV', "El archivo está en proceso", 3 , art+'icon.png'))
    elif "no longer exists" in data:
        xbmc.executebuiltin("Notification(%s,%s,%i,%s)" % ('PalcoTV', "El archivo ha sido borrado", 3 , art+'icon.png'))        
    else:
        #plugintools.log("data= "+data)
        domain = plugintools.find_single_match(data, 'flashvars.domain="([^"]+)"')
        video_id = plugintools.find_single_match(data, 'flashvars.file="([^"]+)"')
        filekey = plugintools.find_single_match(data, 'flashvars.filekey=([^;]+);')
    
        # En la página nos da el token de esta forma (siendo fkzd el filekey): var fkzd="83.47.1.12-8d68210314d70fb6506817762b0d495e";

        token_txt = 'var '+filekey
        #plugintools.log("token_txt= "+token_txt)
        token = plugintools.find_single_match(data, filekey+'=\"([^"]+)"')
        token = token.replace(".","%2E").replace("-","%2D")
        
        #plugintools.log("domain= "+domain)   
        #plugintools.log("video_id= "+video_id)
        #plugintools.log("filekey= "+filekey)
        #plugintools.log("token= "+token)
        
        if video_id == "":
            xbmc.executebuiltin("Notification(%s,%s,%i,%s)" % ('PalcoTV', "Error!", 3 , art+'icon.png'))
        else:
            #http://www.nowvideo.sx/api/player.api.php?user=undefined&pass=undefined&cid3=undefined&numOfErrors=0&cid2=undefined&key=83%2E47%2E1%2E12%2D8d68210314d70fb6506817762b0d495e&file=b5c8c44fc706f&cid=1
            url = 'http://www.nowvideo.sx/api/player.api.php?user=undefined&pass=undefined&cid3=undefined&numOfErrors=0&cid2=undefined&key=' + token + '&file=' + video_id + '&cid=1'
        
            #data = scrapertools.cache_page( url )
            # Vamos a lanzar una petición HTTP de esa URL
            r = requests.get(url)
            data = r.content

            referer = 'http://www.nowvideo.sx/'
            request_headers=[]
            request_headers.append(["User-Agent","Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.65 Safari/537.31"])
            request_headers.append(["Referer",referer])
            body,response_headers = plugintools.read_body_and_headers(url, headers=request_headers)
            # plugintools.log("data= "+body)
            # body= url=http://s173.coolcdn.ch/dl/04318aa973a3320b8ced6734f0c20da3/5440513e/ffe369cb0656c0b8de31f6ef353bcff192.flv&title=The.Black.Rider.Revelation.Road.2014.DVDRip.X264.AC3PLAYNOW.mkv%26asdasdas&site_url=http://www.nowvideo.sx/video/b5c8c44fc706f&seekparm=&enablelimit=0
            body = body.replace("url=", "")
            body = body.split("&")
            if len(body) >= 0:
                print 'body',body
                url = body[0]
                plugintools.play_resolved_url(url)
                xbmc.executebuiltin("Notification(%s,%s,%i,%s)" % ('PalcoTV', "Cargando vídeo...", 1 , art+'icon.png'))
            else:
                xbmc.executebuiltin("Notification(%s,%s,%i,%s)" % ('PalcoTV', "Error!", 3 , art+'icon.png'))


def tumi(params):
    plugintools.log('[%s %s] Tumi %s' % (addonName, addonVersion, repr(params)))

    page_url = params.get("url")
    data = scrapertools.cache_page(page_url)
    
    if "Video is processing now" in data:
        xbmc.executebuiltin("Notification(%s,%s,%i,%s)" % ('PalcoTV', "El archivo está en proceso", 3 , art+'icon.png'))       
    else:
        try:
            x = scrapertools.find_single_match(data, "\|type\|(.*?)\|file\|").replace("||","|").split("|")
            n = scrapertools.find_single_match(data, "//k.j.h.([0-9]+):g/p/v.o")

            printf = "http://%s.%s.%s.%s:%s/%s/%s.%s"
            if n:
                url = printf % (x[3], x[2], x[1],    n, x[0], x[8], "v", x[7])
            else:
                url = printf % (x[4], x[3], x[2], x[1], x[0], x[9], "v", x[8])
        except:
            url = scrapertools.find_single_match(data, "file:'([^']+)'")

        plugintools.log("url_final= "+url)
        plugintools.play_resolved_url(url)


            
def veehd(params):
    plugintools.log('[%s %s] VeeHD %s' % (addonName, addonVersion, repr(params)))
    
    uname = plugintools.get_setting("veehd_user")
    pword = plugintools.get_setting("veehd_pword")
    if uname == '' or pword == '':
        xbmc.executebuiltin("Notification(%s,%s,%i,%s)" % ('PalcoTV', "Debes configurar el identificador para Veehd.com", 3 , art+'icon.png'))
        return
    
    url = params.get("url")
    url_login = 'http://veehd.com/login'
    
    request_headers=[]
    request_headers.append(["User-Agent","Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.65 Safari/537.31"])
    request_headers.append(["Referer",url])
    
    post = {'ref': url, 'uname': uname, 'pword': pword, 'submit': 'Login', 'terms': 'on'}
    post = urllib.urlencode(post)
    
    body,response_headers = plugintools.read_body_and_headers(url_login, post=post, headers=request_headers, follow_redirects=True)
    vpi = plugintools.find_single_match(body, '"/(vpi.+?h=.+?)"')
    
    if not vpi:
        if 'type="submit" value="Login" name="submit"' in body:
            xbmc.executebuiltin("Notification(%s,%s,%i,%s)" % ('PalcoTV', "Error al identificarse en Veehd.com", 3 , art+'icon.png'))
        else:
            xbmc.executebuiltin("Notification(%s,%s,%i,%s)" % ('PalcoTV', "Error buscando el video en Veehd.com", 3 , art+'icon.png'))            
        return
    
    req = urllib2.Request('http://veehd.com/'+vpi)
    for header in request_headers:
        req.add_header(header[0], header[1]) # User-Agent
    response = urllib2.urlopen(req)
    body = response.read()
    response.close()

    va = plugintools.find_single_match(body, '"/(va/.+?)"')
    if va:
        req = urllib2.Request('http://veehd.com/'+va)
        for header in request_headers:
            req.add_header(header[0], header[1]) # User-Agent
        urllib2.urlopen(req)

    req = urllib2.Request('http://veehd.com/'+vpi)
    for header in request_headers:
        req.add_header(header[0], header[1]) # User-Agent
    response = urllib2.urlopen(req)
    body = response.read()
    response.close()

    video_url = False
    if 'application/x-shockwave-flash' in body:
        video_url = urllib.unquote(plugintools.find_single_match(body, '"url":"(.+?)"'))
    elif 'video/divx' in body:
        video_url = urllib.unquote(plugintools.find_single_match(body, 'type="video/divx"\s+src="(.+?)"'))

    if not video_url:
        xbmc.executebuiltin("Notification(%s,%s,%i,%s)" % ('PalcoTV', "Error abriendo el video en Veehd.com", 3 , art+'icon.png'))
        return

    plugintools.log("video_url= "+video_url)
    plugintools.play_resolved_url(video_url)

    


def turbovideos(params):
    plugintools.log('[%s %s] Turbovideos %s' % (addonName, addonVersion, repr(params)))
    url=params['url']
    try:
        url = url.replace('/embed-', '/')
        url = re.compile('//.+?/([\w]+)').findall(url)[0]
        url = 'http://turbovideos.net/embed-%s.html' % url

        #result = client.request(url)
        result = requests.get(url).content

        url = re.compile('file *: *"(.+?)"').findall(result)
        if len(url) > 0: plugintools.play_resolved_url(url[0])  

        result = re.compile('(eval.*?\)\)\))').findall(result)[-1]
        result = unpack(result)

        #url = client.parseDOM(result, 'embed', ret='src')
        url += re.compile("file *: *[\'|\"](.+?)[\'|\"]").findall(result)
        url = [i for i in url if not i.endswith('.srt')]
        url = url[0]

        plugintools.play_resolved_url(url)  
    except:
        return

def streaminto(params):
    plugintools.log('[%s %s] streaminto %s' % (addonName, addonVersion, repr(params)))

    page_url = params.get("url")
    if page_url.startswith("http://streamin.to/embed-") == False:
        videoid = plugintools.find_single_match(page_url,"streamin.to/([a-z0-9A-Z]+)")
        page_url = "http://streamin.to/embed-"+videoid+".html"

    plugintools.log("page_url= "+page_url)
    
    # Leemos el código web
    headers = {'user-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14'}
    r = requests.get(page_url, headers=headers)
    data = r.text
        
    plugintools.log("data= "+data)
    if data == "File was deleted":
        xbmc.executebuiltin("Notification(%s,%s,%i,%s)" % ('PalcoTV', "Archivo borrado!", 3 , art+'icon.png'))        
    else:        
        # TODO: Si "video not found" en data, mostrar mensaje "Archivo borrado!"
        patron_flv = 'file: "([^"]+)"'    
        patron_jpg = 'image: "(http://[^/]+/)'    
        try:
            host = scrapertools.get_match(data, patron_jpg)
            plugintools.log("[streaminto.py] host="+host)
            flv_url = scrapertools.get_match(data, patron_flv)
            plugintools.log("[streaminto.py] flv_url="+flv_url)
            flv = host+flv_url.split("=")[1]+"/v.flv"
            plugintools.log("[streaminto.py] flv="+flv)
            page_url = flv
        except:
            plugintools.log("[streaminto] opcion 2")
            op = plugintools.find_single_match(data,'<input type="hidden" name="op" value="([^"]+)"')
            plugintools.log("[streaminto] op="+op)
            usr_login = ""
            id = plugintools.find_single_match(data,'<input type="hidden" name="id" value="([^"]+)"')
            plugintools.log("[streaminto] id="+id)
            fname = plugintools.find_single_match(data,'<input type="hidden" name="fname" value="([^"]+)"')
            plugintools.log("[streaminto] fname="+fname)
            referer = plugintools.find_single_match(data,'<input type="hidden" name="referer" value="([^"]*)"')
            plugintools.log("[streaminto] referer="+referer)
            hashstring = plugintools.find_single_match(data,'<input type="hidden" name="hash" value="([^"]*)"')
            plugintools.log("[streaminto] hashstring="+hashstring)
            imhuman = plugintools.find_single_match(data,'<input type="submit" name="imhuman".*?value="([^"]+)"').replace(" ","+")
            plugintools.log("[streaminto] imhuman="+imhuman)
            
            import time
            time.sleep(10)
            
            # Lo pide una segunda vez, como si hubieras hecho click en el banner
            #op=download1&usr_login=&id=z3nnqbspjyne&fname=Coriolanus_DVDrip_Castellano_by_ARKONADA.avi&referer=&hash=nmnt74bh4dihf4zzkxfmw3ztykyfxb24&imhuman=Continue+to+Video
            post = "op="+op+"&usr_login="+usr_login+"&id="+id+"&fname="+fname+"&referer="+referer+"&hash="+hashstring+"&imhuman="+imhuman
            request_headers.append(["Referer",page_url])
            data_video = plugintools.read_body_and_headers( page_url , post=post, headers=request_headers )
            data_video = data_video[0]
            rtmp = plugintools.find_single_match(data_video, 'streamer: "([^"]+)"')
            print 'rtmp',rtmp
            video_id = plugintools.find_single_match(data_video, 'file: "([^"]+)"')
            print 'video_id',video_id
            swf = plugintools.find_single_match(data_video, 'src: "(.*?)"')
            print 'swf',swf
            page_url = rtmp+' swfUrl='+swf + ' playpath='+video_id+"/v.flv"  

        plugintools.play_resolved_url(page_url)    
    

def powvideo(params):
    plugintools.log('[%s %s] Powvideo %s' % (addonName, addonVersion, repr(params)))

    page_url = params.get("url")

    try:
        if not "embed" in page_url:
            page_url = page_url.replace("http://powvideo.net/","http://powvideo.net/embed-") + "-640x360.html"
      
        headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0', 'Referer': page_url, "Accept-Encoding": "gzip, deflate, sdch" }
        page_url= page_url.replace("embed","iframe")
    
        r = requests.get(page_url, headers=headers)
        data = r.text
        data = plugintools.find_single_match(data,"<script type='text/javascript'>(.*?)</script>")
        data = jsunpack.unpack(data)
        data = data.replace("\\","")
        media_url = plugintools.find_single_match(data,'\{.*(http.*mp4)').strip()
        
    except:
        media_url=urlr(page_url)
        print 'URLR',media_url
        
    plugintools.play_resolved_url(media_url)


def mailru(params):
    plugintools.log('[%s %s] Mail.ru %s' % (addonName, addonVersion, repr(params)))
    
    page_url = params.get("url")

    try:
        page_url = page_url.replace('/my.mail.ru/video/', '/api.video.mail.ru/videos/embed/')
        page_url = page_url.replace('/videoapi.my.mail.ru/', '/api.video.mail.ru/')
        result = getUrl(page_url).result
        url = re.compile('metadataUrl":"(.+?)"').findall(result)[0]
        cookie = getUrl(page_url, output='cookie').result
        h = "|Cookie=%s" % urllib.quote(cookie)
        result = getUrl(page_url).result
        result = data['videos']
        url = []
        url += [{'quality': '1080p', 'url': i['url'] + h} for i in result if i['key'] == '1080p']
        url += [{'quality': 'HD', 'url': i['url'] + h} for i in result if i['key'] == '720p']
        url += [{'quality': 'SD', 'url': i['url'] + h} for i in result if not (i['key'] == '1080p' or i ['key'] == '720p')]

    except:
        media_url=urlr(page_url)
        print 'URLR',media_url
        
    plugintools.play_resolved_url(media_url)



def mediafire(params):
    plugintools.log('[%s %s] Mediafire %s' % (addonName, addonVersion, repr(params)))

    # Solicitud de página web
    url = params.get("url")
    data = plugintools.read(url)

    # Espera un segundo y vuelve a cargar
    plugintools.log("[PalcoTV] Espere un segundo...")
    import time
    time.sleep(1)
    data = plugintools.read(url)
    plugintools.log("data= "+data)
    pattern = 'kNO \= "([^"]+)"'
    matches = re.compile(pattern,re.DOTALL).findall(data)
    for entry in matches:
        plugintools.log("entry= "+entry)
    # Tipo 1 - http://www.mediafire.com/download.php?4ddm5ddriajn2yo
    pattern = 'mediafire.com/download.php\?([a-z0-9]+)'
    matches = re.compile(pattern,re.DOTALL).findall(data)    
    for entry in matches:
        if entry != "":
            url = 'http://www.mediafire.com/?'+entry
            plugintools.log("URL Tipo 1 = "+url)
            
'''
    # Tipo 2 - http://www.mediafire.com/?4ckgjozbfid
    pattern  = 'http://www.mediafire.com/\?([a-z0-9]+)'
    matches = re.compile(pattern,re.DOTALL).findall(data)
    for entry in matches:
        if entry != "":
            url = 'http://www.mediafire.com/?'+entry
            plugintools.log("URL Tipo 2 = "+url)
        
    # Tipo 3 - http://www.mediafire.com/file/c0ama0jzxk6pbjl
    pattern  = 'http://www.mediafire.com/file/([a-z0-9]+)'
    plugintools.log("[mediafire.py] find_videos #"+pattern+"#")
    matches = re.compile(pattern,re.DOTALL).findall(data)
    for entry in matches:
        if entry != "":
            url = 'http://www.mediafire.com/?'+entry
            plugintools.log("URL Tipo 3 = "+url)

'''
            

def novamov(params):
    plugintools.log('[%s %s] Novamov %s' % (addonName, addonVersion, repr(params)))
    
    page_url = params.get("url")
    
    try:

        headers = {"Host": "www.novamov.com","User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0"}
        r=requests.get(page_url,headers=headers)
        data=r.content
    
        if "This file no longer exists on our servers" in data:
            xbmc.executebuiltin("Notification(%s,%s,%i,%s)" % ('PalcoTV', "Archivo borrado!", 3 , art+'icon.png'))
        else:
            videoid = plugintools.find_single_match(page_url,"http://www.novamov.com/video/([a-z0-9]+)")
            stepkey = plugintools.find_single_match(data,'name="stepkey" value="([^"]+)"')
            ref = page_url
            post = "stepkey="+stepkey+"&submit=submit"
            headers = {"Host": "www.novamov.com","User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0","Referer":page_url}
        
            body,response_headers = plugintools.read_body_and_headers(page_url, post=post)
        
            #http://www.novamov.com//api/player.api.php?key=87.218.124.147-49d804aa90e1b1e0d6c9f6032fefd671&numOfErrors=0&user=undefined&pass=undefined&cid=1&file=p2x88vrlfli8g&cid3=wholecloud.net&cid2=undefined
        
            stream_url = plugintools.find_single_match(body,'flashvars.filekey="(.*?)"')
            cid1 = plugintools.find_single_match(body,'flashvars.cid="(.*?)"')
            headers = {"Host": "www.novamov.com","User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0",
            "Referer":"http://www.novamov.com/player/cloudplayer.swf"} 
            url = "http://www.novamov.com/api/player.api.php?key="+stream_url+"&numOfErrors=0&user=undefined&pass=undefined&cid="+str(cid1)+"&file="+videoid+"&cid3=wholecloud.net&cid2=undefined"
            r=requests.get(url,headers=headers)
            data=r.content
        
            pass_err = plugintools.find_single_match(data,'url=(.*?)&title')
            new_url = url ="http://www.novamov.com/api/player.api.php?key="+stream_url+"&numOfErrors=1&user=undefined&errorUrl="+pass_err+"pass=undefined&cid="+str(cid1)+"&file="+videoid+"&cid3=wholecloud.net&cid2=undefined&errorCode=404"
            r=requests.get(new_url,headers=headers)
            data=r.content
            #print data                                                                                                                                                                                
            media_url = plugintools.find_single_match(data,'url=(.*?)&title')
            #print media_url
    except:
        media_url=urlr(page_url)
        print 'URLR',media_url    
      
    plugintools.play_resolved_url(media_url)

def gamovideo(params):
    plugintools.log('[%s %s] Gamovideo %s' % (addonName, addonVersion, repr(params)))

    page_url = params.get("url")

    try: 
        headers = {"Host": "gamovideo.com","User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8","Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate","DNT": "1",
        "Connection": "keep-alive","Cache-Control": "max-age=0"}
        r = requests.get(page_url, headers=headers)
        data = r.content 
        cookie=r.cookies['__cfduid']

        if "is no longer available" in data:
            xbmc.executebuiltin("Notification(%s,%s,%i,%s)" % ('PalcoTV', "Archivo borrado!", 3 , art+'icon.png'))
        else:
            headers = {"Host": "gamovideo.com","User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8","Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "gzip, deflate","DNT": "1",
            "Connection": "keep-alive","Cache-Control": "max-age=0","__cfduid": cookie}
            r = requests.get(page_url, headers=headers)
            data = r.content
            data = plugintools.find_single_match(data,"<script type='text/javascript'>(.*?)</script>")
            #plugintools.log("data="+data)
            data = unpackerjs.unpackjs(data)
            #plugintools.log("data="+data)
            #data=('jwplayer("vplayer").setup({playlist:[{image:"http://192.99.35.229:8777/i/01/00148/miix7zn7u9hc.jpg",sources:[{file:"rtmp://192.99.35.229:1935/vod?h=7ax22jyuf4pskjwff7lccf773d6us3gqlurfennmwxgl5frijnxmpxyc245a/mp4:54/0544528603_n.mp4?h=7ax22jyuf4pskjwff7lccf773d6us3gqlurfennmwxgl5frijnxmpxyc245a"},{file:"54/0544528603_n.mp4?h=7ax22jyuf4pskjwff7lccf773d6us3gqlurfennmwxgl5frijnxmpxyc245a"}],tracks:[]}],rtmp:{bufferlength:5},height:528,primary:"flash",width:950,captions:{color:\'#FFFFFF\',fontSize:15,fontFamily:"Verdana"}});var vvplay;var tt744083=0;var p0744083=0;jwplayer().onTime(function(x){if(p0744083>0)tt744083+=x.position-p0744083;p0744083=x.position;if(0!=0&&tt744083>=0){p0744083=-1;jwplayer().stop();jwplayer().setFullscreen(false);$(\'#play_limit_box\').show();$(\'div.video_ad\').show()}});jwplayer().onSeek(function(x){p0744083=-1});jwplayer().onPlay(function(x){doPlay(x)});jwplayer().onComplete(function(){$(\'div.video_ad\').show()});function doPlay(x){$(\'div.video_ad\').hide();if(vvplay)return;vvplay=1;}',,vvplayvvplay,
            #time.sleep(5)
        
            pstreamer = plugintools.find_single_match(data,'file\:"(.*?)"')
            playpath = plugintools.find_single_match(data,'file\:".*?file\:"(.*?)"')
            swf_url = "http://gamovideo.com/player61/jwplayer.flash.swf"
            pag_url = page_url 

            media_url = str(pstreamer) + " playpath="+ playpath
            # plugintools.log("media_url= "+media_url)
        
    except:
        media_url=urlr(page_url)
        print 'URLR',media_url
        
    plugintools.play_resolved_url(media_url)   



def moevideos(params):
    plugintools.log('[%s %s] Moevideos %s' % (addonName, addonVersion, repr(params)))

    # No existe / borrado: http://www.moevideos.net/online/27991
    page_url = params.get("url")
    data = scrapertools.cache_page(page_url)
    plugintools.log("data= "+data)
    if "<span class='tabular'>No existe</span>" in data:
        return False,"No existe o ha sido borrado de moevideos"
    else:
        # Existe: http://www.moevideos.net/online/18998
        patron  = "<span class='tabular'>([^>]+)</span>"
        headers = []
        headers.append(['User-Agent','Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14'])
        data = scrapertools.cache_page( page_url , headers=headers )            
        # Descarga el script (no sirve para nada, excepto las cookies)
        headers.append(['Referer',page_url])
        post = "id=1&enviar2=ver+video"
        data = scrapertools.cache_page( page_url , post=post, headers=headers )
        ### Modificado 12-6-2014
        #code = scrapertools.get_match(data,'flashvars\="file\=([^"]+)"')
        #<iframe width="860" height="440" src="http://moevideo.net/framevideo/16363.1856374b43bbd40c7f8d2b25b8e5?width=860&height=440" frameborder="0" allowfullscreen ></iframe>
        code = scrapertools.get_match(data,'<iframe width="860" height="440" src="http://moevideo.net/framevideo/([^\?]+)\?width=860\&height=440" frameborder="0" allowfullscreen ></iframe>')
        plugintools.log("code="+code)

        # API de letitbit
        headers2 = []
        headers2.append(['User-Agent','Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14'])
        ### Modificado 12-6-2014
        url = "http://api.letitbit.net"
        #url = "http://api.moevideo.net"
        #post = "r=%5B%22tVL0gjqo5%22%2C%5B%22preview%2Fflv%5Fimage%22%2C%7B%22uid%22%3A%2272871%2E71f6541e64b0eda8da727a79424d%22%7D%5D%2C%5B%22preview%2Fflv%5Flink%22%2C%7B%22uid%22%3A%2272871%2E71f6541e64b0eda8da727a79424d%22%7D%5D%5D"
        #post = "r=%5B%22tVL0gjqo5%22%2C%5B%22preview%2Fflv%5Fimage%22%2C%7B%22uid%22%3A%2212110%2E1424270cc192f8856e07d5ba179d%22%7D%5D%2C%5B%22preview%2Fflv%5Flink%22%2C%7B%22uid%22%3A%2212110%2E1424270cc192f8856e07d5ba179d%22%7D%5D%5D
        #post = "r=%5B%22tVL0gjqo5%22%2C%5B%22preview%2Fflv%5Fimage%22%2C%7B%22uid%22%3A%2268653%2E669cbb12a3b9ebee43ce14425d9e%22%7D%5D%2C%5B%22preview%2Fflv%5Flink%22%2C%7B%22uid%22%3A%2268653%2E669cbb12a3b9ebee43ce14425d9e%22%7D%5D%5D"
        post = 'r=["tVL0gjqo5",["preview/flv_image",{"uid":"'+code+'"}],["preview/flv_link",{"uid":"'+code+'"}]]'
        data = scrapertools.cache_page(url,headers=headers2,post=post)
        plugintools.log("data="+data)
        if ',"not_found"' in data:
            xbmc.executebuiltin("Notification(%s,%s,%i,%s)" % ('PalcoTV', "Archivo borrado!", 3 , art+'icon.png'))
        else:
            data = data.replace("\\","")
            plugintools.log("data="+data)
            patron = '"link"\:"([^"]+)"'
            matches = re.compile(patron,re.DOTALL).findall(data)
            video_url = matches[0]+"?ref=www.moevideos.net|User-Agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:15.0) Gecko/20100101 Firefox/15.0.1&Range=bytes:0-"
            plugintools.log("[moevideos.py] video_url="+video_url)

            video_urls = []
            video_urls.append( [ scrapertools.get_filename_from_url(video_url)[-4:] + " [moevideos]",video_url ] )
            plugintools.play_resolved_url(video_url[1])
     


def movshare(params):
    plugintools.log('[%s %s] Movshare %s' % (addonName, addonVersion, repr(params)))

    page_url = params.get("url")
    if "http://www.movshare.net/" in page_url:
        page_url = page_url.replace("http://www.movshare.net/","http://www.wholecloud.net/")

    try:

        headers = {"Host": "www.wholecloud.net","User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0"}
        r=requests.get(page_url,headers=headers)
        data=r.content
    
        if "This file no longer exists on our servers" in data:
            xbmc.executebuiltin("Notification(%s,%s,%i,%s)" % ('PalcoTV', "Archivo borrado!", 3 , art+'icon.png'))
        else:
            videoid = plugintools.find_single_match(page_url,"http://www.wholecloud.net/video/([a-z0-9]+)")
            stepkey = plugintools.find_single_match(data,'name="stepkey" value="([^"]+)"')
            ref = page_url
            post = "stepkey="+stepkey+"&submit=submit"
            headers = {"Host": "www.wholecloud.net","User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0","Referer":page_url}
        
            body,response_headers = plugintools.read_body_and_headers(page_url, post=post)
        
            #http://www.wholecloud.net/api/player.api.php?key=87.218.124.147-49d804aa90e1b1e0d6c9f6032fefd671&numOfErrors=0&user=undefined&pass=undefined&cid=1&file=p2x88vrlfli8g&cid3=wholecloud.net&cid2=undefined
        
            stream_url = plugintools.find_single_match(body,'flashvars.filekey="(.*?)"')
            cid1 = plugintools.find_single_match(body,'flashvars.cid="(.*?)"')
            headers = {"Host": "www.wholecloud.net","User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0",
            "Referer":"http://www.wholecloud.net/player/cloudplayer.swf"} 
            url = "http://www.wholecloud.net/api/player.api.php?key="+stream_url+"&numOfErrors=0&user=undefined&pass=undefined&cid="+str(cid1)+"&file="+videoid+"&cid3=wholecloud.net&cid2=undefined"
            r=requests.get(url,headers=headers)
            data=r.content
        
            pass_err = plugintools.find_single_match(data,'url=(.*?)&title')
            new_url = url ="http://www.wholecloud.net/api/player.api.php?key="+stream_url+"&numOfErrors=1&user=undefined&errorUrl="+pass_err+"pass=undefined&cid="+str(cid1)+"&file="+videoid+"&cid3=wholecloud.net&cid2=undefined&errorCode=404"
            r=requests.get(new_url,headers=headers)
            data=r.content
            #print data                                                                                                                                                                                
            media_url = plugintools.find_single_match(data,'url=(.*?)&title')
            #print media_url
    except:
        media_url=urlr(page_url)
        print 'URLR',media_url    
      
    plugintools.play_resolved_url(media_url)


def movreel(params):
    plugintools.log('[%s %s] Movreel %s' % (addonName, addonVersion, repr(params)))

    page_url = params.get("url")
    video_urls = []

    data = scrapertools.cache_page(page_url)

    op = plugintools.find_single_match(data,'<input type="hidden" name="op" value="([^"]+)">')
    file_code = plugintools.find_single_match(data,'<input type="hidden" name="file_code" value="([^"]+)">')
    w = plugintools.find_single_match(data,'<input type="hidden" name="w" value="([^"]+)">')
    h = plugintools.find_single_match(data,'<input type="hidden" name="h" value="([^"]+)">')
    method_free = plugintools.find_single_match(data,'<input type="submit" name="method_free" value="([^"]+)">')

    #op=video_embed&file_code=yrwo5dotp1xy&w=600&h=400&method_free=Close+Ad+and+Watch+as+Free+User
    #post = 'op=video_embed&file_code='+file_code+'+&w='+w+'&h='+h+'$method_free='+method_free
    post = urllib.urlencode( {"op":op,"file_code":file_code,"w":w,"h":h,"method_free":method_free} )
    print 'post',post

    data = scrapertools.cache_page(page_url,post=post)
    #plugintools.log("data="+data)
    data = unpackerjs.unpackjs(data)
    plugintools.log("data="+data)

    media_url = plugintools.find_single_match(data,'file\:"([^"]+)"')
    plugintools.play_resolved_url(media_url)

   
def videobam(params):
    plugintools.log('[%s %s] Videobam %s' % (addonName, addonVersion, repr(params)))
    page_url = params.get("url")
    data = scrapertools.cache_page(page_url)
    videourl = ""
    match = ""
    if "Video is processing" in data:
        xbmc.executebuiltin("Notification(%s,%s,%i,%s)" % ('PalcoTV', "Archivo no disponible temporalmente!", 3 , art+'icon.png'))
    else:
        patronHD = " high: '([^']+)'"
        matches = re.compile(patronHD,re.DOTALL).findall(data)
        for match in matches:
            videourl = match
            plugintools.log("Videobam HQ :"+match)

        if videourl == "":
            patronSD= " low: '([^']+)'"
            matches = re.compile(patronSD,re.DOTALL).findall(data)
            for match in matches:
                videourl = match
                plugintools.log("Videobam LQ :"+match)

            if match == "":
                if len(matches)==0:
                    # "scaling":"fit","url":"http:\/\/f10.videobam.com\/storage\/11\/videos\/a\/aa\/AaUsV\/encoded.mp4
                    patron = '[\W]scaling[\W]:[\W]fit[\W],[\W]url"\:"([^"]+)"'
                    matches = re.compile(patron,re.DOTALL).findall(data)
                    for match in matches:
                        videourl = match.replace('\/','/')
                        videourl = urllib.unquote(videourl)
                        plugintools.log("Videobam scaling: "+videourl)
                        if videourl != "":
                            plugintools.play_resolved_url(videourl)

        else:
            
            plugintools.play_resolved_url(videourl)


def vimeo(params):
    plugintools.log('[%s %s] Vimeo %s' % (addonName, addonVersion, repr(params)))

    page_url = params.get("url")
    ref = page_url
    
    headers = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'}
    r = requests.get(page_url,headers=headers)
    data = r.content

    '''
    data-config-url="http://player.vimeo.com/v2/video/63073570/config?autoplay=0&amp;byline=0&amp;bypass_privacy=1&amp;context=clip.main&amp;default_to_hd=1&amp;portrait=0&amp;title=0&amp;s=4268c7772994be693b480b75b5d84452f3e81f96" data-fallback-url="//player.vimeo.com/v2/video/63073570/fallback?js"
    '''
    url = plugintools.find_single_match(data,'data-config-url="([^"]+)"')
    # print url
    url = url.replace("&amp;","&")
    headers = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3',"Referer":ref}
    
    r = requests.get(url,headers=headers)
    data = r.content
    # print data
    json_object = json.loads(data)#jsontools.load_json(data)
    '''
    http://player.vimeo.com/v2/video/63073570/config?autoplay=0&byline=0&bypass_privacy=1&context=clip.main&default_to_hd=1&portrait=0&title=0&s=4268c7772994be693b480b75b5d84452f3e81f96
    '''
    media_urlsd = json_object['request']['files']['progressive'][0]['url']
    
    media_urlhd = json_object['request']['files']['progressive'][1]['url']
    
    if media_urlhd != "":
        media_url = media_urlhd
    else:
        media_url = media_urlsd

    plugintools.play_resolved_url(media_url)
    

def veetle(params):
    plugintools.log('[%s %s] Veetle %s' % (addonName, addonVersion, repr(params)))

    url = params.get("url")

    # Leemos el código web
    headers = {'user-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14'}
    r = requests.get(url, headers=headers)
    data = r.text
                
    # Obtenemos ID del canal de Veetle
    if url.startswith("http://veetle.com/index.php/channel/view") == True:  # http://veetle.com/index.php/channel/view#520c3ec32200c (la URL incluye el ID de Veetle)
        id_veetle=plugintools.find_single_match(url, 'view#([^/]+)')
        plugintools.log("id_veetle= "+id_veetle)
    elif url.startswith("http://veetle.com/?play=") == True:  # http://veetle.com/?play=7a1c4b6130984cc3bf239cafeff7d04e (hay que buscar ID del canal de Veetle)
        live_id=url.split("play=")[1]
        plugintools.log("live_id= "+live_id)
        id_veetle=plugintools.find_single_match(data, live_id+'/(.*?)_'+live_id)
        plugintools.log("id_veetle= "+id_veetle)

    # Buscamos enlaces de video...
    url_veetle='http://veetle.com/index.php/stream/ajaxStreamLocation/'+id_veetle+'/android-hls'
    headers = {'user-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14'}
    r = requests.get(url_veetle, headers=headers);data = r.text    
    url_veetle = plugintools.find_single_match(data, 'payload"."([^"]+)').replace("\\", "")
    if url_veetle == "":
        url_veetle='http://veetle.com/index.php/stream/ajaxStreamLocation/'+id_veetle+'/flash'
        headers = {'user-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14'}
        r = requests.get(url_veetle, headers=headers);data = r.text
        url_veetle = plugintools.find_single_match(data, 'payload"."([^"]+)').replace("\\", "")        
        
    plugintools.play_resolved_url(url_veetle)


def videoweed(params):
    plugintools.log('[%s %s] Videoweed %s' % (addonName, addonVersion, repr(params)))

    page_url = params.get("url")

    try:
        headers = {"Host": "www.videoweed.es","User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8","Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate","DNT": "1","Connection": "keep-alive"}

        r = requests.get(page_url, headers=headers)
        data = r.text
        # print data

        parametro = plugintools.find_single_match(data,'name="stepkey" value="([^"]+)"')
        post = "stepkey="+parametro+"&submit=submit"

        headers = {"Host": "www.videoweed.es","User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8","Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate","DNT": "1","Connection": "keep-alive","Referer": page_url}
        body,response_headers = plugintools.read_body_and_headers(page_url,headers=headers,post=post)
        #print body

        url = "http://www.videoweed.es/api/player.api.php?"
        cid3 = plugintools.find_single_match(body,'flashvars.cid3="([^"]+)"')
        if cid3 == "":
            cid3 = "videoweed.es"
        file_id = plugintools.find_single_match(body,'flashvars.file="([^"]+)"')
        filekey = plugintools.find_single_match(body,'flashvars.filekey="([^"]+)"').replace(".","%2E").replace("-","%2D")
        if filekey == "":
            filekey = plugintools.find_single_match(body,'fkz="([^"]+)"')
    
        parametros = "&numOfErrors=0&pass=undefined&user=undefined&cid2=undefined&cid=1"

        #http://www.videoweed.es/api/player.api.php?cid3=videoweed.es&file=721afa3d94047&key=87%2E223%2E231%2E193%2Dbd8b0ebd21171ba2e63d4b88a61ad5ab&numOfErrors=0&pass=undefined&user=undefined&cid2=undefined&cid=1
    
        urlfull = url+"cid3="+cid3+"&file="+file_id+"&key="+filekey+parametros
        ref = "http://www.videoweed.es/player/cloudplayer.swf"
        headers = {"Host": "www.videoweed.es","User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8","Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate","DNT": "1","Connection": "keep-alive","Referer": ref}
        r = requests.get(urlfull, headers=headers);data = r.text
    
        plugintools.log(data)
        media_url = plugintools.find_single_match(data,"url=(.*?)&title=")
        #url=http://s61.zerocdn.to/dl/5f9f71deefbb9ac3ead2b54f37806a3d/56786853/ff361cff09a7a5151e6323a05b84ba9345.flv&title=F4ST7HDTS.CASTELLANO8%26asdasdas&site_url=http://www.videoweed.es/file/721afa3d94047&seekparm=&enablelimit=0
    except:
        media_url=urlr(page_url)
        print 'URLR',media_url
        
    plugintools.play_resolved_url(media_url)


def streamable(params):
    plugintools.log('[%s %s] Streamable %s' % (addonName, addonVersion, repr(params)))

    url = params.get("url")
    headers = { "User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14", "Accept-Encoding": "gzip,deflate,sdch" }
    try:
        r = requests.get(url)
        data = r.content
    
        data = plugintools.find_single_match(data,'<embed(.*?)</embed>')
        data = plugintools.find_single_match(data,'setting=(.*?)"')
        import base64
        info_url= base64.b64decode(data)
        #print info_url
    
        r = requests.get(info_url)
        data = r.content
        # print data
    
        vcode = plugintools.find_single_match(data,'"vcode":"(.*?)",')
        st = plugintools.find_single_match(data,'"st":(.*?),')
        media_url = "http://video.streamable.ch/s?v="+vcode+"&t="+st
        media_url=media_url.strip()

    except:
        media_url=urlr(page_url)
        print 'URLR',media_url
    plugintools.play_resolved_url(media_url)


def rocvideo(params):
    plugintools.log('[%s %s] Rocvideo %s' % (addonName, addonVersion, repr(params)))

    page_url = params.get("url")
    if not "embed" in page_url:
        page_url = page_url.replace("http://rocvideo.tv/","http://rocvideo.tv/embed-") + ".html"

    try:
        headers = { "User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14" }
        r=requests.get(page_url, headers=headers);data=r.text
        data = plugintools.find_single_match(data,"<script type='text/javascript'>(eval\(function\(p,a,c,k,e,d.*?)</script>")
        data = unpackerjs.unpackjs(data)
        media_url = plugintools.find_single_match(data,'file:"([^"]+)"').strip()
        plugintools.log("media_url= "+media_url)
    except:
        media_url=urlr(page_url)
        print 'URLR',media_url
        
    plugintools.play_resolved_url(media_url)
    

def realvid(params):
    plugintools.log('[%s %s] Realvid %s' % (addonName, addonVersion, repr(params)))

    page_url = params.get("url")

    try:
        if not "embed" in page_url:
            page_url = page_url.replace("http://realvid.net/","http://realvid.net/embed-") + ".html"
        headers = { "User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14" }
        r=requests.get(page_url, headers=headers);data=r.text
        if data.find("File was deleted") >= 0:
            xbmc.executebuiltin("Notification(%s,%s,%i,%s)" % ('PalcoTV', "Archivo borrado!", 3 , art+'icon.png'))
        else:
            media_url = plugintools.find_single_match(data,'file: "([^"]+)",').strip()
            plugintools.log("media_url= "+media_url)
    except:
        media_url=urlr(page_url)
        print 'URLR',media_url

    plugintools.play_resolved_url(media_url)
        

def netu(params):
    plugintools.log('[%s %s] Netu %s' % (addonName, addonVersion, repr(params)))

    page_url = params.get("url")

    if "http://netu.tv/" in page_url:
        page_url = page_url.replace("http://netu.tv/","http://waaw.tv/")
    id_video = page_url.replace("http://waaw.tv/watch_video.php?v=","")
    #print id_video
    ref = page_url
    headers = {"Host": "netu.tv","User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0","Accept": "*/*",
    "Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3","Accept-Encoding": "gzip, deflate","DNT": "1","Referer": ref,
    "Cookie": "visid_incap_152707","Connection": "keep-alive"}
    url_json = "http://netu.tv/player/ip.php"

    r=requests.get(url_json,headers=headers) 
    respuesta = plugintools.log("Respuesta= "+ str(r.status_code))
    data=r.content
    cookie = r.cookies['visid_incap_152707']
    iss = plugintools.find_single_match(data, 'var iss="([^"]+)"')
    #http://waaw.tv/watch_video.php?v=2HXM4AYDY4WD#iss=OTUuMjIuMTcwLjEyNA==

    if iss !="":
        page_url = page_url+"#iss="+iss
        
        headers = {"Host": "waaw.tv","User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3","Accept-Encoding": "gzip, deflate","DNT": "1",
        "Cookie": ["__cfduid","_ym_uid","pageredir"],"Connection": "keep-alive"}

        id_vid = page_url.replace("http://waaw.tv/watch_video.php?v=","")
        new_id_video = page_url.replace("http://waaw.tv/watch_video.php?v=","http://hqq.tv/player/embed_player.php?vid=")  
        
        plugintools.log("New Url= "+new_id_video)
        body,response_headers = plugintools.read_body_and_headers(new_id_video,headers=headers,post=id_vid,follow_redirects=False)

        ##get_b64_data
        # Petición a hqq.tv con la nueva id de vídeo 
        b64_data = get_b64_data(new_id_video, headers)

        ## Doble decode y unicode-escape
        # Doble decodificacion y retorno del codigo fuente
        utf8 = double_b64(b64_data)
        # plugintools.log("Doble Decode= "+utf8)

        # at 
        at = plugintools.find_single_match(utf8,'<input name="at" type="text" value="([^"]+)"')
        
        # m3u8 
        # Recoger los bytes ofuscados que contiene la url del m3u8
        b_m3u8_2 = get_obfuscated(iss, at, id_video, ref)
    
        # tb_m3u8 
        # Obtener la url del m3u8
        url_m3u8 = tb(b_m3u8_2)
    
    ### m3u8 ###
    media_url = url_m3u8
    # print media_url
    plugintools.play_resolved_url(media_url)   
    
def waaw(params):
    plugintools.log('[%s %s] Waaw.tv (ex Netu.tv) %s' % (addonName, addonVersion, repr(params)))

    netu(params)

## --------------------------------------------------------------------------------
## Decodificación b64 para Netu
## --------------------------------------------------------------------------------

## Decode
def b64(text, inverse=False):
    if inverse:
        text = text[::-1]
    return base64.decodestring(text)

## Petición a hqq.tv con la nueva id de vídeo
def get_b64_data(new_id_video, headers):
    page_url_hqq = new_id_video+"&autoplay=no" #"http://hqq.tv/player/embed_player.php?vid="+
    body,response_headers = plugintools.read_body_and_headers( page_url_hqq , headers=headers )
    data_page_url_hqq = body
    b64_data = plugintools.find_single_match(data_page_url_hqq, 'base64,([^"]+)"')
    return b64_data

## Doble decode y unicode-escape
def double_b64(b64_data):
    b64_data_inverse = b64(b64_data)
    #print b64_data_inverse 
    
    b64_data_2 = plugintools.find_single_match(b64_data_inverse, "='([^']+)';")
    utf8_data_encode = b64(b64_data_2,True)
    utf8_encode = plugintools.find_single_match(utf8_data_encode, "='([^']+)';")
    utf8_decode = utf8_encode.replace("%","\\").decode('unicode-escape')
    return utf8_decode
    
## Recoger los bytes ofuscados que contiene el m3u8
def get_obfuscated(iss, at, id_video, ref):
    
    #http://hqq.tv/sec/player/embed_player.php?iss=OTUuMjIuMTcwLjEyNA==&vid=2HXM4AYDY4WD&at=ac08b1684dc7986c82985389c4ee8987&autoplayed=yes&referer=on&http_referer=http://waaw.tv/watch_video.php?v=2HXM4AYDY4WD&pass=&embed_from=embed_from
    headers = {"Host": "hqq.tv","User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8","Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3",
    "Accept-Encoding": "gzip, deflate","DNT": "1","Referer": "http://hqq.tv/","Connection": "keep-alive"}

    url = "http://hqq.tv/sec/player/embed_player.php?iss="+iss+"&vid="+id_video+"&at="+at+"&autoplayed=yes&referer=on&http_referer="+ref+"&pass=&embed_from=embed_from"
    
    body,response_headers = plugintools.read_body_and_headers( url, headers=headers )
    match_b_m3u8_1 = plugintools.find_single_match(body,'</div>.*?<script>document.write[^"]+"([^"]+)"')
    
    b_m3u8_1 = urllib.unquote( plugintools.find_single_match(body, match_b_m3u8_1) )
    #print b_m3u8_1

    if b_m3u8_1 == "undefined": 
        b_m3u8_1 = urllib.unquote(body)

    match_b_m3u8_2 = plugintools.find_single_match(b_m3u8_1,'"#([^"]+)"')
    #print match_b_m3u8_2
    
    b_m3u8_2 = plugintools.find_single_match(b_m3u8_1, match_b_m3u8_2)
    #print b_m3u8_2

    return b_m3u8_2

## Obtener la url del m3u8
def tb(b_m3u8_2):
    j = 0
    s2 = ""
    while j < len(b_m3u8_2):
        s2+= "\\u0"+b_m3u8_2[j:(j+3)]
        j+= 3

    return s2.decode('unicode-escape').encode('ASCII', 'ignore')

## --------------------------------------------------------------------------------
## --------------------------------------------------------------------------------


def videomega(params):
    plugintools.log('[%s %s] Videomega.tv %s' % (addonName, addonVersion, repr(params)))

    page_url = params.get("url")
    
    try:
        ref = page_url.split("ref=")[1]
        page_url = 'http://videomega.tv/view.php?ref='+ref+'&width=100%&height=400'
        #post = premium = False , user="" , password="", video_password=""
        headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0', 'Referer': page_url, "Accept-Encoding": "gzip, deflate, sdch" }        
        r = requests.get(page_url, headers=headers,premium=False,user="",password="",video_password="");data = r.text
        media_url = plugintools.find_single_match(data,'<source src="([^"]+)"')
        
    except:
        media_url=urlr(page_url)
        print 'URLR',media_url
        
    plugintools.play_resolved_url(media_url)


def videott(params):
    plugintools.log("[%s %s] Videott %s " % (addonName, addonVersion, repr(params)))

    page_url = params.get("url")    
    if page_url.startswith("http://www.video.tt/video/") == True:
        page_url = page_url.replace("http://www.video.tt/video/","http://www.video.tt/watch_video.php?v=")
        #http://www.video.tt/watch_video.php?v=133ZLJSNn
        #http://www.video.tt/video/E22dc6KBI
        #parametro = page_url.replace("http://www.video.tt/watch_video.php?v=","").replace("http://www.video.tt/video/","")   
    try:
        # URL del vídeo
        videoid = page_url.replace("http://www.video.tt/watch_video.php?v=","").replace("http://www.video.tt/video/","")
        timestamp=str(random.randint(1000000000,9999999999))
        hexastring = get_sha1(page_url) + get_sha1(page_url) + get_sha1(page_url) + get_sha1(page_url)
        hexastring = hexastring[:96]
        media_url = "http://gs.video.tt/s?v="+videoid+"&r=1&t="+timestamp+"&u=&c="+hexastring+"&start=0"
    except:
        media_url=urlr(page_url)
        print 'URLR',media_url
        
    plugintools.play_resolved_url(media_url)
    

###### Función auxiliar para conector video.tt ###################

def get_sha1(cadena):
    try:
        import hashlib
        devuelve = hashlib.sha1(cadena).hexdigest()
    except:
        import sha
        import binascii
        devuelve = binascii.hexlify(sha.new(cadena).digest())
    
    return devuelve

####################################################


def flashx(params):
    plugintools.log("[%s %s] Flashx %s " % (addonName, addonVersion, repr(params)))

    page_url = params.get("url")
    
    page_url = page_url.replace("http://flashx.tv/embed-","http://www.flashx.tv/").replace("-640x360","")
    plugintools.log("Url= "+page_url)
    try:        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:42.0) Gecko/20100101 Firefox/42.0','Host': 'www.flashx.tv',
        'DNT': '1','Connection': 'keep-alive','Cache-Control': 'max-age=0','Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate','Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}

        r = requests.get(page_url, headers=headers)
        data = r.content
        r.status_code
        plugintools.log("Respuesta= "+str(r.status_code))
    
        form_url = plugintools.find_single_match(data,"<Form method=\"POST\" action='([^']+)'>")
        form_url = urlparse.urljoin(page_url,form_url)

        usr_login = ""
        ref = ""
        op = plugintools.find_single_match(data,'<input type="hidden" name="op" value="([^"]+)"')
        imhuman = plugintools.find_single_match(data,'<input type="submit".*?name="imhuman" value="([^"]+)"').replace(" ","+")
        id_vid = plugintools.find_single_match(data,'<input type="hidden" name="id" value="([^"]+)"')
        hashstring = plugintools.find_single_match(data,'<input type="hidden" name="hash" value="([^"]*)"')
        fname = plugintools.find_single_match(data,'<input type="hidden" name="fname" value="([^"]+)"')
        time.sleep(10)
    
        post = "op="+op+"&usr_login="+usr_login+"&id="+id_vid+"&fname="+fname+"&referer="+ref+"&hash="+hashstring+"&imhuman="+imhuman
        body,response_headers = plugintools.read_body_and_headers(form_url,headers=headers,post=post) #,allow_redirects=True)
    
        data = plugintools.find_single_match(body,"<script type='text/javascript'>(eval\(function\(p,a,c,k,e,d.*?)</script>")
        data = unpackerjs.unpackjs(data)
        # plugintools.log("data="+data)
        urls = plugintools.find_multiple_matches(data,'file:"([^"]+)')
        # print urls
        for entry in urls:
            print entry    
            if entry.endswith(".mp4") == True:
                media_url = entry
                print 'media_url',media_url
        
    except:
        media_url=urlr(page_url)
        print 'URLR',media_url
        
    plugintools.play_resolved_url(media_url)
        

def okru(params):
    plugintools.log("[%s %s] Ok.ru %s " % (addonName, addonVersion, repr(params)))
    
    page_url=params.get("url")
    headers = {'user-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14',
    'Host': 'ok.ru','DNT': '1','Connection': 'keep-alive','Cache-Control': 'max-age=0','Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate','Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
    r = requests.get(page_url, headers=headers)
    data = r.content
    
    try:
        headers = {'X-Requested-With': 'XMLHttpRequest','user-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14','referer':params.get("url"),
        'Host': 'ok.ru','DNT': '1','Connection': 'keep-alive','Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate','Accept': 'application/json,text/javascript,*/*;q=0.01'}
        hash_url=page_url.replace("http://ok.ru/videoembed/", "").strip()
        plugintools.log("hash= "+hash_url)
        url_json='http://ok.ru/dk?cmd=videoPlayerMetadata&mid='+hash_url
    
        r=requests.get(url_json,headers=headers) #,"utf-8")
        print r.status_code
        data=r.content
    
        js=json.loads(data)
        videos=js["videos"]
        #opts={}
        for video in videos:
            #opts[video["name"]]=video["url"]
            if video['name'] == 'hd':
                media_url = video['url']
                plugintools.log("Url= "+media_url)
            elif video['name'] == 'sd':
                media_url = video['url']
                plugintools.log("Url= "+media_url)
            elif video['name'] == 'mobile':
                media_url = video['url']
                plugintools.log("Url= "+media_url)
            elif video['name'] == 'lowest':
                media_url = video['url']
                plugintools.log("Url= "+media_url)
            elif video['name'] == 'low':
                media_url = video['url']
                plugintools.log("Url= "+media_url)
    except:
        media_url=urlr(page_url)
        print 'URLR',media_url  

    plugintools.play_resolved_url(media_url)    

def vidtome(params):
    plugintools.log("[%s %s] Vidto.me %s " % (addonName, addonVersion, repr(params)))

    page_url=params.get("url")

    try:
        page_url = page_url.replace('/embed-', '/')
        page_url = re.compile('//.+?/([\w]+)').findall(page_url)[0]
        page_url = 'http://vidto.me/embed-%s.html' % page_url
        r=requests.get(page_url)
        data=r.content
        result = re.compile('(eval.*?\)\)\))').findall(data)[-1]
        result = unpackerjs.unpackjs(result)
        quality=plugintools.find_multiple_matches(result, 'label:"([^"]+)')
        url_media=plugintools.find_multiple_matches(result, 'file:"([^"]+)')
        media_url=url_media[len(quality)-1]
        
    except:
        media_url=urlr(page_url)
        print 'URLR',media_url
        
    plugintools.play_resolved_url(media_url)   
    
def playwire(params):
    plugintools.log("[%s %s] Playwire en Ourmatch.net %s " % (addonName, addonVersion, repr(params)))

    url=params.get("url")
    r=requests.get(url)
    data=r.content
    video_contents=plugintools.find_single_match(data, 'var video_contents = {(.*?)</script>')
    items_video=plugintools.find_multiple_matches(video_contents, '{(.*?)}')
    for entry in items_video:        
        url_zeus=plugintools.find_single_match(entry, 'config.playwire.com/(.*?)&quot;')
        zeus='http://config.playwire.com/'+url_zeus
        type_item=plugintools.find_single_match(entry, "type\':\'([^']+)")
        lang=plugintools.find_single_match(entry, "lang:\'([^']+)")
        title_item='[COLOR white]'+type_item+' [/COLOR][I][COLOR lightyellow]'+lang+'[/I][/COLOR]'
        print zeus,title_item
        url_media=[];posters=[]
        r=requests.get(zeus)
        data=r.content
        url_f4m=plugintools.find_single_match(data, 'f4m\":\"(.*?)f4m');url_f4m=url_f4m+'f4m'
        poster=plugintools.find_single_match(data, 'poster\":\"(.*?)png');poster=poster+'png'
        posters.append(poster)
        url_media.append(url_f4m)
        url_videos=dict.fromkeys(url_media).keys()
        url_poster=dict.fromkeys(posters).keys()
        r=requests.get(url_videos[0])
        data=r.content
        print data
        burl=plugintools.find_single_match(data, '<baseURL>([^<]+)</baseURL>')
        media_item=plugintools.find_multiple_matches(data, '<media(.*?)"/>')
        i=1
        while i<=len(media_item):
            for item in media_item:
                plugintools.log("item= "+item)
                media=plugintools.find_single_match(item, 'url="([^"]+)')
                bitrate=plugintools.find_single_match(item, 'bitrate="([^"]+)')
                url_media=burl+'/'+media
                title_fixed=title_item+' [COLOR lightblue][I]('+bitrate+' kbps)[/I][/COLOR]'
                plugintools.add_item(action="play", title=title_fixed, url=url_media, thumbnail=url_poster[0], fanart='http://images.huffingtonpost.com/2014-09-12-image1.JPG', folder=False, isPlayable=True)
                i=i+1                
                

    #http://config.playwire.com/17003/videos/v2/4225978/zeus.json
    #https://config.playwire.com/17003/videos/v2/4225978/manifest.f4m
    #https://cdn.phoenix.intergi.com/17003/videos/4225978/video-sd.mp4?hosting_id=17003


def youwatch(params):
    plugintools.log('[%s %s] YouWatch %s' % (addonName, addonVersion, repr(params)))

    page_url = params.get("url")
    try:
        #headers= {"Host": "youwatch.org","User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0"}
        r = requests.get(page_url)
        data = r.content
        print '$'*25,"[PalcoTv] Respuesta= "+str(r.status_code),'$'*25

        # http://youwatch.org/embed-7bov08kkp238-_-VmZWeTBYam5aWDlzOXgwNXlvVW1sL20xU2FzZTYwK3hXcXB4U1dYM1NqSVZzTDNvV3c9PQo=.html
        url_you = plugintools.find_single_match(data,'<iframe class="embed-responsive-item" src="(.*?)=')
        url_you = "http:"+url_you+"==.html"
    
        headers = {"Host": "youwatch.org","User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0",
        "Referer": page_url}
        r = requests.get(url_you,headers=headers)
        data = r.content
        # http://khaltek.info/embed-7bov08kkp238-_-VmZWeTBYam5aWDlzOXgwNXlvVW1sL20xU2FzZTYwK3hXcXB4U1dYM1NqSVZzTDNvV3c9PQo=.html?970043043
        url_kha1 = plugintools.find_single_match(data,'<iframe src="([^"]+)"')
        # print url_kha1

        headers = {"Host": "khaltek.info","User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0",
        "Referer": url_you}
        r = requests.get(url_kha1,headers=headers)
        data = r.content  
        url_kha2 = plugintools.find_single_match(data,'<iframe src="([^"]+)"')
        # print url_kha2

        headers = {"Host": "khaltek.info","User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0",
        "Referer": url_kha1}
        r = requests.get(url_kha2,headers=headers)
        data = r.content
        # print data
        url_source = plugintools.find_single_match(data,'sources:.*?file:"([^"]+)"')
        # print url_source
        media_url=url_source
    except:
        media_url=urlr(page_url)
        print 'URLR',media_url

    plugintools.play_resolved_url(media_url)


def vidggto(params):
    plugintools.log('[%s %s] Vidgg.to %s' % (addonName, addonVersion, repr(params)))
    
    page_url = params.get("url")
    try:
        r = requests.get(page_url)
        data = r.content
        print '$'*25,"[PalcoTv] Respuesta= "+str(r.status_code),'$'*25
        # print data
    
        key = plugintools.find_single_match(data,'flashvars.filekey="(.*?)"')
        file_id = plugintools.find_single_match(data,'flashvars.file="(.*?)"')
        cid = plugintools.find_single_match(data,'flashvars.domain="(.*?)"')
        domain = plugintools.find_single_match(data,'flashvars.cid="(.*?)"')
        ref = "http://www.vidgg.to/player/cloudplayer.swf"

        headers = {"Host":"www.vidgg.to","User-Agent": '"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0"', "Referer": ref}
        # http://www.vidgg.to/api/player.api.php?key=87.223.99.234-6e60102419de42e1a5550fd0119a211e&numOfErrors=0&user=undefined&pass=undefined&cid=1&file=288d5af5a64c0&cid3=seriesyonkis.sx&cid2=undefined
        url_new = "http://www.vidgg.to/api/player.api.php?key="+key+"&numOfErrors=0&user=undefined&pass=undefined&cid="+cid+"&file="+file_id+"&cid3="+domain+"&cid2=undefined"
    
        r = requests.get(url_new,headers=headers)
        data = r.content
        #print data
        #url=http://s240.zerocdn.to/dl/23a3e0c1ef50a88777fbee9ba554bc85/5686721b/ff1208c256562d03962845fb3af0655e16.flv&title=4N4T0M14.12x8.m720p%26asdasdas&site_url=http://www.vidgg.to/video/288d5af5a64c0&seekparm=&enablelimit=0
        media_url = plugintools.find_single_match(data,'url=(.*?)&title')
    except:
        media_url=urlr(page_url)
        print 'URLR',media_url
    
    plugintools.play_resolved_url(media_url)

def vimple(params):
    plugintools.log('[%s %s] Vimple %s' % (addonName, addonVersion, repr(params)))

    page_url = params.get("url")

    try:
        r = requests.get(page_url)
        data = r.content
        print '$'*25,"[PalcoTv] Respuesta= "+str(r.status_code),'$'*25
        # print data

        url = plugintools.find_single_match(data,"dataUrl:'(.*?)'")
        url_new = "http://player.vimple.ru"+url
        ref = "http://videoplayer.ru/ru/player/spruto/player.swf?v=3.1.0.7" 
        headers = {"Host":"s13.vimple.ru:8081","User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0","Referer":ref}
    
        r = requests.get(url_new)
        data = r.content
        user_id = r.cookies['UniversalUserID'];print user_id
    
        js = json.loads(data)
        media = js['sprutoData']['playlist'][0]['video'][0]['url']
        media_url = media+"|Cookie=UniversalUserID="+user_id
    
        #http://s13.vimple.ru:8081/vv52/716622.mp4?v=2c6a0a43-bfa1-469e-abf8-8b7d8df9769b&t=635872710621810000&d=7334&sig=6edab5d97959da7b3451444cb002a557
        #http://s15.vimple.ru:8081/vv65/698440.mp4?v=bfe4e467-2765-4be0-a479-22ee1e2ab515&t=635872785719935000&d=5987&sig=09ad419d594c1a674b4caaea3efca60f|Cookie=UniversalUserID=24259d8f030a42df9fe6eec1e80083b9
    except:
        media_url=urlr(page_url)
        print 'URLR',media_url

    plugintools.play_resolved_url(media_url)

def idowatch(params):
    plugintools.log('[%s %s] IdoWatch %s' % (addonName, addonVersion, repr(params)))
    
    page_url = params.get("url")
    try:
        headers = {"Host": "idowatch.net","User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0"}
    
        r = requests.get(page_url,headers=headers)
        data = r.content
        print '$'*25,"[PalcoTv] Respuesta= "+str(r.status_code),'$'*25
        bloq_url = plugintools.find_single_match(data,"<script type='text/javascript'>(.*?)</script>")
        media_url = plugintools.find_single_match(bloq_url,'file:"(.*?)"')
    except:
        media_url=urlr(page_url)
        print 'URLR',media_url
    
    plugintools.play_resolved_url(media_url)


def cloudtime(params):
    plugintools.log('[%s %s] CloudTime %s' % (addonName, addonVersion, repr(params)))
    
    page_url = params.get("url")
    
    try:
        headers = {"Host": "www.cloudtime.to","User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0"}
    
        r = requests.get(page_url,headers=headers)
        data = r.content
        print '$'*25,"[PalcoTv] Respuesta= "+str(r.status_code),'$'*25

        stepkey = plugintools.find_single_match(data,'name="stepkey" value="([^"]+)"')
        submit = plugintools.find_single_match(data,'name="submit" class="btn" value="([^"]+)"')
        post = "stepkey="+stepkey+"&submit="+submit
    
        headers = {"Host": "www.cloudtime.to","User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0","Referer":page_url}
        body,response_headers = plugintools.read_body_and_headers(page_url,headers=headers,post=post)
    
        #print body
        #http://www.cloudtime.to/api/player.api.php?cid3=cloudtime.to&file=90c557483413b&key=87.223.99.234-08d874b967c90d5f298bbed5968d1dd9&numOfErrors=0&pass=undefined&user=undefined&cid2=undefined&cid=1
        #http://www.cloudtime.to/api/player.api.php?cid3=cloudtime%2Eto&file=90c557483413b&key=87%2E223%2E99%2E234%2D08d874b967c90d5f298bbed5968d1dd9&numOfErrors=0&pass=undefined&user=undefined&cid2=undefined&cid=1

        cid3 = "cloudtime%2Eto"
        file_id = plugintools.find_single_match(body,'flashvars.file="([^"]+)"').replace(".","%2E").replace("-","%2D")
        key = plugintools.find_single_match(body,'flashvars.filekey="([^"]+)"').replace(".","%2E").replace("-","%2D")
        new_url = "http://www.cloudtime.to/api/player.api.php?cid3="+cid3+"&file="+file_id+"&key="+key+"&numOfErrors=0&pass=undefined&user=undefined&cid2=undefined&cid=1"
        print new_url
        #http://www.cloudtime.to/api/player.api.php?cid3=cloudtime.to&file=90c557483413b&key=87.223.99.234-08d874b967c90d5f298bbed5968d1dd9&numOfErrors=0&pass=undefined&user=undefined&cid2=undefined&cid=1
        #http://www.cloudtime.to/api/player.api.php?cid3=cloudtime%2Eto&file=90c557483413b&key=87%2E223%2E99%2E234%2D08d874b967c90d5f298bbed5968d1dd9&numOfErrors=0&pass=undefined&user=undefined&cid2=undefined&cid=                                            

        ref = "http://www.cloudtime.to/player/cloudplayer.swf"
        headers = {"Host": "www.cloudtime.to","User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0","Referer":ref}
        r = requests.get(new_url,headers=headers)
        data = r.content
        #print data
        media = data.replace("url=","").split('&')
        media_url = media[0]
    except:
        media_url=urlr(page_url)
        print 'URLR',media_url
    
    plugintools.play_resolved_url(media_url)


def vidzitv(params):
    plugintools.log('[%s %s] Vidzi.tv %s' % (addonName, addonVersion, repr(params)))
    
    page_url = params.get("url")
	
    try:
        headers = {"Host": "vidzi.tv","User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0"}
        r=requests.get(page_url, headers=headers);data=r.text #;print data
        print '$'*25,"[PalcoTv] Respuesta= "+str(r.status_code),'$'*25
        data = plugintools.find_single_match(data,"<script type='text/javascript'>(eval\(function\(p,a,c,k,e,d.*?)</script>")
        data = unpackerjs.unpackjs(data)
        try:
            media = plugintools.find_multiple_matches(data,'file:"([^"]+)"')
            if media == "":
                plugintools.log("Archivo borrado: "+page_url)
                xbmc.executebuiltin("Notification(%s,%s,%i,%s)" % ('PalcoTV', "El Archivo ha sido borrado", 3 , art+'icon.png'))
            elif media == 1:
                media_url = media
            elif media >= 2:
                media_url = media[1] 
            else:
                media_url = media[-1]
            plugintools.log("media_url= "+str(media_url))     
        except:
            media_url = plugintools.find_single_match(data,'file:"([^"]+)"')
            plugintools.log("media_url= "+str(media_url))
    except:
        media_url=urlr(page_url)
        print 'URLR',media_url
    
    plugintools.play_resolved_url(media_url)


def vodlocker(params):
    plugintools.log('[%s %s] VodLocker %s' % (addonName, addonVersion, repr(params)))
    
    page_url = params.get("url")

    if not "embed" in page_url:
      page_url = page_url.replace("http://vodlocker.com/","http://vodlocker.com/embed-") + ".html"

    try:
        headers = {"Host": "vodlocker.com","User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0"}
        r = requests.get(page_url,headers=headers)
        data = r.content
        print '$'*25,"[PalcoTv] Respuesta= "+str(r.status_code),'$'*25
        #print data
        media_url = plugintools.find_single_match(data,'file: "([^"]+)"')
        if media_url == "":
            plugintools.log("Archivo borrado: "+page_url)
            xbmc.executebuiltin("Notification(%s,%s,%i,%s)" % ('PalcoTV', "El Archivo ha sido borrado", 3 , art+'icon.png'))
    except:
        media_url=urlr(page_url)
        print 'URLR',media_url

    plugintools.play_resolved_url(media_url)


def streamenet(params):
    plugintools.log('[%s %s] Streame.net %s' % (addonName, addonVersion, repr(params)))
    
    page_url = params.get("url")

    if not "embed" in page_url:
      page_url = page_url.replace("http://streame.net/","http://streame.net/embed-") + ".html"

    try:
        headers = {"Host": "streame.net","User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0"}
        r = requests.get(page_url,headers=headers)
        data = r.content
        print '$'*25,"[PalcoTv] Respuesta= "+str(r.status_code),'$'*25
        #print data
        try:
            media = plugintools.find_multiple_matches(data,'sources:.*?file:"([^"]+)"')
            if media == "":
                plugintools.log("Archivo borrado: "+page_url)
                xbmc.executebuiltin("Notification(%s,%s,%i,%s)" % ('PalcoTV', "El Archivo ha sido borrado", 3 , art+'icon.png'))
            elif media == 1:
                media_url = media
            elif media >= 2:
                media_url = media[1] 
            else:
                media_url = media[-1]
                plugintools.log("media_url= "+str(media_url))     
        except:
            media_url = plugintools.find_single_match(data,'sources:.*?file:"([^"]+)"')
            plugintools.log("media_url= "+str(media_url))   
    except:
        media_url=urlr(page_url)
        print 'URLR',media_url
        
    plugintools.play_resolved_url(media_url)


def watchonline(params):
    plugintools.log('[%s %s] WatchOnLine %s' % (addonName, addonVersion, repr(params)))
    
    page_url = params.get("url")
    headers = {"Host": "www.watchonline.to","User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0"}
    
    if not "embed" in page_url:
      page_url = page_url.replace("http://www.watchonline.to/","http://www.watchonline.to/embed-") + ".html"

    try:
        headers = {"Host": "www.watchonline.to","User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0"}
        r = requests.get(page_url,headers=headers)
        data = r.content
        print '$'*25,"[PalcoTv] Respuesta= "+str(r.status_code),'$'*25
        #print data
        try:
            bloq_media = plugintools.find_multiple_matches(data,'sources:(.*?)image:')
            media = plugintools.find_multiple_matches(bloq_media,'file:"([^"]+)"')
            if media == "":
                plugintools.log("Archivo borrado: "+page_url)
                xbmc.executebuiltin("Notification(%s,%s,%i,%s)" % ('PalcoTV', "El Archivo ha sido borrado", 3 , art+'icon.png'))
            else:
                media_url = media[0]
                plugintools.log("media_url= "+str(media_url))     
        except:
            media_url = plugintools.find_single_match(data,'sources:.*?file:"([^"]+)"')
            plugintools.log("media_url= "+str(media_url))   
    except:
        media_url=urlr(page_url)
        print 'URLR',media_url
        
    plugintools.play_resolved_url(media_url)


def allvid(params):
    plugintools.log('[%s %s] Allvid %s' % (addonName, addonVersion, repr(params)))
    
    page_url = params.get("url")
    
    if not "embed" in page_url:
      page_url = page_url.replace("http://allvid.ch/","http://allvid.ch/embed-") + ".html"
    # print page_url
    try:
        headers = {"Host": "allvid.ch","User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0"}
        r=requests.get(page_url)
        data = r.content
        print '$'*25,"[PalcoTv] Respuesta= "+str(r.status_code),'$'*25
    
        script = plugintools.find_single_match(data,"<script type='text/javascript'>(eval\(function\(p,a,c,k,e,d.*?)</script>")
        # este server da error en la decodificacion javascript 
        # data = unpackerjs.unpackjs(script)
        # <<--- parche provisional --->>
        bloq = plugintools.find_single_match(script,"eval.*?\}\)\}'[^']+'(.*?)'")
        itemlist = bloq.split("|")
        for item in itemlist:
            try:
                if len(item) >= 50: #lo que hago es coger el id del video que tienen mas de 50 caracteres
                    #print item
                    id_vid = item
                    media_url = "http://fs4.allvid.ch/"+id_vid+"/v.mp4" #componer la url manualmente
                    plugintools.log("Url= "+media_url)
            except:
                plugintools.log("Archivo borrado: "+page_url)
                xbmc.executebuiltin("Notification(%s,%s,%i,%s)" % ('PalcoTV', "El Archivo ha sido borrado", 3 , art+'icon.png'))
    except:
        media_url=urlr(page_url)
        print 'URLR',media_url

    plugintools.play_resolved_url(media_url)


def streamplay(params):
    plugintools.log('[%s %s] StreamPlay %s' % (addonName, addonVersion, repr(params)))
    
    page_url = params.get("url")

    if not "embed" in page_url:
        page_url = page_url.replace("http://streamplay.to/","http://streamplay.to/embed-") + ".html"  
    
    try:        
        headers = {"Host": "streamplay.to","User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0"}
        r = requests.get(page_url,headers=headers)
        data = r.text
        print '$'*25,"[PalcoTv] Respuesta= "+str(r.status_code),'$'*25
        #print data

        data = plugintools.find_single_match(data,"<script type='text/javascript'>(eval\(function\(p,a,c,k,e,d.*?)</script>")
        data = unpackerjs.unpackjs(data)
        # plugintools.log("data="+data)
        try:
            urls = plugintools.find_multiple_matches(data,'file:"([^"]+)')
            # print urls
            for item in urls:
                if item == "":
                    plugintools.log("Archivo borrado: "+page_url)
                    xbmc.executebuiltin("Notification(%s,%s,%i,%s)" % ('PalcoTV', "El Archivo ha sido borrado", 3 , art+'icon.png'))   
                elif item.endswith(".mp4") == True:
                    media_url = item
                    print 'media_url',media_url
                else:
                    media_url = item[-1]
                    print 'media_url',media_url
        except:
            url = plugintools.find_single_match(data,'file:"([^"]+)')
            media_url = url            
    except:
        media_url=urlr(page_url)
        print 'URLR',media_url
       
    plugintools.play_resolved_url(media_url)


def myvideoz(params):
    plugintools.log('[%s %s] MyvideoZ %s' % (addonName, addonVersion, repr(params)))
    
    page_url = params.get("url")

    try:
        headers = {"Host": "myvideoz.net","User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0"}
    
        r = requests.get(page_url,headers=headers)
        data = r.content
        sess = r.cookies['PHPSESSID']
        print '$'*25,"[PalcoTv] Respuesta= "+str(r.status_code),'$'*25
    
        url = plugintools.find_single_match(data,"<meta property=\"og:video\" content='([^']+)'")
        if url == "":
            plugintools.log("Archivo borrado: "+page_url)
            xbmc.executebuiltin("Notification(%s,%s,%i,%s)" % ('PalcoTV', "El Archivo ha sido borrado", 3 , art+'icon.png'))
        #http://myvideoz.net/nuevo/player/player.swf?config=http%3A%2F%2Fmyvideoz.net%2Fnuevo%2Fplayer%2Ffsb.php%3Fv%3D70764%26autostart%3Dno
        ref = url.replace('%3A',':').replace('%2F','/').replace('%3D','=').replace('%3F','?').replace('%26','&')
        new_url = ref.replace('http://myvideoz.net/nuevo/player/player.swf?config=','') 
        #http://myvideoz.net/nuevo/player/fsb.php?v=70764&autostart=no
        
        headers = {"Host": "myvideoz.net","User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0",
        "Referer": ref,"PHPSESSID":sess}

        r = requests.get(new_url,headers=headers)
        data = r.content 
        media_url = plugintools.find_single_match(data,"<file>([^<]+)</file>")
        plugintools.log("Url= "+media_url)
        if media_url == "":
            plugintools.log("Archivo borrado: "+page_url)
            xbmc.executebuiltin("Notification(%s,%s,%i,%s)" % ('PalcoTV', "El Archivo ha sido borrado", 3 , art+'icon.png'))
    except:
        media_url=urlr(page_url)
        print 'URLR',media_url
   
    plugintools.play_resolved_url(media_url)
