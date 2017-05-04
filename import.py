#Script to import data from the data file (response.csv) to the database

import pandas as ps
from sqlalchemy import create_engine

#connection string for database. will only work from the local machine anyway
conn_str = 'postgresql://marek@localhost/final_project'

#first file, with responses and short column names
file1 = 'responses.csv'
table1 = 'responses'

#second file, with mappings from short cols to long
file2 = 'columns.csv'
table2 = 'column_mappings'

#create engine for db connection
engine = create_engine(conn_str)

#read csv into a dataframe
responses = ps.read_csv(file1)

#strip commas and single quotes
responses.columns = responses.columns.str.replace(',|\'', '')

#convert every character to lowercase
responses.columns = responses.columns.str.lower()

#replace pseudo-whitespace with underscores
responses.columns = responses.columns.str.replace(' |-|/', '_')

#import the first file
responses.to_sql(table1, engine, if_exists='replace')


#read second csv into dataframe
columns = ps.read_csv(file2)

#switch the column order. the file has original, short, we want short, original
columns = columns[list(reversed(columns.columns.tolist()))]

#apply the same replacements to the short names, so we can match them up
columns.ix[:,0]= columns.ix[:,0].str.replace(',|\'', '')
columns.ix[:,0] = columns.ix[:,0].str.lower()
columns.ix[:,0] = columns.ix[:,0].str.replace(' |-|/', '_')

#import the second file
columns.to_sql(table2, engine, if_exists='replace', index=False)
