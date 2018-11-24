# Guppy-CMS Article Maker
Python tool aiming at generating rich and multi-lingual Guppy-CMS articles.

# What it is all about
This project is made only for Guppy-CMS users, you can get it there  : https://www.freeguppy.org/    
I frequently post my work as a craftsman on my Website for know how sharing purposes, and I always make my articles based on a bunch of pictures, youtube videos, explicative texts.    
I publish all articles in two languages, French and English.    
In order to reduce the necessary time to do all that editorial stuff, I have developped this helper code in python.    

# License
This work can be shared under the respect of the Creative Commons License: CC BY-NC-SA 4.0
[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)

	
# About Me
This is personnal work from Christophe Mineau, I am an amateur craftsman, maker and professional software designer.  
Most of my craft work is published on my Website : www.labellenote.fr  
Most of my tooling work is also published on HomeMadeTools.net : http://www.homemadetools.net/builder/Christophe+Mineau   


# How To Use it
Here are the steps that need to be taken :      

* Create a directory and gather all the pictures you want to pubish
* Launch the tool once, with no parameter in that directory :  
	python LBNarticleMaker.py "D:\Guppy\Articles\MyDummyArticle"  
* This creates a template "ARTICLE.xml" file in the directory  
(See an example in that repo)
* Edit the ARTICLE.xml  
It is a generic file with at least one template of all the known XML tags, each corresponding to an article feature.  
You have a large choice of features and layouts.  
You can delete or re-arrange the tags as you wish, put them in different orders, several times etc ...
* In the main article tag, choose the primary langage and possibly a second translation language.
* Fill in you text sections, in the primary language.
* When you are happy, run a second time the tool :  
	python LBNarticleMaker.py "D:\Guppy\Articles\MyDummyArticle"
* This time, an html source file "ARTICLE_SOURCECODE.html" is generated, containing one section for each langage.  
The translated langage is a Google tranlation.
* Copy / paste each langage section source code in the Source box of the Guppy article for that langage.
* Review and correct carefuly the often weird Google translations, and do the final layout adjustments in the Guppy article Box
* Do not forget to upload to your site an equivalent folder with the pictures.


# TAGS
* ```<ARTICLE lang="('Fr', 'En')" relpath_on_site="file/dir1/dir2"></ARTICLE>```

# Examples


# Known issues
It is always possible that Google discontinues its translation service, or at least the free access to it.  
It may alaso happen that the interface suddenly changes. But the community is wide enough to find quickly a solution.

# TODO
Add a sound clip tag.


