#!/usr/bin/env python3


###################################################
###				PRELIMINARY WORK				###
###################################################

#		  PARSE RAW CSV FILES FOR DB DATA		  #
from sys import stderr

#try to open the files for reading
try:
	responsesCSV = open("responses.csv")
	qdescripts = open("qdescripts")
	columnsCSV = open("columns.csv")
except FileNotFoundError as e:
	print("Your directory appears corrupt, try downloading again.",\
          e, file=stderr)
	exit(1)


def sanitize(badstring):
	'''Fixes the horrible column-naming scheme the data maintainers had'''
	return badstring.replace('"', '')\
	                .replace(' ', '_')\
	                .replace(',', '')\
	                .replace('-', '')\
	                .replace('/', '_')\
	                .replace("'", '')

#read and close files
try:
	responsesRaw = responsesCSV.read().strip().split('\n')
	qdescriptsRaw= qdescripts.read().strip().split('\n')
	columnMapRaw = columnsCSV.read().strip().split('\n')[1:]

	columnNames = [sanitize(col) for col in responsesRaw.pop(0).split('","')]
	results = [repr(tuple(x.strip('"') for x in row.split(',')))\
	           for row in responsesRaw]
	columnMap = {line[0].replace('"', ''): sanitize(line[1])\
	             for line in\
	                 [rawline.split('","') for rawline in columnMapRaw]}

	#makes a list of tuples for the `columns` table, in the form: 
	#(short name, description)
	columns = list()
	for line in qdescriptsRaw:
		#this line's actual pretty neat; the `__repr__` of a python `tuple`
		#happens to be formatted exactly properly for psql `VALUES` insertion
		columns.append(repr((columnMap[line.split(':')[0]], line.replace("'", ''))))

	#A little cleanup in case this gets memory-intesive
	del columnMap
	del responsesRaw
	del qdescriptsRaw
	del columnMapRaw

except Exception as e:
	print("Something wicked happened while reading the source files",\
	      file=stderr)
	print(e, file=stderr)
	exit(1)
finally:
	responsesCSV.close()
	qdescripts.close()
	columnsCSV.close()



###################################################
#		  		  CREATE TABLES					  #
###################################################
import psycopg2 as psql

#pls no hack
connection = psql.connect(host="mprussak.bounceme.net",\
                  dbname="final_project",\
                  user="brennan",\
                  password="403_password_brennan")
db = connection.cursor()
try:
	#first, drop the tables if they exist to avoid collisions
	db.execute("DROP TABLE IF EXISTS columns;")
	db.execute("DROP TABLE IF EXISTS results;")
	connection.commit()

	#Now, (re)create the schema
	db.execute("CREATE TABLE columns ("
	           "	name text PRIMARY KEY,"
	           "	description text NOT NULL"
	           ");")
	db.execute("CREATE TABLE results ("+\
	           "	id serial PRIMARY KEY,"+\
	           " varchar(50), ".join(columnNames)+\
	           " varchar(50));")
	connection.commit()

	#Now populate the schema with our data
	db.execute("INSERT INTO columns (name, description) VALUES"+\
	                ", ".join(columns)+';')
	db.execute("INSERT INTO results ("+','.join(columnNames)+") VALUES"+\
	                ", ".join(results)+';')
	connection.commit()
except Exception as e:
	print("Something wicked happened when connecting to the database.",\
	      e, file=stderr)
	exit(1)
finally:
	db.close()
	connection.close()
