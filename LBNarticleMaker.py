#! /usr/bin/python
# -*- coding: utf-8 -*-
"""LBNarticleMaker script.
Ce script est à l'intension exclusive des utilisateurs du CMS Guppy (https://www.freeguppy.org/)
This script is itended exclusively for Guppy CMS users.(https://www.freeguppy.org/)

Il permet de créer facilement des articles multi-lingues possédant éventuellement les éléments suivants :
It allows to create multi-lingual articles with possibly the following elements :
- Des titres, de trois niveaux possibles / Some titles, with 3 possible levels
- Une photo d'introduction / A head picture
- Des blocs de texte / Some text blocks
- Une photo isolée avec légende / A single picture with its caption
- Une vidéo Youtube  / A Youtube video
- Une série de photos commentées, qui peuvent avoir différentes formes / A series of commented pictures, that can have different shapes 
 
Le script s'utilise de la manière suivante : / The script is used the following way :
- Rassembler les photos dans un nouveau répertoire <dir> /  Put together the pictures in a new directory <dir>
- python LBNarticleMaker.py  <dir>
- Le programme crée dans le répertoire un fichier ARTICLE.xml / The program creates in the directory a file called  ARTICLE.xml
- Editer le contenu du fichier pour entrer les informations contenues dans l'article / Edit the xml file and fill in the article contents
- Appeler à nouveau python LBNarticleMaker.py  <dir> / Call again python LBNarticleMaker.py  <dir>
- Le contenu html de l'article s'affiche sur la console / The html article displays on the console
- Un fichier ARTICLE.html est également enregistré / An ARTICLE.html is also generated
- Le code html généré contient le corps de l'article en Français et dans la deuxième langue si demandé. /
The generated html code contains the article in its primary language and a second language if requested.
 
 
Il ne reste qu'à copier/coller dans l'éditeur d'article Guppy (bouton source), pour chaque langue correspondante / You only have to copy/paste the content
in the Guppy article editor (source button), for each correponding language.

Les traductions sont issues de Google traduction, il faut bien entendu les corriger ensuite dans l'éditeur de Guppy./
The translations are from Google translation, they ned to be reviewed afterward in the Guppy editor.

Copyright Christophe Mineau - www.labellenote.fr
Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License


Usage:
  LBNarticleMaker.py <path>
  LBNarticleMaker.py (-h | --help)
  LBNarticleMaker.py <path> [--sourceLanguage=<lg>] [--photoType=<type>]
  LBNarticleMaker.py <path> --debug
  
  
 
Options:
  -h --help                Get help.
  --version                Get this program version.
  --photoType=<typ>        Type of the photos, [default: jpg].
  --sourceLanguage=<lg>    Source language, [default: Fr], you can use En, Sp, De ... 
  --debug                  Displays translation results on the fly.
  
  
  
  
Example:
  python LBNarticleMaker.py "D:\Guppy\Articles\MyDummyArticle" 
  python LBNarticleMaker.py "D:\Guppy\Articles\MyDummyArticle" --photoType=png
  
"""
 

import os
import time

import platform
print("Python version = {}".format(platform.python_version()))
# from translate import Translator # pip install translate   # doesn't work very well ..
# from googletrans import Translator # pip install googletrans (bug 2018)
from py_translator import Translator # pip3 install py_translator==1.8.9  see https://stackoverflow.com/questions/52455774/googletrans-stopped-working-with-error-nonetype-object-has-no-attribute-group

from lxml import etree as ET
from docopt import docopt  # pip install docopt
from _elementtree import SubElement
from string import Template

# Globals
VERSION = 'LBNarticleMaker 2.0'
SOURCE_LANGUAGE = 'Fr'    # overriden by the explicit parameter --sourceLanguage=<lg>
IMAGE_EXTENSION = '.jpg'  # overriden by the explicit parameter --photoType=<typ> 
DIRPATH = ""              # explicit parameter of the script <path>
DEBUG = False

ARTICLEFILE_NAME = "ARTICLE.xml"
OUTPUT_ARTICLEFILE_NAME = "ARTICLE_SOURCECODE.html"

# Default values (overriden by the ARTICLE.xml parameter file contents
RELPATH_ON_SITE = ""


class LocalTranslator(Translator):
    def __init__(self, fromLanguage, toLanguage):
        self.fromLanguage = fromLanguage
        self.toLanguage = toLanguage
        if self.fromLanguage != self.toLanguage:
            Translator.__init__(self)
        self.WarningDone = False
        
    def translate(self, txt):
        if self.fromLanguage == self.toLanguage:
            return txt
        else:
            if not self.WarningDone:
                self.WarningDone = True
                print("  !! Traduction en cours, soyez patient ... / translation ongoing, please be patient ...")
            #translationChunks = txt.split('.')
            translationChunks = [ txt ]
            translatedTxt = ''
            for chunk in translationChunks:
                translatedChunk = Translator.translate(self, chunk, dest = self.toLanguage, src = self.fromLanguage ).text
                translatedTxt += translatedChunk 
                if DEBUG:
                    print("#DEBUG: text to translate : {}".format(chunk.strip())) # .encode('utf-8')
                    print("#DEBUG: translated text : {}\n".format(translatedTxt)) # .encode('utf-8')
            return translatedTxt
        
class ArticleFile:
    '''
    ArticleFile represents the XML file where the Article contents is defined by the user.
    This file is created at the first call of the tool.
    At second call, the file is used to create the article
    '''
    def __init__(self, filePath):
        self.filePath = filePath
        if os.path.isfile(filePath):
            self.exists = True
        else:
            self.exists = False
            
    def parseArticleFile(self):
        '''
        Parsing of the XML file, getting the root elementTree object
        and returning an instance of the full ARTICLE object 
        '''    
        if not self.exists:
            return
        xmlTree = ET.parse(self.filePath)
        articleElement = xmlTree.getroot()
        if articleElement is None or articleElement.tag != 'ARTICLE':
            print("Erreur : Impossible de trouver l'élément ARTICLE dans le fichier xml !")
            exit(1)
        return GuppyArticle(articleElement)
       
          
            
    def makeTemplateArticleFile(self):
        photoList = [ f for f in os.listdir(DIRPATH) if not (os.path.isdir(os.path.join(DIRPATH,f))) and IMAGE_EXTENSION in f]
        photoList.sort()

        article = ET.Element('ARTICLE', relpath_on_site='file/dir1/dir2', lang="('Fr', 'En')")
        article.append(ET.Comment('''
        Balise ARTICLE : 
        Attributs obligatoires :
        * relpath_on_site= Chemin relatif pointant le répertoire des photos sur le site Guppy, Exemple : 'file/dir1/dir2'
        * lang= Langues de publication , Exemple: 
            ('Fr')          L'article est produit en une seule langue, pas de traduction
            ('Fr', 'En')  L'article est produit une fois en Français, une fois en Anglais
        Langages possibles : https://en.wikipedia.org/wiki/ISO_639-1
        '''))
        
        
        title = ET.SubElement(article, 'TITLE')
        title.text = "MON TITRE"
        article.append(ET.Comment('''
        Balise TITLE :
        Attributs optionnels :
        * format = 'h1'  : titre de niveau 1
          format = 'h2'  : titre de niveau 2
          format = 'h3'  : titre de niveau 3
        '''))
        

        head_picture = ET.SubElement(article, 'HEAD_PICTURE')
        head_picture.text = "my_preferred_picture.jpg"
        article.append(ET.Comment('''
        Balise HEAD_PICTURE : Image de présentation de l'article (celle qui sera partagée sur FB)
        Attributs  :
        * width='400' (optionnel) : largeur de l'image 
        '''))
           
        pre_video_blabla = ET.SubElement(article, 'BLABLA')
        pre_video_blabla.text = "Enter here description before the video"
        article.append(ET.Comment('''
        Balise BLABLA :  paragraphe de texte
        '''))
        
        solophoto = ET.SubElement(article, 'PHOTO')
        solophoto.append(ET.Comment('''
        Balise PHOTO : Une photo d'illustration isolée 
        Attributs  :
        * width='400' (optionnel) : largeur de l'image         
        '''))
        solophotoname =  ET.SubElement(solophoto, 'NAME')
        solophotoname.text = "one_illustration.jpg"
        solophodesc =  ET.SubElement(solophoto, 'DESCRIPTION')
        solophodesc.text = 'Description of the illustration.'    
            
        
        spacer = ET.SubElement(article, 'SPACER', lines='3')
        article.append(ET.Comment('''
        Balise SPACER :  sauts de lignes
        Attribut obligatoire :
        * lines = 'n'   nombre de lignes à sauter
        '''))
        
        
        video = ET.SubElement(article, 'VIDEO')
        video.text = "https://youtu.be/Ljli2uJJO0k"
        article.append(ET.Comment('''
        Balise VIDEO :  insérer une vidéo YOUTUBE
        Code Youtube  pour insérer une vidéo. (cliquer partager dans Youtube)
        Attributs facultatifs :
        *  width = 'largeur'  (560 par défaut)
        *  height = 'hauteur' (315) par défaut
        '''))
        
        post_video_blabla = ET.SubElement(article, 'BLABLA')
        post_video_blabla.text = "Enter here description after the video"
        article.append(ET.Comment('''
        Balise BLABLA :  paragraphe de texte
        '''))
 
        
        photos = ET.SubElement(article, 'PHOTOS', format='Table_1col')
        photos.append(ET.Comment('''
        Balise PHOTOS : Collection de photos
        Attribut obligatoire :
        * format = Comment seront affichées les photos, 4 valeurs possibles :
            Table_1col : un tableau à 1 colonne de photo et sa description 
            Table_2col : un tableau à deux colonnes de photo et leur description au dessous
            Carousel  : un diaporama défilant
        '''))

        for p in photoList:
            photo = ET.SubElement(photos, 'PHOTO')
            name =  ET.SubElement(photo, 'NAME')
            name.text = p
            desc =  ET.SubElement(photo, 'DESCRIPTION')
            desc.text = " _ Description  _"
             
                
        footer = ET.SubElement(article, 'BLABLA')
        footer.text = "Enter here the text that will be at bottom of the article"
        article.append(ET.Comment('''
        Balise BLABLA :  paragraphe de texte
        '''))
        
        tree = ET.ElementTree(article)
        tree.write(self.filePath, pretty_print=True, xml_declaration=True,   encoding="utf-8")

        
        
class ArticleItem:
    ''' represents a section of the article
    the item is a first level item in the XML file
    It can be one of the tags :
    - TITLE , single head title
    - HEAD_PICTURE , the one that will be shared on FB
    - BLA_BLA
    - VIDEO
    - SPACER
    - PHOTO 
    - PHOTOS, which is a collection of PHOTO_Items (tag PHOTO)
    The article is a succesion of items, ordered as they are ordered in the XML file
    
    '''
    def __init__(self, xmlElement):
        self._tag = xmlElement.tag;
        
    def getBeforeCode(self):
        ''' 
        gets the code (ex style) that must be put before
        '''
        html = ''
        return html
    
    def getHtml(self, translator):
        '''
        gets the html content of the item
        '''
        html = ''
        return html
    
    def getAfterCode(self):
        ''' 
        gets the code that bust be put after
        '''
        html = ''
        return html
    
    def resetClass(self):
        ''' 
        Resets static variables to their initial value
        '''
        pass
    
class TITLE_Item(ArticleItem):
    ''' 
    TITLE_Item is a class holding a title 
    It represents a TITLE tag in the XML file
    ''' 
    formats = {
        'H1' : '''<h1 style="color: red; text-align: center;"><span style="background-color:yellow;">&nbsp;&nbsp;&nbsp;
       ${TITLE}
       &nbsp;&nbsp;&nbsp;</span></h1>
       <br><br><br>
        ''',
        'H2' : '<br><br><h2 style="color: blue;">${TITLE}</h2><br><br>\n',
        'H3' : '<br><h3 style="color: blue;"><u>${TITLE}</u></h3><br>\n',
                }
       
    def __init__(self, titleElement):
        super().__init__(titleElement)
        self.title = titleElement.text  
        try:
            self.format = titleElement.get('format').upper()
        except:
            self.format = None
        if not self.format in TITLE_Item.formats.keys():
            self.format = "H1"
        
    def getHtml(self, translator):
        t = Template(TITLE_Item.formats[self.format])
        html = ''
        html += t.substitute(TITLE = translator.translate(self.title))
        return html 

class HEAD_PICTURE_Item(ArticleItem):
    ''' 
    HEAD_PICTURE_Item is a class holding a Central picture for the beginning of the article
    It is the picture that will be shared on FaceBook (with adequat plugin)
    It represents a HEAD_PICTURE tag in the XML file
    ''' 
    HEAD_PICTURE_CODE = '<center><img src="${PICTURE}" ${WIDTH} alt="FB"></center><br><br>\n'
    def __init__(self, element):
        super().__init__(element)
        self.picture = RELPATH_ON_SITE + element.text  
        self.width = element.get('width')
        
    def getHtml(self, translator):
        width = '' if self.width is None else 'width="{}"'.format(self.width)
        html = ''
        html += Template(HEAD_PICTURE_Item.HEAD_PICTURE_CODE).substitute(PICTURE = self.picture, WIDTH = width)
        return html
    
class BLABLA_Item(ArticleItem):
    ''' 
    BLABLA_Item is a class holding a paragraph of the article
    It represents a BLABLA tag in the XML file
    ''' 
    def __init__(self, element):
        super().__init__(element)
        self.blabla = element.text   
        
    def getHtml(self, translator):
        html = ''
        html += '<p>'
        html += translator.translate(self.blabla).replace('\n','<br>\n')
        html += '</p>\n'
        return html

class VIDEO_Item(ArticleItem):
    ''' 
    VIDEO_Item is a class holding a Youtube video reference of the article
    It represents a VIDEO tag in the XML file
    ''' 
    YOUTUBE_CODE = '''
<iframe width="${WIDTH}" height="${HEIGHT}" src="https://www.youtube.com/embed/${VIDEO}" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>
'''
    def __init__(self, element):
        super().__init__(element)
        self.video = element.text  
        if "https://youtu.be/"  in self.video :
            self.video = self.video[17:]
        width = element.get('width')
        self.width = 560 if width is None else width
        height = element.get('height')
        self.height = 315 if height is None else height
        
    def getHtml(self, translator):
        html = ''
        html += Template(VIDEO_Item.YOUTUBE_CODE).substitute(VIDEO=self.video, WIDTH=self.width, HEIGHT=self.height)
        html += '\n'
        return html

class SPACER_Item(ArticleItem):
    ''' 
    SPACER_Item is a line spacer in the article
    It represents a SPACER tag in the XML file
    The attribute "lines" gives the number of lines to jump
    ''' 
    def __init__(self, element):
        super().__init__(element)
        self.lines = element.get('lines') 
        
    def getHtml(self, translator):
        html = ''
        html +=  '\n' + "<br>" * int(self.lines) + '\n'
        return html
        
class PHOTO_Item(ArticleItem):
    ''' 
    PHOTO_Item is a class holding a photo with its description 
    It represents a PHOTO tag in the XML file
    '''
    styleAlreadyDelivered = False # Class variale
    NumberAllocator = 1 # Class variale
    SOLO_PHOTO = '''
    <table>
    <tr><td>${IMGCODE}</td></tr>
    <tr><td style="text-align:  center;"><p id=${CAPTIONID}>${CAPTION}</p></td></tr>
    </table>
    '''
    IMAGE = '<img class="autoLBNArticleSoloPhoto" src="${SRC}" alt="${ALT}" id="${IDIMG}" onclick = "javascript:setModalImg(\'${IDIMG}\',\'${IDCAPTION}\')" ${WIDTH}/>'
    def __init__(self, photoElement):
        global RELPATH_ON_SITE
        super().__init__(photoElement)
        try:
            self.photoName = photoElement.find("NAME").text
        except:
            self.photoName = ''
        try:
            self.photoCaption = photoElement.find("DESCRIPTION").text
        except:
            self.photoCaption = ' '
        self.width = photoElement.get('width')  
        self.photoId = 'img_' + self.photoName
        self.captionId = 'caption_' + self.photoName
        self.photoPath = RELPATH_ON_SITE + self.photoName
        if photoElement.getparent().tag != 'PHOTOS':
            self.soloPhoto = True
            self.photoNumber = 0  # will not be displayed
        else:
            self.soloPhoto = False
            self.photoNumber = PHOTO_Item.NumberAllocator
            PHOTO_Item.NumberAllocator += 1
        
    def resetNumbering(self):
        ''' 
        Resets only the photo number to initial value
        '''
        PHOTO_Item.NumberAllocator = 1
        
    def resetClass(self):
        ''' 
        Resets static variables to their initial value
        '''
        PHOTO_Item.styleAlreadyDelivered = False 
        PHOTO_Item.NumberAllocator = 1 

    def getHtml(self, translator):  # used in case of Solo photos (outside of PHOTOS collections)
        width = ' width=' + ( '320' if self.width is None else self.width )
        t1 = Template(PHOTO_Item.IMAGE)
        imgcode = t1.substitute(SRC = self.photoPath, ALT = self.photoName, IDIMG = self.photoId, IDCAPTION = self.captionId, WIDTH = width)
        caption = translator.translate(self.photoCaption) 
        t2 = Template(PHOTO_Item.SOLO_PHOTO)
        html = t2.substitute(IMGCODE = imgcode, CAPTIONID = self.captionId, CAPTION = caption )
        return html        
        
    def getThumbNailHtml(self):
        html = ''
        html += '<td  class=autoLBNArticlePhoto>\n'
        html += '' if self.photoNumber == 0 else '<div class=autoLBNArticleNumber>- ' + str(self.photoNumber) + ' -</div><br>\n'
        html +=  self.zoomableImage(self.photoPath, self.photoId, self.captionId) 
        html += '</td>\n'
        return html
        
    def getCaptionHtml(self, translator):
        html = ''
        html += '<td  class=autoLBNArticleCaption>\n'
        html += '<p id="' + self.captionId + '">' + translator.translate(self.photoCaption) + '</p>\n'
        html += '</td>\n'
        return html
    
    def zoomableImage(self, src, idImg, idCaption, alt=''):
        width = " width=" + ( self.width if self.width else '320' )
        html = ''
        html += '<div class="autoLBNArticleThumbnail">\n'
        html += '<div class="autoLBNArticleImage">'
        t = Template(PHOTO_Item.IMAGE)
        html += t.substitute(SRC = src, ALT = alt, IDIMG = idImg, IDCAPTION = idCaption, WIDTH = width)
        html += '</div>\n'
        html += '</div>\n'
        return html
    
    def getBeforeCode(self):        
        return '''
<style>
.autoLBNArticleSoloPhoto  {
    cursor: pointer;
}
</style>
'''
    
class PHOTOS_Item(ArticleItem):
    ''' 
    PHOTOS_Item is a class holding a collection of PHOTO items
    It represents a PHOTOS tag in the XML file
    The attribute "format" holds the style of layout of the collection
    It can be :
    - Table_1col'
    - Table_2col
    - Carousel
    ''' 
    # class variables
    styleAlreadyDelivered = False  
    carouselStyleAlreadyDelivered = False  
    table1AfterCodeAlreadyDelivered = False
    carouselAfterCodeAlreadyDelivered = False
    
    def __init__(self, photosElement):
        super().__init__(photosElement)
        self.photos = [ PHOTO_Item(photoElement)  for photoElement in photosElement if photoElement.tag is not ET.Comment] 
        self.format = photosElement.get("format")
        self.photos[0].resetNumbering()  # numbering restarts from 1 for next photo table
        
    def resetClass(self):
        ''' 
        Resets static variables to their initial value
        '''
        PHOTOS_Item.styleAlreadyDelivered = False  
        PHOTOS_Item.carouselStyleAlreadyDelivered = False  
        PHOTOS_Item.table1AfterCodeAlreadyDelivered = False
        PHOTOS_Item.carouselAfterCodeAlreadyDelivered = False 
    
    def getHtml(self, translator):    
        if self.format == 'Table_1col':
            html = self.getHtml_1col(translator)
        elif self.format == 'Table_2col':
            html = self.getHtml_2col(translator)
        elif self.format == 'Carousel':
            html = self.getHtml_Carousel(translator)     
        return html
        
    def getHtml_1col(self, translator):
        html = ''
        html += "<table class=autoLBNArticleTable>\n"
        for photo in self.photos:
            html += "<tr class=autoLBNArticleTable>\n"
            html += photo.getThumbNailHtml()
            html += photo.getCaptionHtml(translator)
            html += "</tr>\n"
        html += "</table>\n"
        return html 
     
    def getHtml_2col(self, translator):
        html = ''
        html += "<table class=autoLBNArticleTable>\n"
        iphotos = iter(self.photos)
        for photo1 in iphotos:
            t1 = photo1.getThumbNailHtml()
            c1 = photo1.getCaptionHtml(translator)
            try:
                photo2 = next(iphotos)
                t2 = photo2.getThumbNailHtml()
                c2 = photo2.getCaptionHtml(translator)                
            except:
                t2 = ' '
                c2 = ' '
            html += "<tr class=autoLBNArticleTable>\n"
            html += t1
            html += t2
            html += "</tr>\n"
            html += "<tr class=autoLBNArticleTable>\n"    
            html += c1
            html += c2                
            html += "</tr>\n"
        html += "</table>\n"
        return html  
    
    def getHtml_Carousel(self, translator):
        n = 0
        N = len(self.photos)           
        html = '''
<div class="autoLBNArticleSlideshow-container">
'''
        for photo in self.photos:
            n += 1
            html += '<div class="autoLBNArticleSlides autoLBNArticleFade">\n'
            caption = translator.translate(photo.photoCaption).replace('\n','<br>\n')
            photoPath = RELPATH_ON_SITE + photo.photoName
            html += '  <div class="autoLBNArticleNumbertext">' + str(n) + '/' + str(N) + '</div>\n'
            html += '  <img class="autoLBNArticleImg" src="' + photoPath + '">\n'
            html += '  <div class="autoLBNArticleText">' + caption + '</div>\n'
            html += '</div>\n'
        html += '''
  <a class="autoLBNArticlePrev" onclick="plusSlides(-1)">&#10094;</a>
  <a class="autoLBNArticleNext" onclick="plusSlides(1)">&#10095;</a>
</div>
<br>
<div style="text-align:center">
'''
        for i in range(1,N+1):
            html += '  <span class="autoLBNArticleDot" onclick="currentSlide(' + str(i) + ')"></span>\n'
        html += '''
</div>
'''        
        return html
    
    def getBeforeCode(self):    
        if self.format == 'Table_1col':
            return self.getBeforeCode_1col()
        elif self.format == 'Table_2col':
            return self.getBeforeCode_1col()
        elif self.format == 'Carousel':
            return self.getBeforeCode_Carousel() 
        
    def getBeforeCode_1col(self):
        if PHOTOS_Item.styleAlreadyDelivered:
            return ''
        else:
            PHOTOS_Item.styleAlreadyDelivered = True
            return '''
<style>

.autoLBNArticleTable, .autoLBNArticleCaption, .autoLBNArticlePhoto {
    border-spacing: 3px;
    border-collapse: separate;
    border: 1px solid black;
}

.autoLBNArticlePhoto {
    width: 320px;
    text-align: center;
    padding: 10px; 
    position: relative;
}

.autoLBNArticleNumber {
    vertical-align: top; 
    position: absolute;
    top : 0;
    left:45%;
}

.autoLBNArticleCaption {
    width: 320px;
    text-align: left; 
    padding: 10px;
}

.autoLBNArticleThumbnail {
    width: 320px;
    text-align: center; 
}

.autoLBNArticleImage {
    width: 100%;
    height: 100%;    
}

.autoLBNArticleImage img {
    -webkit-transition: all 1s ease; /* Safari and Chrome */
    -moz-transition: all 1s ease; /* Firefox */
    -ms-transition: all 1s ease; /* IE 9 */
    -o-transition: all 1s ease; /* Opera */
    transition: all 1s ease;
    border-radius: 5px;
    cursor: pointer;
}

.autoLBNArticleImage:hover img {
    -webkit-transform:scale(2); /* Safari and Chrome */
    -moz-transform:scale(2); /* Firefox */
    -ms-transform:scale(2); /* IE 9 */
    -o-transform:scale(2); /* Opera */
     transform:scale(2);
     transition-delay: 1s;
     z-index: 2;
}

/* Modal window when image is clicked */
/* The Modal (background) */
.autoLBNArticleModal {
    display: none; /* Hidden by default */
    position: fixed; /* Stay in place */
    z-index: 1; /* Sit on top */
    padding-top: 100px; /* Location of the box */
    left: 0;
    top: 0;
    width: 100%; /* Full width */
    height: 100%; /* Full height */
    overflow: auto; /* Enable scroll if needed */
    background-color: rgb(0,0,0); /* Fallback color */
    background-color: rgba(0,0,0,0.9); /* Black w/ opacity */
    z-index: 3;   /* Bring on top */
}

/* Modal Content (image) */
.autoLBNArticleModal-content {
    margin: auto;
    display: block;
    width: 90%;
    max-width: 800px;
    height: auto;
}

/* Caption of Modal Image */
.autoLBNArticleModal-caption {
    margin: auto;
    display: block;
    width: 80%;
    max-width: 700px;
    text-align: center;
    color: #ccc;
    padding: 10px 0;
    height: 150px;
}

/* Add Animation */
.autoLBNArticleModal-content, #autoLBNArticleCaption {    
    -webkit-animation-name: zoom;
    -webkit-animation-duration: 0.6s;
    animation-name: zoom;
    animation-duration: 0.6s;
}

@-webkit-keyframes zoom {
    from {-webkit-transform:scale(0)} 
    to {-webkit-transform:scale(1)}
}

@keyframes zoom {
    from {transform:scale(0)} 
    to {transform:scale(1)}
}

/* The Close Button */
.autoLBNArticleClose {
    position: absolute;
    top: 15px;
    right: 35px;
    color: #f1f1f1;
    font-size: 40px;
    font-weight: bold;
    transition: 0.3s;
}

.autoLBNArticleClose:hover,
.autoLBNArticleClose:focus {
    color: #bbb;
    text-decoration: none;
    cursor: pointer;
}

/* 100% Image Width on Smaller Screens */
@media only screen and (max-width: 700px){
    .modal-content {
        width: 100%;
    }
}

</style>

<!-- The Modal window for photo display when clicked -->
<div id="autoLBNArticleMyModal" class="autoLBNArticleModal">

  <!-- The Close Button -->
  <span class="autoLBNArticleClose" onclick = "closeModalImg()">&times;</span>

  <!-- Modal Content (The Image) -->
  <img class="autoLBNArticleModal-content" id="autoLBNArticleModalImg">

  <!-- Modal Caption (Image Text) -->
  <div class="autoLBNArticleModal-caption" id="autoLBNArticleModalCaption"></div>
</div>        
'''  
        
    def getBeforeCode_Carousel(self):
        if PHOTOS_Item.carouselStyleAlreadyDelivered:
            return ''
        else:
            PHOTOS_Item.carouselStyleAlreadyDelivered = True
            return ''' 
<style>
.autoLBNArticleSlides {display: none}

.autoLBNArticleImg {
  vertical-align: middle;
  width: 60%; 
  max-width: 600px;
}

/* Slideshow container */
.autoLBNArticleSlideshow-container {
  max-width: 1000px;
  position: relative;
  margin: auto;
  text-align: center;
  background-color: black;
}

/* Next & previous buttons */
.autoLBNArticlePrev, .autoLBNArticleNext {
  cursor: pointer;
  position: absolute;
  top: 50%;
  width: auto;
  padding: 16px;
  margin-top: -22px;
  color: white;
  font-weight: bold;
  font-size: 36px;
  transition: 0.6s ease;
  border-radius: 0 3px 3px 0;
}

/* Position the "next button" to the right */
.autoLBNArticleNext {
  right: 0;
  border-radius: 3px 0 0 3px;
}
/* Position the "left button" to the left */
.autoLBNArticlePrev {
  left: 0;
  border-radius: 3px 0 0 3px;
}

/* On hover, add a black background color with a little bit see-through */
.autoLBNArticlePrev:hover, .autoLBNArticleNext:hover {
  background-color: rgba(0,0,0,0.8);
}

/* Caption text */
.autoLBNArticleText {
  color: #f2f2f2;
  font-size: 18px;
  position: absolute;
  bottom: 8px;
  width: 100%;
  text-align: center;
  background-color: rgba(150,100,100,0.6);
}

/* Number text (1/3 etc) */
.autoLBNArticleNumbertext {
  color: #f2f2f2;
  font-size: 12px;
  padding: 8px 12px;
  position: absolute;
  top: 0;
}

/* The dots/bullets/indicators */
.autoLBNArticleDot {
  cursor: pointer;
  height: 15px;
  width: 15px;
  margin: 0 2px;
  background-color: #bbb;
  border-radius: 50%;
  display: inline-block;
  transition: background-color 0.6s ease;
}

.autoLBNArticleActive, .autoLBNArticleDot:hover {
  background-color: #717171;
}

/* Fading animation */
.autoLBNArticleFade {
  -webkit-animation-name: autoLBNArticleFade;
  -webkit-animation-duration: 1.5s;
  animation-name: autoLBNArticleFade;
  animation-duration: 1.5s;
}

@-webkit-keyframes autoLBNArticleFade {
  from {opacity: .4} 
  to {opacity: 1}
}

@keyframes autoLBNArticleFade {
  from {opacity: .4} 
  to {opacity: 1}
}

/* On smaller screens, decrease text size */
@media only screen and (max-width: 300px) {
  .autoLBNArticlePrev, .autoLBNArticleNext, .autoLBNArticleText {font-size: 11px}
}
</style>
'''
 
    def getAfterCode(self):    
        if self.format == 'Table_1col':
            return self.getAfterCode_1col()
        elif self.format == 'Table_2col':
            return self.getAfterCode_1col() # same as 1 col
        elif self.format == 'Carousel':
            return self.getAfterCode_Carousel() 
        
    
    def getAfterCode_1col(self):
        if PHOTOS_Item.table1AfterCodeAlreadyDelivered:
            return ''
        else:
            PHOTOS_Item.table1AfterCodeAlreadyDelivered = True
            return ''' 
<script>
// Get the modal at loading time : no display
var modal = document.getElementById('autoLBNArticleMyModal');
modal.style.display = "none";


// When the user clicks on <span> (x), close the modal   span.onclick = "closeModalImg()"
function closeModalImg() { 
    // Get the modal
    var modal = document.getElementById('autoLBNArticleMyModal');
    // Stop displaying the modal
    modal.style.display = "none";
}

//  Fills the modal with the clicked Image img.onclick = setModalImg(idImg, idCaption) 
function setModalImg(idImg, idCaption) {
    // Get the image and insert it inside the modal 
    var img = document.getElementById(idImg);
    var modalImg = document.getElementById("autoLBNArticleModalImg");
    var captionText = document.getElementById(idCaption);
    var modalCaptionText = document.getElementById("autoLBNArticleModalCaption");
    modalImg.src = img.src;
    modalCaptionText.innerHTML = captionText.innerHTML;  
    // Display the modal
    var modal = document.getElementById('autoLBNArticleMyModal');
    modal.style.display = "block";        
}

</script>
'''   
  
    def getAfterCode_Carousel(self):
        if PHOTOS_Item.carouselAfterCodeAlreadyDelivered:
            return ''
        else:
            PHOTOS_Item.carouselAfterCodeAlreadyDelivered = True
            return ''' 
<script>
function plusSlides(n) {
  showSlides(autoLBNArticleSlideIndex += n);
}

function currentSlide(n) {
  showSlides(autoLBNArticleSlideIndex = n);
}

function showSlides(n) {
  var i;
  var slides = document.getElementsByClassName("autoLBNArticleSlides");
  var dots = document.getElementsByClassName("autoLBNArticleDot");
  if (n > slides.length) {autoLBNArticleSlideIndex = 1}    
  if (n < 1) {autoLBNArticleSlideIndex = slides.length}
  for (i = 0; i < slides.length; i++) {
      slides[i].style.display = "none";  
  }
  for (i = 0; i < dots.length; i++) {
      dots[i].className = dots[i].className.replace(" autoLBNArticleActive", "");
  }
  slides[autoLBNArticleSlideIndex-1].style.display = "block";  
  dots[autoLBNArticleSlideIndex-1].className += " autoLBNArticleActive";
}
</script>

<script>
/* This Script must come after the loading of the Div elements*/
var autoLBNArticleSlideIndex = 1;
showSlides(autoLBNArticleSlideIndex);
</script>
'''


                              
class GuppyArticle:
    ''' class for a guppy article
        Holds all the contents of the article
    '''    
    def __init__(self, element):  # xmlElement ARTICLE
        global RELPATH_ON_SITE
        try:
            self.relpath_on_site = element.get('relpath_on_site')
            if self.relpath_on_site.strip()[-1] != '/':
                self.relpath_on_site += '/'
            RELPATH_ON_SITE = self.relpath_on_site 
        except:
            print("Erreur: L'élément ARTICLE du fichier ne possède pas d'attribut 'relpath_on_site'.")
            exit(0)
        try:
            self.lang = eval(element.get('lang'))
        except:
            self.lang = ('Fr')
        self.elements = []
        for subElement in element:
            try:
                subElementClass = eval( subElement.tag + '_Item')  #  Classes are names like TITLE_Item for instance
                self.elements.append(subElementClass(subElement)) # instantiation and add to elements list
            except:
                pass  # unknown tags or comments
                   
    def composeArticle(self, translator):
        HTML = '===================== Composing - Language ' + translator.toLanguage + ' =====================\n\n\n'      
        for e in self.elements:
            HTML += e.getBeforeCode()
            HTML += e.getHtml(translator)
        for e in self.elements:  # After code must be really after the last element of a type
            HTML += e.getAfterCode()
        HTML += '\n\n\n===================== End of article - Language ' + translator.toLanguage + ' =====================\n\n\n'
        return HTML
    
    def resetClasses(self):
        '''
        resets the static voariables of the used classes
        '''
        for e in self.elements:
            e.resetClass()


if __name__ == "__main__":

    # __doc__ contains the module docstring
    # docopt lib manages the arguments and the manager is built upon the help string provided (posix style). Here we give the docstring
    arguments = docopt(__doc__, version=VERSION)
    #print(arguments)
    #exit(0)
    try:
        DIRPATH = arguments['<path>']
        SOURCE_LANGUAGE = arguments['--sourceLanguage']
        IMAGE_EXTENSION = arguments['--photoType']
        DEBUG = True if arguments['--debug'] else False
    except:
        print("ERROR: Incorrect parameters, use --help.")
        exit(1)
        
    
    articleFile = ArticleFile(os.path.join(DIRPATH, ARTICLEFILE_NAME))
    if not articleFile.exists:
        articleFile.makeTemplateArticleFile()
        print("Le fichier contenant les descriptions n'existe pas, un modèle vient d'être créé.")
        print("Remplissez le fichier {} et relancez le programme {} ensuite.".format(articleFile.filePath, __file__))
        exit(0)
    else:
        article = articleFile.parseArticleFile()
                                 
    outputFile= os.path.join(DIRPATH, OUTPUT_ARTICLEFILE_NAME)
    try:
        os.remove(outputFile)
    except:
        pass
    
    for lang in article.lang:
        articleSource = article.composeArticle(LocalTranslator(SOURCE_LANGUAGE, lang))
        article.resetClasses() # reenable before and after code.
        # print(articleSource)
        with open(outputFile, "a", encoding="utf-8") as f:
            f.write(articleSource)
    print('File generated : {}.'.format(outputFile))