from __future__ import print_function
import re
import spacy

from pyclausie import ClausIE


nlp = spacy.load('en_core_web_sm')
re_spaces = re.compile(r'\s+')
cl = ClausIE.get_instance()

class Person(object):
    def __init__(self, name, likes=None, has=None, travels=None):
        """
        :param name: the person's name
        :type name: basestring
        :param likes: (Optional) an initial list of likes
        :type likes: list
        :param dislikes: (Optional) an initial list of likes
        :type dislikes: list
        :param has: (Optional) an initial list of things the person has
        :type has: list
        :param travels: (Optional) an initial list of the person's travels
        :type travels: list
        """
        self.name = name
        self.likes = [] if likes is None else likes
        self.has = [] if has is None else has
        self.travels = [] if travels is None else travels

    def __repr__(self):
        return self.name


class Pet(object):
    def __init__(self, pet_type, name=None):
        self.name = name
        self.type = pet_type


class Trip(object):
    def __init__(self,departs_on = None,departs_to = None,departs_time = None):
        self.departs_on = departs_on
        self.departs_to = departs_to
        self.departs_time = departs_time



persons = []
pets = []
trips = []


def process_data_from_input_file(file_path='./assignment_01.data'):
    with open(file_path) as infile:
        cleaned_lines = [line.strip() for line in infile if (not line.startswith(('$$$', '###', '==='))) and line!='']

    return cleaned_lines


def select_person(name):
    for person in persons:
        if person.name == name:
            return person


def add_person(name):
    person = select_person(name)

    if person is None:
        new_person = Person(name)
        persons.append(new_person)

        return new_person

    return person


def select_pet(name2):
    for pet in pets:
        if pet.name == name2:
            return pet


def add_pet(type, name1=None):
    pet = None

    if name1:
        pet = select_pet(name1)

    if pet is None:
        pet = Pet(type, name1)
        pets.append(pet)

    return pet

def selct_trip( on = None , to = None, dep_time = None):
    for trip in trips:
        if trip.departs_on == on and trip.departs_to == to  :
            return trip

def add_trip(on = None, to = None, dep_time = None):
    new_trip  = None
    new_trip = selct_trip(on,to,dep_time)
    if new_trip is None:
        new_trip = Trip(on,to,dep_time)
        trips.append(new_trip)

    return new_trip



def get_persons_pet(person_name):

    person = select_person(person_name)

    for thing in person.has:
        if isinstance(thing, Pet):
            return thing



def process_relation_triplet(triplet):
    """
    Process a relation triplet found by ClausIE and store the data

    find relations of types:
    (PERSON, likes, PERSON)
    (PERSON, has, PET)
    (PET, has_name, NAME)
    (PERSON, travels, TRIP)
    (TRIP, departs_on, DATE)
    (TRIP, departs_to, PLACE)

    :param triplet: The relation triplet from ClausIE
    :type triplet: tuple
    :return: a triplet in the formats specified above
    :rtype: tuple
    """

    sentence = triplet.subject + ' ' + triplet.predicate + ' ' + triplet.object

    doc = nlp(unicode(sentence))

    root = True

    for t in doc:
        if t.pos_ == 'VERB' and t.head == t:
            root = t
        # elif t.pos_ == 'NOUN'

    if root is True:
        return
    # also, if only one sentence
    # root = doc[:].root


    """
    CURRENT ASSUMPTIONS:
    - People's names are unique (i.e. there only exists one person with a certain name).
    - Pet's names are unique
    - The only pets are dogs and cats
    - Only one person can own a specific pet
    - A person can own only one pet
    """


    # Process (PERSON, likes, PERSON) relations
    if root.lemma_ == 'like' and 'neg' not in [t.dep_ for t in root.children]:
        if triplet.subject in [e.text for e in doc.ents if e.label_ == 'PERSON' or e.text in KNOWN_NAMES] and triplet.object in [e.text for e in doc.ents if e.label_ == 'PERSON']:
            s = add_person(triplet.subject)
            o = add_person(triplet.object)
            if o not in s.likes:
                s.likes.append(o)

    if root.lemma_ == 'be' and triplet.object.startswith('friends with') and 'neg' not in [t.dep_ for t in root.children]:
        obj_span = doc.char_span(sentence.find(triplet.object), len(sentence))
        #fw_doc = nlp(unicode(triplet.object))
        #with_token = [t for t in fw_doc if t.text == 'with'][0]
        #fw_who = [t for t in with_token.children if t.dep_ == 'pobj']
        fw_who = [a.text for a in obj_span if a.pos_ == 'PROPN']
        for friend in fw_who:
            if triplet.subject in [e.text for e in doc.ents if e.label_ == 'PERSON'] :  #and fw_who in [e.text for e in doc.ents if e.label_ == 'PERSON']
                s = add_person(triplet.subject)
                o = add_person(friend)
                if o not in s.likes:
                    s.likes.append(o)
                if s not in o.likes:
                    o.likes.append(s)
    if root.text == 'are' and triplet.object == 'friends':
        sub_span = doc.char_span(sentence.find(triplet.subject), len(sentence))
        people = [token.text for token in sub_span if token.ent_type_ == 'PERSON']
        for s in people:
            s = add_person(s)
            for o in [person for person in people if person != s.name]:
                o = add_person(o)
                if o not in s.likes:
                    s.likes.append(o)
                if s not in o.likes:
                    o.likes.append(s)

    # Process (PET, has, NAME)
    if triplet.subject.endswith('name') and ('dog' in triplet.subject or 'cat' in triplet.subject):
        obj_span = doc.char_span(sentence.find(triplet.object), len(sentence))

        # handle single names, but what about compound names? Noun chunks might help.
        for chunks in obj_span.noun_chunks:

            if chunks[0].pos_ == 'PROPN':
                name = chunks
                subj_start = sentence.find(triplet.subject)
                subj_doc = doc.char_span(subj_start, subj_start + len(triplet.subject))

                s_people = [token.text for token in subj_doc if token.ent_type_ == 'PERSON']
                assert len(s_people) == 1
                add_person(s_people[0])
                s_person = select_person(s_people[0])

                s_pet_type = 'dog' if 'dog' in triplet.subject else 'cat'

                pet = add_pet(s_pet_type, str(name))

                s_person.has.append(pet)
    if 'named' in triplet.object and ('dog' in triplet.object or 'cat' in triplet.object):
        sub_triplet = cl.extract_triples([triplet.object+'.'])[0]
        sub_sentence = sub_triplet.subject + ' ' + sub_triplet.predicate + ' ' + sub_triplet.object
        doc2 = nlp(unicode(sub_sentence))
        obj_span = doc2.char_span(sub_sentence.find(sub_triplet.object), len(sub_sentence))
        if obj_span[0].pos_ == 'PROPN':
            name = sub_triplet.object
            subj_start = sentence.find(triplet.subject)
            subj_doc = doc.char_span(subj_start, subj_start + len(triplet.subject))

            s_people = [token.text for token in subj_doc if token.ent_type_ == 'PERSON']
            assert len(s_people) == 1

            add_person(s_people[0])
            s_person = select_person(s_people[0])

            s_pet_type = 'dog' if 'dog' in triplet.object else 'cat'

            pet = add_pet(s_pet_type,name1 = str(name))

            s_person.has.append(pet)


    #Process (PERSON, travels, TRIP)
    if root.lemma_ in ['take','fly','leave','go'] and 'GPE' in [e.label_ for e in doc.ents]:
        obj_span = doc.char_span(sentence.find(triplet.object), len(sentence))
        subj_start = sentence.find(triplet.subject)
        subj_doc = doc.char_span(subj_start, subj_start + len(triplet.subject))

        s_people = [token.text for token in subj_doc if token.ent_type_ == 'PERSON' or token.text in KNOWN_NAMES]
        trip_to = [a.text for a in obj_span if a.ent_type_ == 'GPE']
        trip_time = ' '.join([token.text for token in obj_span if token.ent_type_=='DATE' ])
        for people in s_people:
            people = add_person(people)
            for trip in trip_to:
                trip = add_trip(to=trip,dep_time=trip_time)
                if trip not in people.travels:
                    people.travels.append(trip)




def preprocess_question(question):
    # remove articles: a, an, the

    q_words = question.split(' ')

    # when won't this work?
    for article in ('a', 'an', 'the'):
        try:
            q_words.remove(article)
        except:
            pass
    ques = re.sub(re_spaces, ' ', ' '.join(q_words))
    ques = ques.replace('\'s',' is')
    return ques


def has_question_word(string):
    # note: there are other question words
    for qword in ('who', 'what'):
        if qword in string.lower():
            return True

    return False



def answer_question(question_string = None):
    sents = process_data_from_input_file()

    global KNOWN_NAMES
    KNOWN_NAMES    = {'Joe','Mary','Bob','Sally','Chris'}

    triples = cl.extract_triples(sents)

    for t in triples:
        r = process_relation_triplet(t)
        # print(r)

    question = question_string
    if question[-1] != '?':
        # question = raw_input("Please enter your question: ")


        print('This is not a question... please try again')
        return
    try:
        q_trip = cl.extract_triples([preprocess_question(question)])[0]
        q_sentence = q_trip.subject + ' ' + q_trip.predicate + ' ' + q_trip.object
        q_doc = nlp(unicode(q_sentence))
    except:
        q_trip = cl.extract_triples([preprocess_question('This is a empty question.')])[0]
        q_sentence = q_trip.subject + ' ' + q_trip.predicate + ' ' + q_trip.object
        q_doc = nlp(unicode(preprocess_question(question)))
    #1)     (WHO, has, PET)
    # here's one just for dogs
    if q_trip.subject.lower() == 'who' and (q_trip.object == 'dog' or q_trip.object =='cat'):
        answer = '{} has a {} named {}.'

        for person in persons:
            pet = get_persons_pet(person.name)
            if pet and pet.type == q_trip.object :
                print(answer.format(person.name, q_trip.object, pet.name))

    #2)     (Who is [going to|flying to|traveling to|visiting] <place>?)
    elif 'who' in q_trip.subject.lower() and True in [a in q_trip.predicate for a in ['going','flying','traveling','visiting']] and 'GPE' in [token.ent_type_ for token in q_doc] :
        answer = '{} is going to {}.'
        obj_doc = q_doc.char_span(q_sentence.find(q_trip.object), len(q_sentence))

        place = [token.text for token in obj_doc if token.ent_type_ == 'GPE'][0]

        _p = 0
        for person in persons:
            if place in [travel.departs_to for travel in person.travels]:
                print(answer.format(person.name,place))
                _p = 1
        if _p == 0:
            print(answer.format('No one',place))





    #3)     (Does <person> like <person>?)
    elif 'does' in q_trip.subject.lower() and 'like' in q_trip.predicate and q_trip.object in [e.text for e in q_doc.ents if e.label_ == 'PERSON']:

        subj_start = q_sentence.find(q_trip.subject)
        subj_doc = q_doc.char_span(subj_start, subj_start + len(q_trip.subject))
        s_people = select_person([token.text for token in subj_doc if token.ent_type_ == 'PERSON'][0])
        o_people = select_person(q_trip.object)
        if o_people in s_people.likes:
            print(s_people.name,'like',o_people.name)
        else:
            print(s_people.name,'does not like',o_people.name)


    #4)    (What's the name of <person>'s <pet_type>?)
    elif 'what' in [q.text.lower() for q in q_doc] and 'name' in [q.text.lower() for q in q_doc] and 'PERSON' in [token.ent_type_ for token in q_doc]:

        s_people = select_person([token.text for token in q_doc if token.ent_type_ == 'PERSON'][0])
        # for chunks in q_doc.noun_chunks:
            # for token in chunks:
        pet_type = [t.text for t in q_doc if t.dep_=='attr' and t.pos_=='NOUN']
        pet_type = [p for p in pet_type if p.lower() in ['cat','dog']][0]

                # print(token.text,token.dep_,token.pos_)
                # print('attr','NOUN')
                # if  (str(token.dep_),str(token.pos_)) in [('pobj','NOUN'),[('attr','NOUN')]]:
                #     pet_type = token.text
                #     print(pet_type)
        
        for pet in s_people.has:
            
            if pet.type == pet_type:
                print (s_people.name,"'s ",pet_type,"'s name is ",pet.name)


    #5)     ( When is <person> [going to|flying to|traveling to|visiting] <place>?)
    elif 'when' in q_trip.object.lower() and True in [a in q_trip.predicate for a in['going', 'flying', 'traveling', 'visiting']] and 'GPE' in [token.ent_type_ for token in q_doc]:
        obj_doc = q_doc.char_span(q_sentence.find(q_trip.object), len(q_sentence))
        place = [token.text for token in obj_doc if token.ent_type_ == 'GPE'][0]
        o_people = select_person(q_trip.subject)
        answer = '{} is going to {} at the time of {}'
        for trip in o_people.travels:
            if trip.departs_to == place:
                time = trip.departs_time
        try:
            print(answer.format(o_people.name,place,time))
        except:
            print(o_people.name,' is not going to ',place)


    #6)    (Who likes <person>?)
    elif 'who' in q_trip.subject.lower() and 'likes' in q_trip.predicate and q_trip.object in [e.text for e in q_doc.ents if e.label_ == 'PERSON']:
        o_people = select_person(q_trip.object)
        for p in persons:
            if o_people in p.likes:
                print (p.name ,'likes', o_people.name)
    #7)     (Who does <person> like?)
    elif 'who' in q_trip.object.lower() and 'like' in q_trip.predicate and q_trip.subject in [e.text for e in q_doc.ents if e.label_ == 'PERSON']:
        s_people = select_person(q_trip.subject)
        for p in s_people.likes:
            print (s_people.name,'likes',p.name)
    else:
        print("I don't know.")





# if __name__ == '__main__':
#     main()
#     stop_sign = 1