#!/bin/bash

#how I sanitized the data
# side note, people who leave commas in data that's going into a csv deserve all manner of misfortune

file=responses.csv

#first one deletes single quote, double quote, and newline
#second one replaces spaces, dashes, and forward slashes with underscores
#third one replaces null values (,,) with (,\N,)
sed 's#'"'"'\|"\|\\n##g;s# \|, \|-\|/#_#g;s#,,#,\\N,#g' $file > sanitized_$file
