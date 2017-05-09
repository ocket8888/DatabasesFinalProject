#!/usr/bin/env python3

import argparse as ap

#Argument Parsing
parser = ap.ArgumentParser(description='Compares student lives from a british survey via pie chart.', usage="%(prog)s [-l | -h | <question> <answer> <other question>]", epilog="Each entry output using `-l` or `--list` ends with 'keyword=\"<keyword>\"', which specifies the keyword to use when this entry is the <question> or <other_question> argument. <answer> arguments should be given exactly; use quotes to enclose strings that contain spaces. Same thing applies to the way-too-many keywords that have spaces in them due to poor life choices by the data maintainers.")
parser.add_argument('-l', '--list', action='store_true', help="Lists the available questions and the possible respective answer ranges, and exit.")
parser.add_argument("question", default=None, type=str, nargs='?', help="The question to see related info for.")
parser.add_argument("answer", default=None, type=str, nargs='?', help="The answer to the question from <question>.")
parser.add_argument("other_question", default=None, type=str, nargs='?', help="A question to show a breakdown for, given that students also answered <question> with <answer>")

args = parser.parse_args()

#list all the questions from the survey along with their descriptions and column names
#could probably be one hideous, nested list comprehension, but this is hard enough to read as it is
#and any halfway decent python compiler will make that optimization for us.
if args.list:
	descriptions = open("qdescripts").read().strip().split("\n")
	colnames = [line.split("\",\"")[1] for line in open("columns.csv").read().strip().split("\n")]
	output = [descriptions[i]+", keyword=\""+colnames[i] for i in range(0,len(descriptions))]
	print('\n'.join(output))
	exit()

#if we're not listing the questionnaire, we need all three positional arguments.
elif not args.question or not args.answer or not args.other_question:
	print("You must specify a question that students answered a certain way and another question to break down based on that! (use `-h` or `--help` for usage)")
	exit(1)


#at this point we can assume we have a question, an answer and another question to break down
#so execution can continue normally.

###################################################
###		GET THE DATA (NEEDS PSQL SUPPORT)		###
###################################################

colnames = [line.strip().split('\",\"')[1] for line in open("columns.csv").read().strip().split('\n')]
colnames = [colnames[i][0:len(colnames[i])-1] for i in range(0,len(colnames))] #Boy I wish there was a way I knew of to slice to the 'end-1' of an anonymous string

#build a map of column names to column numbers
columns = dict()
for i in range(0, len(colnames)):
	columns[colnames[i]] = i

dummyDatabase = [line.strip().split(',') for line in open("responses.csv").read().strip().split('\n')[1:]]

dataToAnalyze = [entry[columns[args.other_question]] for entry in dummyDatabase if entry[columns[args.question]] is args.answer]

###################################################
### 			END DATA RETRIEVAL				###
###################################################

from collections import Counter
print(dict(Counter(dataToAnalyze)))
