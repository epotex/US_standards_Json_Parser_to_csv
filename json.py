import sys
import urllib2
import simplejson
import argparse
import csv
import re
import time
import logging
import os

##############
"""Logging vars"""
logging.basicConfig(filename='t2k_jstc.log',level=logging.DEBUG, format='%(asctime)s %(message)s') 
logging.info('###############New Run###############')

"""Parser Vars"""
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--Discipline", help="Choose your Discipline (Ela or Math)")
parser.add_argument("-g", "--grade", help="Choose your grade level")
args = parser.parse_args()
#Discipline = args.Discipline """CMD Vars""" 
Discipline = "txmath"
#gradefilter = args.grade """CMD Vars"""
gradefilter = "10"
EDU_LABEL = 'dcterms_educationLevel'
PREF_LABEL = 'prefLabel'
"""Number to name dict"""
NUM2NAME = {'k': 'KINDERGARTEN',
            '1': 'FIRST',
            '2': 'SECOND',
            '3': 'THIRD',
            '4': 'FOURTH',
            '5': 'FIFTH',
            '6': 'SIXTH',
            '7': 'SEVENTH',
            '8': 'EIGHTH',
            '9': 'NINTH',
            '10': 'TENTH',
            '11': 'ELEVENTH',
            '12': 'TWELFTH'}#,
            #'6-8':'SIXTH-EIGHTH'}

"""Descipline to packege"""
Package = {'ela':'CCSS',
           'math':'CCSS',
           'txela':'TEKS',
           'txmath':'TEKS',
           'science':'NGSS'
           }

"""State by discipline"""
stats_list = {'ela':'',
              'math':'',
              'txela': 'TEXAS',
              'txmath': 'TEXAS',
              'science':'NGSS'
              }
"""Name of packege by descipline"""
names = {'ela':'Common Core State Standards',
         'math':'Common Core State Standards',
         'txela':  'Texas Essential Knowledge and Skills',
         'txmath': 'Texas Essential Knowledge and Skills',
         'science':'Next Generation Science Standards'
         }
"""Descipline by descipline arg"""
Discip = {'txela':'ELA',
          'txmath': 'MATH',
          'ela':'ELA',
          'math':'MATH',
          'science':'SICENCE'
          }
urls = {'math' :'MATHURL',
        'ela':'ELAURL',
        'txela':'TXELA',
        'txmath':'TXMATH',
        'science':'SICENCE'
        }
"""Json URLS list"""
urls = {'math' :'https://s3.amazonaws.com/asnstaticd2l/data/manifest/D10003FB.json',
        'ela':'https://s3.amazonaws.com/asnstaticd2l/data/manifest/D10003FC.json',
        'txela':'https://s3.amazonaws.com/asnstaticd2l/data/manifest/D100036C.json',
        'txmath':'https://s3.amazonaws.com/asnstaticd2l/data/manifest/D2486388.json',
        'science':'https://asn.jesandco.org/resources/D2454348_manifest.json'}
try:
    URL = urls[Discipline.lower()]
    URL = urls[Discipline.lower()]
    discipline_name = Discip[Discipline.lower()]
    name = names[Discipline.lower()]
    State =stats_list[Discipline.lower()]
    Standard_Package = Package[Discipline.lower()]
    grade_name = NUM2NAME[gradefilter]
except KeyError:
    pass
Country='USA'
def usage():
    print "Usage:"
    print "t2k_jstc.py -d Discipline -g Grade Level"
    print "Example:"
    print "t2k_jstc.py -d ela -g 7"
    print " "
    print "Currently the following standards supported:"
    print "Standards for ELA"
    print "##########"
    print "Texas standards| txela(for the -d option)"
    print "CCSS standards| ela(for the -d option)"
    print "##########"
    print " "
    print "Standards for Math"
    print "##########"
    print "Texas standards| txmath(for the -d option)"
    print "CCSS standards| math(for the -d option)"
    print "Standards for Science"
    print "##########"
    print "Science  standards| Science(for the -d option)"
  
#Functions:

"""Get the element grade level"""
def get_edu_label(element):
    for age in element[EDU_LABEL]:
        try:
            return age.get(PREF_LABEL)[0]
        except (TypeError, AttributeError):
            continue
"""Set the general ID + output file name prefix"""
def general_id():
    return 'Grade'+'_'+gradefilter

"""Set file name"""
filename = general_id() + '_' + Discipline.upper() + '.'+'csv'

"""Get json """
def get_doc(URL):
    req = urllib2.Request(URL)
    opener = urllib2.build_opener()
    data = opener.open(req)
    logging.info('Read complete')
    return simplejson.load(data)

"""Csv writer """
def csv_output(*args):

    with open(filename, 'a') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', lineterminator='\n', quoting=csv.QUOTE_ALL)
        writer.writerow(args)
    csvfile.close()

"""Get entity by grade level """    
def comparevalue(entity, val):
    for i in entity[EDU_LABEL]:
        try:
            pref = i[PREF_LABEL]
        except (KeyError, TypeError):
            continue
        if pref == val:
            return True
    return False

"""Create entities list"""            
def select_entities(doc, pref_value):
    entities = []
    for entity in doc:
        if comparevalue(entity, pref_value):
            entities.append(entity)
    return entities

"""Get the ASN identifier """
def get_asn_id(urlid):
    if urlid:
        asnid = re.findall("([^\/]+)$", str(urlid))
        return asnid[0]


"""Create the "StatementNotation" for TEKS standards"""

def tx_notation(child,father):
    noteid = re.findall("s/\([^)]*\)//", father['asn_listID'].strip())
    cnoteid = re.findall("s/\([^)]*\)//", child['asn_listID'].strip())
    for note in father['asn_listID'].strip():
        for childnote in child['asn_listID'].strip():
            return noteid[0], cnoteid[0] 
        
def general_notetion(item):
    try:
        return  item['asn_statementNotation'].strip()
    except KeyError:
        pass   
    


"""CCSS ELA Parsing"""

def CCSS_ELA():
    logging.info('Json parding started')
    #First Line decleration
    csv_output(
           Country,
           State.strip(),
           Standard_Package.strip(),
           discipline_name.strip().upper(),
           grade_name.strip(),
           Standard_Package,
           None,
           'FALSE',
           name,
           None
           )   

    for father in e:
        csv_output('father',
                   Country,
                   State,
                   Standard_Package,
                   discipline_name.upper().strip(),
                   grade_name,
                   general_notetion(father),
                   Standard_Package,
                   'FALSE',
                   father['text'].encode( "utf-8" )
                   )
        for child in father['children']:
            for agegroup in child['dcterms_educationLevel']:
                if gradefilter in agegroup.values():
                    #Child
                    csv_output('child',
                        Country.strip(),
                        State.strip(),
                        Standard_Package.strip(),
                        discipline_name.upper().strip(),
                        grade_name,
                        general_notetion(child),
                        general_notetion(father),
                        'FALSE',
                        child['text'].encode( "utf-8" ),
                        )
                    for grandchild in child['children']:
                         try:
  
                             csv_output( 'grand',
                                Country,
                                State,
                                Standard_Package,
                                discipline_name.upper(),
                                grade_name,
                                #get_asn_id(grandchild['id']),
                                child['asn_statementNotation'].strip(),
                                #get_asn_id(children['id']),
                                grandchild['asn_statementNotation'].strip(),
                                'TRUE', 
                                grandchild['asn_statementNotation'].strip(),
                                grandchild['text'].encode( "utf-8" )
                                )
                       
                         except KeyError:
                             continue
                      
    logging.info('Json parding ended')

"""CCSS MATH Parsing"""
def CCSS_Math():
    logging.info('Json parding started')
    #First Line decleration
    csv_output("name",
           Country,
           State.strip(),
           Standard_Package.strip(),
           discipline_name.strip().upper(),
           grade_name.strip(),
           Standard_Package,
           None,
           'FALSE',
           name,
           None
           )  

    for father in e:
        for age in father[EDU_LABEL]:
            if age[PREF_LABEL] == gradefilter:
                csv_output("father",
                           Country,
                           State,
                           Standard_Package,
                           discipline_name.upper().strip(),
                           grade_name,
                           general_notetion(father),
                           Standard_Package,
                           'FALSE',
                           father['text'].encode( "utf-8" )
                           )
                for children in father['children']:
                    csv_output("child",
                               Country.strip(),
                        State.strip(),
                        Standard_Package.strip(),
                        discipline_name.upper().strip(),
                        grade_name,
                        general_notetion(children),
                        general_notetion(father),
                        'FALSE',
                        children['text'].encode( "utf-8" )                        
                        )
                    try:
                        for grandchild in children['children']:
                            csv_output("grandchild",
                                       Country.strip(),
                                State.strip(),
                                Standard_Package.strip(),
                                discipline_name.upper().strip(),
                                grade_name,
                                general_notetion(grandchild),
                                general_notetion(children),
                                'FALSE',
                                general_notetion(grandchild),
                                grandchild['text'].encode( "utf-8" )                            
                                )
                            for grandgrand in grandchild['children']:
                                csv_output("grandgrand",
                                       Country.strip(),
                                State.strip(),
                                Standard_Package.strip(),
                                discipline_name.upper().strip(),
                                grade_name,
                                general_notetion(grandgrand),
                                general_notetion(grandchild),
                                'FALSE',
                                general_notetion(grandgrand),
                                grandgrand['text'].encode( "utf-8" )                            
                                )
                    except KeyError:
                        try:
                            print children['children']
                        except KeyError:
                            continue
    logging.info('Json parding ended')
"""TEKS ELA Parsing"""
def TX_ELA():
    #Headr
    logging.info('Json parding started')
    csv_output(
            Country,
            State,
            Standard_Package,
            discipline_name.strip().upper(),
            grade_name.strip(),
            Standard_Package,
            None,
            'FALSE',
            name,
            None
            )

    for father in e:
      

        csv_output(
                   Country,
                   State,
                   Standard_Package,
                   discipline_name.upper().strip(),
                   grade_name,
                   #get_asn_id(father['id']),
                   'TEKS2014',
                   Standard_Package,
                   'FALSE',
                   father['text'].encode( "utf-8" )
                   )        
        for child in father['children']:
        #Child
         

            #print child.keys()
            csv_output(child['dcterms_educationLevel'],
                Country,
                State,
                Standard_Package,
                discipline_name.upper().strip(),
                grade_name,
                #get_asn_id(child['id']),
                child['asn_listID'].strip('-'),
                #get_asn_id(father['id']),
                'TEKS2014',
                'FALSE',
                child['text'].encode( "utf-8" )
                )
            try:
                for grandchild in child['children']:
                   cnote = str(child['asn_listID'].strip().strip("()"))
                   gnote =  str(grandchild['asn_listID'].strip().strip("()"))
                   StatementNotation =  cnote +"."+ gnote
                   csv_output(grandchild['dcterms_educationLevel'],
                        Country,
                        State,
                        Standard_Package,
                        discipline_name.upper().strip(),
                        grade_name,
                        #get_asn_id(grandchild['id']),
                        StatementNotation,
                        child['asn_listID'].strip('-'),
                        'TRUE',
                        StatementNotation,
                        grandchild['text'].encode( "utf-8" )
                        )
            except KeyError:
                continue                
                try:
                    for grandgrand in grandchild['children']:
                        csv_output(
                            Country,
                            State,
                            Standard_Package,
                            discipline_name.upper(),
                            grade_name,
                            get_asn_id(grandgrand['id']),
                            get_asn_id(grandchild['id']),
                            'TRUE', 
                            grandgrand['text'].encode( "utf-8" )
                            )
                except KeyError:
                    continue
             
            except KeyError:
                continue
    logging.info('Json parding ended')

"""TEKS MATH Parsing"""    

def TX_MATH():
    logging.info('Json parding started')
    #Headr
    csv_output(
            Country,
            State,
            Standard_Package,
            discipline_name.strip().upper(),
            grade_name.strip(),
            Standard_Package,
            None,
            'FALSE',
            name,
            None
            )

    for father in e:
        csv_output(
                   Country,
                   State,
                   Standard_Package,
                   discipline_name.upper().strip(),
                   grade_name,
                   father['id'],
                   Standard_Package,
                   'FALSE',
                   father['text'].encode( "utf-8" )
                   )
        for child in father['children']:
                csv_output(
                Country,
                State,
                Standard_Package,
                discipline_name.upper().strip(),
                grade_name,
                child['id'],
                father['id'],
                'FALSE',
                child['text'].encode( "utf-8" )
                )
                try:
                    for grand in child['children']:
                            #desc = str(child['dcterms_description']['literal'])
                            #cnote =  desc + "." + grandgrand['asn_listID'].strip("()")

                            csv_output(
                                Country,
                                State,
                                Standard_Package,
                                discipline_name.upper().strip(),
                                grade_name,
                                grand['asn_listID'],
                                Standard_Package,
                                'TRUE',
                                grand['text'].encode( "utf-8" )
                                )
                            for grandgrand in grand['children']:
                                desc = str(child['dcterms_description']['literal'])
                                note =  desc + "." + grand['asn_listID'].strip("()") +"." + grandgrand['asn_listID'].strip("()")
                                csv_output(
                                        Country,
                                        State,
                                        Standard_Package,
                                        discipline_name.upper(),
                                        grade_name,
                                        note,
                                        grand['asn_listID'],
                                        'TRUE', 
                                        note,
                                        grandgrand['text'].encode( "utf-8" )
                                        )

                except: KeyError
                continue
     
              
         
    logging.info('Json parding ended')

"""TEKS SCIENCE Parsing"""

def NGSS_SCIENCE():
    logging.info('Json parding started')
    #Headr
    csv_output(
            Country,
            State,
            Standard_Package,
            discipline_name.strip().upper(),
            grade_name.strip(),
            Standard_Package,
            None,
            'FALSE',
            name,
            None
            )

    for father in e:
               
        csv_output(
                   Country,
                   State,
                   Standard_Package,
                   discipline_name.upper().strip(),
                   grade_name,
                   general_notetion(father),
                   Standard_Package,
                   'FALSE',
                   father['text'].encode( "utf-8" )
                   )
        for child in father['children']:
            
            csv_output(
                Country,
                State,
                Standard_Package,
                discipline_name.upper().strip(),
                grade_name,
                general_notetion(child),
                general_notetion(father),
                'FALSE',
                child['text'].encode( "utf-8" )
                )
            try:
                for grandchild in child['children']:
              
                   csv_output(
                        Country,
                        State,
                        Standard_Package,
                        discipline_name.upper().strip(),
                        grade_name,
                        general_notetion(grandchild),
                        general_notetion(child),
                        'TRUE',
                        ' ',
                        grandchild['text'].encode( "utf-8" )
                        )
            except KeyError:
                
                continue                
                try:
                    for grandgrand in grandchild['children']:
                        csv_output(
                            Country,
                            State,
                            Standard_Package,
                            discipline_name.upper(),
                            grade_name,
                            get_asn_id(grandgrand['id']),
                            get_asn_id(grandchild['id']),
                            'TRUE', 
                            grandgrand['text'].encode( "utf-8" )
                            )
                except KeyError:
                    continue
               
            except KeyError:
                continue
    logging.info('Json parding ended')


if __name__ == '__main__':
    
    """Removing old files"""
    logging.info('Removing any old CCSS files')
    if os.path.isfile(filename):
        os.remove(filename)
        logging.info('%s DELETED', filename)
    else:
        logging.info('Could not found any old file to remove...')
        
    """Main ARG selector"""     
    if Discipline.lower() =="ela":
        logging.info('CCSS ELA chosed... Getting the CCSS ELA json')
        logging.info('Parsing for %s grade', gradefilter )
        doc = get_doc(URL)
        e = select_entities(doc, gradefilter)
        CCSS_ELA()
        logging.info('DONE! %s has been created', filename)
    elif Discipline.lower() == "math":
        logging.info('CCSS MATH chosed... Getting the CCSS MATH json')
        logging.info('Parsing for %s grade', gradefilter )
        doc = get_doc(URL)
        e = select_entities(doc, gradefilter)
        CCSS_Math()
        logging.info('DONE! %s has been created', filename)
    elif Discipline.lower() == "txela":
        logging.info('TEKS ELA chosed... Getting the TEKS ELA json')
        logging.info('Parsing for %s grade', gradefilter )
        doc = get_doc(URL)
        e = select_entities(doc, gradefilter)
        TX_ELA()
        logging.info('DONE! %s has been created', filename)
    elif Discipline.lower() == "txmath":
        logging.info('TEKS MATH chosed... Getting the TEKS MATH json')
        logging.info('Parsing for %s grade', gradefilter )
        doc = get_doc(URL)
        e = select_entities(doc, gradefilter)
        TX_MATH()
        logging.info('DONE! %s has been created', filename)
    elif Discipline.lower() == "science":
        logging.info('NGSS science chosed... Getting the NGSS science json')
        logging.info('Parsing for %s grade', gradefilter )
        doc = get_doc(URL)
        e = select_entities(doc, gradefilter)
        NGSS_SCIENCE()
        logging.info('DONE! %s has been created', filename)
    else:
        usage()  
