#!/usr/bin/env python3


###################################################
###				ARGUMENT PARSING				###
###################################################
import argparse as ap

#Just describes the program and how to use it.
parser = ap.ArgumentParser(\
	description="Compares student lives from a british survey via pie chart. Also outputs line-separated numerical data to stdout in the format:\
		<answer>\\t<number of this answer>\\t<percent of total constituted by this answer>%\
		where '\\t' indicates a tab character.",\
	usage="%(prog)s [-l | -h | -s <question> | -c <question> <answer> <other question>] [-x]",\
	epilog="Each entry output using `-l` or `--list` ends with 'keyword=\"<keyword>\"', which specifies the keyword to use when this entry is the\
		<question> or <other question> argument. <answer> arguments should be given exactly; use quotes to enclose strings that contain spaces.\
		Same thing applies to the way-too-many keywords that have spaces in them due to poor life choices by the data maintainers.\
		Exit codes:\
			0 indicates normal exit,\
			1 indicates manual command-line argument validation failed, and a message will be printed saying why,\
			2 is reserved for errors encountered by the `argparse.ArgumentParser.parse_args()` function, so errors should be verbose")

#These lines each add a command-line argument, as well as handle some meta stuff for them.
parser.add_argument('-l', '--list', action='store_true', help="Lists the available questions and the possible respective answer ranges, and exit.")
parser.add_argument("-c", "--compare", type=str, nargs=3, help="Compares the answers of students to a question based on a given answer for another question.\
	Expects input in the format: '<question> <answer> <other question>', where <question> is the one with the given answer - specified by <answer> - and\
	<other question> is the one to break down. Example: '-c Music 5 Dance' will display a pie chart of the answers to 'Dance, Disco, Funk: Don't enjoy at all - Enjoy very much'\
	for students who answered 'I enjoy listening to music: Strongly disagree - Strongly agree' with '5' (which indicates 'Strongly agree').")
parser.add_argument("-s", "--single", type=str, nargs=1, help="Shows a pie chart detailing the answers to a question.")
parser.add_argument("-x", "--explode", nargs=1, type=str, help="Select an answer to explode. This will explode the pie slice (all assuming that at least one person gave this answer).\
	Must be a valid answer to <question> (if using -s) or <other question> (if using -c).")

args = parser.parse_args() #runs the parser on `ARGV`




#	LIST OPTION and ARGUMENT NUMBER CHECKING	#


from sys import argv, stderr


### This is all stuff we'd need whether we're listing or not ###
colnames = [line.strip().split('\",\"')[1] for line in open("columns.csv").read().strip().split('\n')]
colnames = [colnames[i][0:len(colnames[i])-1] for i in range(1,len(colnames))] #Boy I wish there was a way I knew of to slice to the 'end-1' of an anonymous string#build a map of column names to column numbers
columns = dict()
for i in range(0, len(colnames)):
	columns[colnames[i]] = i
del colnames
descriptions = open("qdescripts").read().strip().split("\n")

#list all the questions from the survey along with their descriptions and column names
#could probably be one hideous, nested list comprehension, but this is hard enough to read as it is
#and any halfway decent python compiler will make that optimization for us.
if args.list:
	output = [descriptions[columns[keyword]]+", keyword=\""+keyword+'"' for keyword in columns]
	print('\n'.join(output))
	exit()

#if we're not listing the questionnaire, we need either `-s` or `-c`.
elif not args.single and not args.compare:
	print("You must specify something for me to do! (use `-h` or `--help` for usage)", file=stderr)
	exit(1)


#at this point we can assume we have a question, an answer and another question to break down
#so execution can continue normally.



###################################################
###				DATA RETRIEVAL					###
###################################################
#TODO - Replace this with actual sql, which may affect formatting later.
#Also, don't forget that the dumb data has quotes in it when it's already COMMA SEPARATED THERE'S NO NEED TO QUOTE A STRING WHEN THE END OF A COLUMN IS STRICTLY SPECIFIED BY COMMAS AND BY THE WAY WHY IS THE FORMAT OF COLUMNS.CSV SO MUCH WORSE THAN THE KAGGLE DESCRIPTION AND WHY DO YOU PUT SPECIAL CHARACTERS LIKE '/' AND ',' IN THE !!!SHORT!!! !!!NAMES!!! USED FOR !!!!!!!!!!!!!!1COLUMN NAUMANING!!!!!!!!!!1!!!1!!!!!!!!!!!11
dummyDatabase = [[col.strip('"') for col in line.strip().split(',')] for line in open("responses.csv").read().strip().split('\n')[1:]]

if args.single:
	dataToAnalyze = [entry[columns[args.single[0]]] for entry in dummyDatabase]
elif args.compare:
	dataToAnalyze = [entry[columns[args.compare[2]]] for entry in dummyDatabase if entry[columns[args.compare[0]]] == args.compare[1]]



###################################################
### 				DATA OUTPUT					###
###################################################

#				  OUTPUT ON STDOUT				  #

from collections import Counter as count
formattedResults = count([datum if datum else "Didn't Answer" for datum in dataToAnalyze])
total = len(dataToAnalyze)
print("\n".join([key+"\t"+str(formattedResults[key])+"\t"+str(formattedResults[key]*100.0/total)+"%" for key in sorted(formattedResults)]))


#				  PIE CHART OUTPUT				  #

def shortDescription(description):
	'''This just gets rid of extraneous information in question descriptions'''
	shorter = descriptions[columns[description]]
	shorter = shorter.replace(" (integer)","")
	shorter = shorter.replace(" (categorical)","")
	shorter = shorter.replace("1-2-3-4-5", "-")
	return shorter

from matplotlib import pyplot as plt

### set up inputs to matplotlib from the data ###
labels = tuple(sorted(formattedResults)) #pie slice labels
sizes = [formattedResults[label] for label in labels] #just the counts for each label (in the same order!)
explode = [0 for i in range(0, len(labels))] #sets the explode amount for each slice

#set `explode` properly if specified on the command-line
if args.explode:
	#needs to be in a try/catch block, because this will throw an IndexError if nobody gave that answer
	#(even if it's a valid answer)
	try:
		explode[labels.index(args.explode[0])] += 0.1
	except IndexError as e:
		if args.single:
			print(args.explode+" isn't a valid answer to "+args.single[0]+", or nobody gave this answer.", file=stderr)
		elif args.compare:
			print(args.explode+" isn't a valid answer to "+args.compare[2]+", or nobody gave this answer who also answered "+args.compare[0]+" with "+args.compare[1]+'.', file=stderr)

fig1, ax1 = plt.subplots()

#Sets the chart title, if only because it looks weird without one
if args.single:
	fig1.suptitle("Breakdown of Students' Answers to\n'"+shortDescription(args.single[0])+"'", fontsize=24, fontweight='bold')
elif args.compare:
	fig1.suptitle("Breakdown of Students' Answers to\n'"+shortDescription(args.compare[2])+\
		"'\nwho also Answered\n'"+shortDescription(args.compare[0])+\
		"'\nwith '"+args.compare[1]+"'",\
		fontsize=20,\
		fontweight='bold')

#This sets up the plot, and returns `<?>, <text based on data>, <text generated automatically>`
patches, texts, autotexts = ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.2f%%', shadow=True, startangle=45)

#all the pie chart text is way too tiny by default
for i in range(0,len(texts)):
	texts[i].set_fontsize(15)
	autotexts[i].set_fontsize(15)

#These last two lines set the aspect ratio (to 'equal' which guarantees that the pie chart is a circle) and shows the plot window, respectively.
ax1.axis('equal')
plt.show()
