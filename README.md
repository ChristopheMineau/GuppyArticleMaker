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

1. Create a directory and gather all the pictures you want to pubish
1. Launch the tool once, with no parameter in that directory :  
	python LBNarticleMaker.py "D:\Guppy\Articles\MyDummyArticle"  
1. This creates a template "ARTICLE.xml" file in the directory  
(See an example in that repo)
1. Edit the ARTICLE.xml  
It is a generic file with at least one template of all the known XML tags, each corresponding to an article feature.  
You have a large choice of features and layouts.  
You can delete or re-arrange the tags as you wish, put them in different orders, several times etc ...
1. In the main article tag, choose the primary langage and possibly a second translation language.
1. Fill in you text sections, in the primary language.
1. When you are happy, run a second time the tool :  
	python LBNarticleMaker.py "D:\Guppy\Articles\MyDummyArticle"
1. This time, an html source file "ARTICLE_SOURCECODE.html" is generated, containing one section for each langage.  
The translated langage is a Google tranlation.
1. Copy / paste each langage section source code in the Source box of the Guppy article for that langage.
1. Review and correct carefuly the often weird Google translations, and do the final layout adjustments in the Guppy article Box
1. Do not forget to upload to your site an equivalent folder with the pictures.


# TAGS

* ```<ARTICLE lang="('Fr', 'En')" relpath_on_site="file/dir1/dir2"> ... </ARTICLE>``` 
	* Article container TAG.
	* Attributes (mandatory):
		* lang : Here you provide the source language and optional second language.  
		* relpath_on_site : Provide  the relative path on the site of the folder

*  ``` <TITLE>MON TITRE</TITLE>```  
	* A title 
	* Attributes (optional):  
		* format = 'h1'  : title level 1  
		* format = 'h2'  : title level 2  
		* format = 'h3'  : title level 3  
		
* ```<HEAD_PICTURE width='600'>my_preferred_picture.jpg</HEAD_PICTURE>```  
	* A picture at top of article, the one that will be shared on FB if you also use my FB addon   
        * Attributes (optional):
        	* width='400' : display width  
		
* ```<BLABLA> your text ... </BLABLA>```  
	* A text paragraph  
	
* ```<PHOTO width='200'>```  
```
	<NAME>one_illustration.jpg</NAME>
    	<DESCRIPTION>Description of the illustration.</DESCRIPTION>
</PHOTO>
```  
	* Attributes (optional):  
        	* width = '200'  : display width  
	* A single picture, anywhere in the article  
	* Sub-tags  (mandatory)  
		* NAME : file name of the photo in the directory  
		* DESCRIPTION : a caption text, leave 1 blank if empty  

* ```<SPACER lines="3"/>```
	* Jump lines  
	* Attributes (mandatory):  
		* lines : number of lines to jump

* ```<VIDEO>https://youtu.be/Ljli2uJJO0k</VIDEO>```  
	* A Youtube video. On Youtube, click share to see the code.  
	* Attributes (optional):  
		* width = '200'  : display width (default 560) 
		* height = '100' : display height (default 315)  
* ```<PHOTOS format='Table_1col'> ```  
  ```
   <PHOTO>
      <NAME>pic0001.jpg</NAME>
      <DESCRIPTION> _ Description1  _</DESCRIPTION>
    </PHOTO>
    ....
  </PHOTOS>
  ```
	* A collection of photos  
	They can be displayed in three ways, tables or slideshow.  
	* Attributes (mandatory):  
		* format : How will be displayed the galery  
			* Table_1col : A 1 column table with picture and description besides  
			* Table_2col : A 2 columns table with picture and description below  
			* Carousel  : a slideshow   
	* Sub-tags  (at least 1)  
		* PHOTO : Photo tag as described above  
 

# Examples


# Known issues
It is always possible that Google discontinues its translation service, or at least the free access to it.  
It may alaso happen that the interface suddenly changes. But the community is wide enough to find quickly a solution.

# TODO
Add a sound clip tag.


