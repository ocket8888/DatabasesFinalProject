#Script to import data from the data file (response.csv) to the database

import pandas as ps
from sqlalchemy import create_engine

file = 'responses.csv'
table = 'responses'
conn_str = 'postgresql://marek@localhost/final_project'

#read csv into a dataframe
responses = ps.read_csv(file)

#strip commas and single quotes
responses.columns = responses.columns.str.replace(',|\'', '')

#convert every character to lowercase
responses.columns = responses.columns.str.lower()

#replace pseudo-whitespace with underscores
responses.columns = responses.columns.str.replace(' |-|/', '_')

#create engine for db connection
engine = create_engine(conn_str)

#run the import
responses.to_sql('responses', engine, if_exists='replace')
