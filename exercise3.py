'''IMPORTING PACKAGES'''
import spacy
import en_core_web_sm
import es_core_news_sm
from collections import Counter

''' LOADING AND PROCESSING THE DATA '''
#We define the file path of the datasets
en_corpus_path = './corpus/en_corpus.txt'
es_corpus_path = './corpus/es_corpus.txt'

#We open the dataset files, apply the SpaCy model and set the default max length to a higher quantity
en_nlp = spacy.load('en_core_web_sm')
with open(en_corpus_path, 'r') as en_file:
    en_corpus = en_file.read().replace('\n', ' ')
en_nlp.max_length = len(en_corpus) + 100
en_doc = en_nlp(en_corpus)

es_nlp = spacy.load('es_core_news_sm')
with open(es_corpus_path, 'r') as es_file:
  es_corpus = es_file.read().replace('\n', ' ')
es_nlp.max_length = len(es_corpus) + 100
es_doc = es_nlp(es_corpus)

''' DEFINING FUNCTIONS '''
#We define a function for extracting a list of nouns that could denote propositional content
def extract_nouns_prop(doc, list_words):
    nouns_prop = []
    for token in doc:
        #Condition for common nouns that are modified by a propositional predicates
        if token.dep_ == "amod" and token.tag_=="ADJ" and token.lemma_ in list_words and token.head.pos_ == "NOUN":
            nouns_prop.append(token.head.lemma_)
    return nouns_prop

#We define a function for extracting a list of nouns that could denote eventive content
def extract_nouns_ev(doc, list_adjs, list_verbs):
    nouns_ev = []
    for token in doc:
        #Condition for common nouns that are modified by a eventive predicate
        if token.dep_ == "amod" and token.tag_=="ADJ" and token.lemma_ in list_adjs and token.head.pos_ == "NOUN":
            nouns_ev.append(token.head.lemma_)
        #Condition for common nouns that are subjects of a verb denoting eventuality
        if token.head.lemma_ in list_verbs and token.dep_ == "nsubj" and token.pos_ == "NOUN":
            nouns_ev.append(token.lemma_)
    return nouns_ev

#We define a function for extracting the words that coincide in two given lists
def intersection(list1, list2):
    return list(set(list1) & set(list2))

#We define a function for sorting alphabetically a given dictionary for facilitating later analyses
def sort_dic(dictionary):
    myKeys = list(dictionary.keys())
    myKeys.sort()
    sorted_dict = {i: dictionary[i] for i in myKeys}
    
    return(sorted_dict)

''' CAPTURING NOUNS THAT CAN DENOTE INFORMATIONAL CONTENT '''
#NOUNS DENOTING INFORMATIONAL CONTENT IN ENGLISH
#Firstly, we create a handmade list of adjectives denoting informational content
en_propositional_predicates = ["true", "false", "factual", "misleading", "deceptive",
                               "fallacious", "deceitful", "ambiguous", "spurious",
                               "mock", "delusive", "literal"]

#Then, we call the function that we have already defined to create a list of nouns
en_nouns_prop = extract_nouns_prop(en_doc, en_propositional_predicates)

#Lastly, we enrich the list of nouns adding two additional conditions that follow a specific structure in English
for token in en_doc:
    #Condition for propositional predicates in copulas
    if token.pos_ == "ADJ" and token.lemma_ in en_propositional_predicates:
        children = [child for child in token.head.children]
        for child in children:
            if child.pos_ == "NOUN" and child.dep_ == "nsubj":
                en_nouns_prop.append(child.lemma_)
    #Condition for common nouns that accept a subordinate clause with a different subject
    if token.head.dep_ == "acl" and token.tag_ == "NOUN" and token.dep_ == "nsubj" and token.head.head.pos_ == "NOUN":
        en_nouns_prop.append(token.head.head.lemma_)

#NOUNS DENOTING INFORMATIONAL CONTENT IN SPANISH
#We repeat the steps that we have previously followed
es_propositional_predicates = ['verdadero', 'falso', 'plausibles', 'implausible', 'cierto', 'verídico',
                               'veraz',  'probado', 'fáctico', 'literal', 'espurio', 'falaz', 'ambiguo' ]

es_nouns_prop = extract_nouns_prop(es_doc, es_propositional_predicates)

#We enrich the list of nouns adding two additional conditions that follow a specific structure in Spanish
for token in es_doc:
    #Condition for propositional predicate in copulas
    if token.head.dep_ == "ROOT" and token.head.pos_ == "ADJ" and token.head.lemma_ in es_propositional_predicates and token.pos_ == "NOUN":
        es_nouns_prop.append(token.lemma_)
    #Condition for common nouns that accept a subordinate clause with the prepositions "de que" and a different subject
    if token.head.dep_ == "acl" and token.dep_ == "nsubj" and token.head.head.pos_ == "NOUN":
        children = [child.text for child in token.head.children]
        if "de" in children and "que" in children:
            es_nouns_prop.append(token.head.head.lemma_)
    
#Then we use the set() function to remove duplicates and we print our results
print('Nouns that can denote informational content in English:', set(en_nouns_prop), '\n')
print('Nouns that can denote informational content in Spanish:', set(es_nouns_prop), '\n')

'''CAPTURING NOUNS THAT CAN DENOTE EVENTUALITY'''
#NOUNS DENOTING INFORMATIONAL CONTENT IN ENGLISH
#Firstly, we create a handmade list of adjectives, verbs, and nouns denoting eventive content
en_eventive_predicates = ["enduring", "lasting", "long-lived", "long-running", "long-established",
                          "long-standing", "lifelong", "permanent", "abiding", "durable", "everlasting",
                          "enduring", "long-lasting", "lifelong", "continuing", "remaining", "surviving",
                          "eternal", "perpetual", "infinite", "endless"]
en_eventive_verbs = ['survive' , 'endure', 'continue', 'live', 'hold', 'perish', 'fade', 'die', 'languish',
                     'stop', 'start', 'finish', 'last', 'begin', 'delay', 'prolong', 'elapse', 'culminate',
                     'maintain', 'remain', 'commence']
en_eventive_pp = ["minute", "hour", "month", "day", "year", "second", "week"]

#Then, we call the function that we have already defined to create a list of nouns
en_nouns_ev = extract_nouns_ev(en_doc, en_eventive_predicates, en_eventive_verbs)

#Lastly, we enrich the list of nouns adding two additional conditions that follow a specific structure in English
for token in en_doc:
    #Condition for eventive predicates in copulas
    # for token in en_doc:
    #   if token.pos_ == "ADJ" and token.lemma_ in en_eventive_predicates:
    #     children = [child for child in token.head.children]
    #     for child in children:
    #       if child.pos_ == "NOUN" and child.dep_ == "nsubj":
    #         en_nouns_prop.append(child.lemma_)
    #Condition for '5-minute break'
    if token.pos_ == "NOUN" and token.dep_ == 'pobj' and token.lemma_ in en_eventive_pp and token.head.dep_ == 'prep' and token.head.head.pos_ == "NOUN":
        en_nouns_ev.append(token.head.head.lemma_)
    #Condition for 'a break of 5 minutes'
    if token.pos_ == "NOUN" and token.dep_ == 'compound' and token.lemma_ in en_eventive_pp and token.head.pos_ == "NOUN":
        en_nouns_ev.append(token.head.lemma_)

#NOUNS DENOTING INFORMATIONAL CONTENT IN SPANISH
#We repeat the steps that we have previously followed
es_eventive_predicates = ["duradero", "perdurable", "eterno", "inacabable", "indefinido", "inextinguible",
                          "inmemorial", "inmortal", "perenne", "persistente", "prolongado", "sempiterno",
                          "infinito", "interminable", "perpetuo", "imperecedero"]
es_eventive_verbs = ["durar", "comenzar", "empezar", "terminar", "iniciar", "continuar",
                     "finalizar", "acabar", "inaugurar", "demorar", "prolongar", "transcurrir",
                     "abarcar", "culminar", "mantener", "permanecer"]
es_eventive_pp = ["hora", "minuto", "año", "mes", "segundo", "semana"]

es_nouns_ev = extract_nouns_ev(es_doc, es_eventive_predicates, es_eventive_verbs)

#We enrich the list of nouns adding an additional conditions that follows a specific structure in Spanish
for token in es_doc:
    #Condition for eventive predicates in copulas
    # for token in es_doc:
    #   if token.head.dep_ == "ROOT" and token.head.pos_ == "ADJ" and token.head.lemma_ in es_eventive_predicates and token.pos_ == "NOUN":
    #     es_nouns_prop.append(token.lemma_)
    #Condition for 'un descanso de cinco minutos'
    if token.tag_ == "NUM" and token.head.dep_ == "nmod" and token.head.lemma_ in es_eventive_pp and token.head.head.tag_ == "NOUN" and token.head.head.pos_ == "NOUN":
        es_nouns_ev.append(token.head.head.lemma_)

#Finally, we use the set() function to remove duplicates and we print our results
print('Nouns that can denote eventuality in English:', set(en_nouns_ev), '\n')
print('Nouns that can denote eventuality in Spanish:', set(es_nouns_ev), '\n')

'''CAPTURING COINCIDENCES BETWEEN THE TWO CLASSES'''
#We call the function for extracting the coincidences of the two categories in each language
en_coincidences = intersection(en_nouns_prop, en_nouns_ev)
es_coincidences = intersection(es_nouns_prop, es_nouns_ev)

print('Intersections between these classes in English:', en_coincidences, "\n")
print('Intersections between these classes in Spanish:', es_coincidences, '\n')

########### MEASURING THE FREQUENCY OF THE COINCIDENCES IN EACH LIST ###########
#We use the Counter function to measure the frequency of each token in each category of the two languages
en_freq_prop = Counter(en_nouns_prop)
en_freq_ev = Counter(en_nouns_ev)

es_freq_prop = Counter(es_nouns_prop)
es_freq_ev = Counter(es_nouns_ev)

#Then, we define a function to filter each frequency list by the coincidences of both lists
def en_my_filtering_function(pair):
    #We define the words that we want to maintain in each frequency list
    wanted_keys = ['word', 'judgment', 'love', 'legend', 'life', 'fairy', 'man', 'half']
    key, value = pair
    if key in wanted_keys:
        #Keep the pair in the list
        return True
    else:
        #Deletes the pair out of the list
        return False

def es_my_filtering_function(pair):
    #We define the words that we want to maintain in each frequency list
    wanted_keys = ['cuestión', 'importancia', 'espacio', 'necesidad', 'cavilación', 'noticia', 'oración', 'año', 'señorito', 'sentimiento', 'soplo', 'mujer', 'vez', 'momento', 'matiz', 'conquista', 'casa', 'talento', 'guisa', 'ciudad', 'mano', 'estado', 'don', 'amor', 'expresión', 'señora', 'juez', 'resto', 'madre', 'campo', 'riqueza', 'cosa', 'gobierno', 'gloria', 'fenómeno', 'vida', 'señor', 'situación', 'instante', 'condición', 'personaje', 'familia', 'palabra', 'vista', 'mirada', 'arma', 'ilusión', 'persona', 'alma', 'sitio', 'voz', 'teniente', 'obra', 'recurso', 'hombre', 'cuerpo', 'dicha', 'ciencia', 'número', 'amigo', 'tiniebla', 'saber', 'protesta', 'peligro', 'temor', 'lujo', 'acto', 'dueño']
    key, value = pair
    if key in wanted_keys:
        #Keep the pair in the list
        return True
    else:
        #Deletes the pair out of the list
        return False

#We apply the function that was defined just above for each category of each language
en_coincidences_prop = dict(filter(en_my_filtering_function, en_freq_prop.items()))
en_coincidences_ev = dict(filter(en_my_filtering_function, en_freq_ev.items()))

es_coincidences_prop = dict(filter(es_my_filtering_function, es_freq_prop.items()))
es_coincidences_ev = dict(filter(es_my_filtering_function, es_freq_ev.items()))

#We call the function for sorting the results alphabetically
sorted_en_coincidences_prop = sort_dic(en_coincidences_prop)
sorted_en_coincidences_ev = sort_dic(en_coincidences_ev)

sorted_es_coincidences_prop = sort_dic(es_coincidences_prop)
sorted_es_coincidences_ev = sort_dic(es_coincidences_ev)

#Lastly, we print our results sorted
print('Frequency of intersections with informational content in English:', sorted_en_coincidences_prop, "\n")
print('Frequency of intersections with eventual content in English:', sorted_en_coincidences_ev, "\n", "\n")
print('Frequency of intersections with informational content in Spanish:', sorted_es_coincidences_prop, "\n")
print('Frequency of intersections with eventual content in Spanish:', sorted_es_coincidences_ev)
