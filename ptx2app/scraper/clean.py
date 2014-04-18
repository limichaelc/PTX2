import re
import json

# used to remove duplicate courses (especially languages)

data = open('finalcopy.txt', 'r')
dictionary = eval(data.read())
data.close()

def main():
    previous = []
    newdict = []
    for i in dictionary:
        #print i.get('booklist')
        #if len(i.get('booklist')) != 0:
         #   if i.get('booklist')[0] == 'error':
                #print p
        #p +=1
        #if len(i.get('booklist')) > 0:
        print i.get('coursename')
            #print i.get('booklist')[0].get('title')
        newdict.append(i)
        previous = i.get('coursedesig')
    #save copy of unduplicated dictionary
    with open('data.json', 'wb') as fp:
        json.dump(newdict, fp)
main()
