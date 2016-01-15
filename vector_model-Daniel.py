#!/usr/bin/env python2
# -*- coding: UTF-8 -*-

from __future__ import print_function
import fileinput
import re
import math
import nltk.stem 
from timeit import Timer

"""
	Trabalho para diciplina de Recuperação de Informação
	Aluno: Daniel Fernandes
	Matricula:21201910

"""

def insertionSort(alist):
    for index in range(1,len(alist)):

        currentvalue = alist[index]
        position = index

        while (position>0 and alist[position-1].weight<currentvalue.weight):
            alist[position]=alist[position-1]
            position = position-1

        alist[position]=currentvalue

    return alist

class StopWord:
    def __init__(self, path="stop_word.txt"):
        doc = open(path)
        self.stop_word = set(doc.read().splitlines())
    
    def clean(self, txt):
        new_txt = []
        stemmer = nltk.stem.PorterStemmer()
        for word in txt:
            try:
                w = stemmer.stem(word)
            except:
                w = ""
            if(not w in self.stop_word):
                    new_txt.append(w)
                
                
        return new_txt

class Article:
    campos = set(["PN","RN","AN","AU","TI","SO","MJ","MN","AB","EX","RF","CT"])

    def __init__(self, value={}):
        self.paper_number = "" #PN
        self.record_number = "" #RN
        self.medline_acession_number = "" #AN
        self.author = "" #AU
        self.title = "" #TI
        self.source = ""  #SO
        self.major_subjects = "" #MJ
        self.minor_subjects = "" #MN
        self.abstract = ""#AB
        self.extract = "" #EX
        self.references = "" #RF
        self.citations = "" #CT
        self.txt = None
        self.vector = []
        self.campos_dic = {

        "PN": self.__PN__,
        "RN": self.__RN__,
        "AN": self.__AN__,
        "AU": self.__AU__,
        "TI": self.__TI__,
        "SO": self.__SO__,
        "MJ": self.__MJ__, 
        "MN": self.__MN__,
        "AB": self.__AB__,
        "EX": self.__EX__,
        "RF": self.__RF__,
        "CT": self.__CT__

        }
            
        for k,v in value.items():
            self.k = v 

    def make_index_txt(self, stop_word=StopWord()):
        t = ("%s %s %s %s %s") %(self.title, self.abstract, self.extract, self.major_subjects, self.minor_subjects)
        patterns = [r"\.", r"\,", r"\:", r"\'\w?", r"\"", r"\n", "\?", "\(", "\)", r"\+|<|>|%", r"\b\d+%?"]
        for pattern in patterns: 
            t = str(re.sub(pattern, "", t)) 
        t = str(re.sub(r"/|-", " ", t)) 
        t = t.lower().split()
        t = stop_word.clean(t)
        return t

        
    def __PN__(self, txt):
        #first field in file
        self.paper_number = txt.replace("\n", "")
    def __RN__(self, txt):
        self.record_number = str(int(txt.replace("\n", "")))
    def __AN__(self, txt):
        self.medline_acession_number = txt
    def __AU__(self, txt):
        self.author += txt
    def __TI__(self, txt):
        self.title += txt
    def __SO__(self, txt):
        self.source += txt
    def __MJ__(self, txt):
        self.major_subjects += txt
    def __MN__(self, txt):
        self.minor_subjects += txt
    def __AB__(self, txt):
        self.abstract += txt
    def __EX__(self, txt):
        self.extract += txt
    def __RF__(self, txt):
        self.references += txt
    def __CT__(self, txt):
        #last field in file
        self.citations += txt

    def __gt__(self, another):
        return self.weight < another.weight

    def __hash__(self):
        
        return int(self.record_number)

    def to_dict(self):
        d = {}
        d["paper_number"] = self.paper_number
        d["record_number"] = self.record_number 
        d["medline_acession_number"] = self.medline_acession_number 
        d["author"] = self.author
        d["title"] = self.title
        d["source"] = self.source
        d["major_subjects"] = self.major_subjects
        d["minor_subjects"] = self.minor_subjects
        d["abstract"] = self.abstract
        d["extract"] = self.extract
        d["references"] = self.references
        d["citations"] = self.citations
        return d 

    def __repr__(self):
        return str(int(self.record_number))

    def print_details(self):
        
        print("PN"+ self.paper_number, end="" )
        #print("peso:"+ str(self.weight))
    
        if self.record_number !="" :print("RN"+ self.record_number, end="")
        if self.medline_acession_number !="" :print("AN"+ self.medline_acession_number, end="")
        if self.author !="": print("AU"+ self.author, end="")
        if self.title != "": print("TI"+ self.title, end="")
        if self.source != "" : print("SO"+ self.source, end="")
        if self.major_subjects != "": print("MJ"+ self.major_subjects, end="")
        if self.minor_subjects != "": print("MN"+ self.minor_subjects, end="")
        if self.abstract != "" : print("AB"+ self.abstract, end="")
        if self.extract != "":  print("EX"+ self.extract, end="")
        if self.references != "": print("RF"+ self.references, end="")
        if self.citations != "" : print("CT"+ self.citations, end="")
        return ""


class ArticleBase:
    def __init__(self):
        self.count_articles = 0
        pass
 
    def parser(self, path):
        articles = []
        doc = fileinput.input(path)
        campo_aux = ""
        for line in doc:
            i = 0
            campo = line[:2]
            if(campo == "PN"):
                article = Article()
                self.count_articles += 1
                line = re.sub("^"+campo, "", line)
                article.campos_dic["PN"](line)
                articles.append(article)
                continue
            if(campo in Article.campos):
                campo_aux = str(campo)
                line = re.sub("^"+campo, "", line)
                article.campos_dic[campo](line)
            else:
                article.campos_dic[campo_aux](line)
        return articles

    def make_index(self, articles):
        vocabulary = Vocabulary()
        stop_word = StopWord() 
        for article in articles:
            for word in article.make_index_txt(stop_word):
                vocabulary.add(word, article)
        return vocabulary

    def save_to_file(self, articles, path):
        d = {}
        for article in articles:
            d[hash(article)] = article.to_dict()
        open(path, 'w').write(str(d))

class Vocabulary:
    def __init__(self):
        self.index = {}

    def add(self, key, article):
        if(self.index.get(key, None) == None):
            inverted_list = InvertedList()
            self.index[key] = inverted_list
            self.index[key].add(article)
        else:
            self.index[key].add(article)

    def save_to_file(self, path):
        f = open(path, 'w')
        for k,v in self.index.items():
            f.write("{'%s' : %s}\n" % (k, v))
        f.close()

    def get(self, key, default_value):
        return self.index.get(key, default_value)

    def __getitem__(self, elem):
        return self.index[elem]

    def __repr__(self):
        return str(self.index)

    def items(self):
        return self.index.items()
    
class InvertedList:
    def __init__(self ):
        self.idf = None
        self.tf = None
        self.list = {}
        self.freq_item = 0


    def add(self, article):
        self.freq_item += 1
        if(self.list.get(article, None) == None):
            self.list[article] = 1
        else:
            self.list[article] +=1

    
    def __idf__(self, articles):
        if(len(self.list) == 0):
            return 0
        else:
            return math.log10(len(articles)/float(len(self.list)))

    def __tf__(self, articles, article):
        if(self.list.get(article, None) == None):
            return 0
        else:
            self.tf = 1 + math.log10(self.list[article])
            return self.tf

    def __len__(self):
        return len(self.list)

    def __repr__(self):
        return repr(self.list)



def load_articles(path):
    return eval(open(path).read())

def load_vocabulary(path):
    f = fileinput.input(path)
    voc = {}
    for line in f:
        d = eval(line)
        for k,v in d.items(): 
            voc[k] = InvertedList(v)
    return voc

class QueryBase:
    
    def __init__(self):
        self.p_10 = 0
        self.map = 0
        self.quant_query = 0
        self.time = 0
 
    def parser(self, path, articles, vocabulary):

        doc = fileinput.input(path)
        campo_aux = ""
        query = None
        for line in doc:
            i = 0
            campo = line[:2]
            if(campo == "QN"):
                if(query != None):
                     t = Timer(lambda: query.make_rank(articles, vocabulary))
                     t = t.timeit(number=1)
                     self.time = self.time + t 
                     query.metrics(self)
                     print("Tempo para criar rank e ordenar", t)
                query = Query()
                line = re.sub("^"+campo, "", line)
                query.campos_dic["QN"](line)
                continue

            if(campo in Query.campos):
                campo_aux = str(campo)
                line = re.sub("^"+campo, "", line)
                query.campos_dic[campo](line)
            else:
               query.campos_dic[campo_aux](line)

        t = Timer(lambda: query.make_rank(articles, vocabulary))
        t = t.timeit(number=1)
        self.time = self.time + t
        query.metrics(self)
        print("Tempo para criar rank e ordenar",t)

    def general_metrics(self):
        print("#"*10)
        print("Media do tempo criar rank  e ordenar: %f" % (self.time/float(self.quant_query)))
        print("Media da metrica p@10: %f" % (self.p_10/float(self.quant_query)))
        print("Media da metrica map: %f" % (self.map/float(self.quant_query)))
            
        
class Query:

    campos = set(["QN", "QU", "NR", "RD"])

    def __init__(self):
        self.query_text = ""
        self.query_number = ""
        self.number_relevant = ""
        self.relevant_documents = set()
        self.vector = {}
        self.norma_vector = 0
        self.rank = []

        self.campos_dic = {

        "QN": self.__QN__,
        "QU": self.__QU__,
        "NR": self.__NR__,
        "RD": self.__RD__

        }

    def __QN__(self, txt):
        #first field in file
        self.query_number = int(txt)
    def __QU__(self, txt):
        self.query_text += txt
    def __NR__(self, txt):
        self.number_relevant = int(txt)
    def __RD__(self, txt):
        l = re.findall("(\d+) \d+", txt)
        self.relevant_documents.update(l)

    def make_index_txt(self, stop_word=StopWord()):
        t = self.query_text
        patterns = [r"\.", r"\,", r"\:", r"\'\w?", r"\"", r"\n", "\?", "\(", "\)", r"\+|-|<|>|%", r"\b\d+%?"]
        for pattern in patterns: 
            t = str(re.sub(pattern, "", t)) 
        t = str(re.sub(r"/", " ", t)) 
        t = t.lower().split()
        t = stop_word.clean(t)
        self.text = t
        return t

    def make_norma_vector(self):
        for k, v in self.vector.items():
            self.norma_vector += v * v
         

    def make_vector(self, articles, vocabulary):
        total_article = len(articles)
        for word in self.make_index_txt():
            self.vector[word] = self.__idf__(word, articles, vocabulary)*self.__tf__(word, articles)
        
    def make_rank(self, articles, vocabulary):
        self.make_index_txt()
        self.make_vector(articles, vocabulary)
        self.make_norma_vector()
        total_article = len(articles)
        for article in articles:
            article.weight = 0
            article.norma_vector = 0
            for word in self.text:
                if(vocabulary.get(word, None) != None ):
                    vocab_tf_idf = vocabulary[word].__tf__(articles, article)*vocabulary[word].__idf__(articles) 
                    article.weight += vocab_tf_idf * self.vector[word]
                    article.norma_vector += vocab_tf_idf * vocab_tf_idf
                
            if(self.norma_vector != 0 and article.norma_vector !=0):
                article.weight = article.weight/float(math.sqrt(self.norma_vector) * math.sqrt(article.norma_vector))
                self.rank.append(article)
        self.rank = insertionSort(self.rank)
        

    def __idf__(self, word, articles, vocabulary):
        total_article = len(articles)
        if(vocabulary.get(word, None) != None):
        
            return math.log10(total_article/float(len(vocabulary[word])))
        else:
            return 0

    def __tf__(self, word, total_article):
        total_article = len(articles)
        freq = 0

        if(vocabulary.get(word, None) != None):
            for w in self.text:
                if(w == word):
                    freq += 1
            return 1 + math.log10(freq)
        else:
            return 0

    def count_relevant(self, number):
        count = 0
        for i in range(number):
            doc = self.rank[i]
            if(doc.record_number in self.relevant_documents):
                count += 1
        return count

    def map(self): 
        aux = 0
        count = 0
        cr = 0
        for doc in self.rank:
            count += 1
            if(doc.record_number in self.relevant_documents):
                cr += 1
                aux += cr/float(count)
        aux = aux/float(self.number_relevant)
        return aux
        
    def p_10(self):
        return self.count_relevant(10)/10.0

    def metrics(self, query_base):
        map = self.map()
        p10 = self.p_10()
        print("-"*10)
        print("Query number", self.query_number)
        #print("Query text", self.query_text)
        print("Metrics")
        print("MAP", map)
        print("P@10", p10)
        query_base.p_10 += p10
        query_base.map += map
        query_base.quant_query += 1

import os
base = ArticleBase()
path = "base/"
articles = []
print("Carregando os artigos:", end='')
for p in os.listdir(path):
    print(p, end=' ')
    articles.extend(base.parser(path+ p))
print("[OK]")
print("Criando o indice:", end='')
vocabulary = base.make_index(articles)
print("[OK]")
path = "query/cfquery"
base = QueryBase()
base.parser(path, articles ,vocabulary)
base.general_metrics()
