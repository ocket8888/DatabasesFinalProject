#Script to import data from the data file (response.csv) to the database

import psycopg2
from psycopg2.extensions import AsIs

#open the file in read only mode. assumes same directory
file = open('sanitized_responses.csv', 'r')

#get all the column names and sanitize inputs
#I'm not sorry about the following line, sue me (yes, chained replaces are supposedly the fastest)
# actually this kept growing so now I feel a little sorry but not enough to change it
f_columns = file.readline().lower().split(',')

#open a connection to the database. this *should* only work from the local machine
# as the server is configured to require passwords for connections from other machines.
conn = psycopg2.connect("dbname=final_project user=marek")

#create a cursor, the object that actually interacts with the database
cur = conn.cursor()

#delete the table if it exists
cur.execute("DROP TABLE IF EXISTS responses;")

#create a table with one row, just a serial id to serve as the primary key
#it's worth noting the use of transactions, so nothing is permanent until you
# call conn.execute() and if something fails, you'll have to call conn.rollback()
# and start over
cur.execute("CREATE TABLE responses (id SERIAL PRIMARY KEY);")

#add all the columns to the table. short of hardcoding each column, or looking at the next line,
# I couldn't figure out an easy way to distinguish between text and integer columns. so for now
# everything is text, if it turns out to be a significant problem it shouldn't be terribly difficult
# to change.

for column in f_columns:
	#the second parameter has to be a single-item tuple because *reasons*
	#need the AsIs to prevent the addition of unwanted quotes
	cur.execute("ALTER TABLE responses ADD %s text;", [AsIs(column)])

#finally, add the actual data. this shits the easy part
cur.copy_from(file, 'responses', sep=',', columns=f_columns)

conn.commit()
cur.close()
conn.close()
