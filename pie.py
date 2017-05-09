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
	usage="%(prog)s [-l | -h | <question> <answer> <other question>]",\
	epilog="Each entry output using `-l` or `--list` ends with 'keyword=\"<keyword>\"', which specifies the keyword to use when this entry is the\
		<question> or <other_question> argument. <answer> arguments should be given exactly; use quotes to enclose strings that contain spaces.\
		Same thing applies to the way-too-many keywords that have spaces in them due to poor life choices by the data maintainers.\
		Exit codes:\
			0 indicates normal exit,\
			1 indicates manual command-line argument validation failed, and a message will be printed saying why,\
			2 is reserved for errors encountered by the `argparse.ArgumentParser.parse_args()` function, so errors should be verbose")

#These lines each add a command-line argument, as well as handle some meta stuff for them.
parser.add_argument('-l', '--list', action='store_true', help="Lists the available questions and the possible respective answer ranges, and exit.")
parser.add_argument("question", default=None, type=str, nargs='?', help="The question to see related info for.")
parser.add_argument("answer", default=None, type=str, nargs='?', help="The answer to the question from <question>.")
parser.add_argument("other_question", default=None, type=str, nargs='?', help="A question to show a breakdown for, given that students also answered <question> with <answer>")
parser.add_argument("-x", "--explode", nargs=1, type=str, help="Select an answer to explode. This will explode the pie slice (all assuming that at least one person gave this answer).\
	Must be a valid answer to <other_question>.")

args = parser.parse_args() #runs the parser on `ARGV`




#	LIST OPTION and ARGUMENT NUMBER CHECKING	#


from sys import argv, stderr


### This is all stuff we'd need whether we're listing or not ###
colnames = [line.strip().split('\",\"')[1] for line in open("columns.csv").read().strip().split('\n')]
colnames = [colnames[i][0:len(colnames[i])-1] for i in range(0,len(colnames))] #Boy I wish there was a way I knew of to slice to the 'end-1' of an anonymous string#build a map of column names to column numbers
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

#if we're not listing the questionnaire, we need all three positional arguments.
elif not args.question or not args.answer or not args.other_question:
	print("You must specify a question that students answered a certain way and another question to break down based on that! (use `-h` or `--help` for usage)", stderr)
	exit(1)

from sys import argv
if len(argv) is not 4 and not args.explode:
	print("Expected exactly three arguments, "+repr(len(argv))+" given. (use `-h` or `--help` for usage)", stderr)
	exit(1)


#at this point we can assume we have a question, an answer and another question to break down
#so execution can continue normally.



###################################################
###				DATA RETRIEVAL					###
###################################################
#TODO - Replace this with actual sql, which may affect formatting later.

dummyDatabase = [line.strip().split(',') for line in open("responses.csv").read().strip().split('\n')[1:]]

dataToAnalyze = [entry[columns[args.other_question]] for entry in dummyDatabase if entry[columns[args.question]] is args.answer]



###################################################
### 				DATA OUTPUT					###
###################################################

#				  OUTPUT ON STDOUT				  #

from collections import Counter as count
formattedResults = count([datum if datum else "Didn't Answer" for datum in dataToAnalyze])
total = len(dataToAnalyze)
print("\n".join([key+":\t"+str(formattedResults[key])+"\t"+str(formattedResults[key]*100.0/total)+"%" for key in sorted(formattedResults)]))


#				  PIE CHART OUTPUT				  #

def shortDescription(description):
	'''This just gets rid of extraneous information in question descriptions'''
	shorter = descriptions[columns[description]]
	shorter = shorter.replace(" (integer)","")
	shorter = shorter.replace(" (categorical)","")
	shorter = shorter.replace("1-2-3-4-5", "-")
	return shorter

from matplotlib import pyplot as plt
labels = tuple(sorted(formattedResults))
sizes = [formattedResults[label] for label in labels]
explode = [0 for i in range(0, len(labels))]

if args.explode:
	try:
		explode[labels.index(args.explode[0])] += 0.1
	except IndexError as e:
		print(args.explode+" isn't a valid answer to "+args.other_question+", or nobody gave this answer who also answered "+args.question+" with "+args.answer+'.', stderr)

fig1, ax1 = plt.subplots()
fig1.suptitle("Breakdown of Students' Answers to\n'"+shortDescription(args.other_question)+\
	"'\nwho also Answered\n'"+shortDescription(args.question)+\
	"'\nwith '"+args.answer+"'",\
	fontsize=20,\
	fontweight='bold')
patches, texts, autotexts = ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.2f%%', shadow=True, startangle=45)
for i in range(0,len(texts)):
	texts[i].set_fontsize(15)
	autotexts[i].set_fontsize(15)
ax1.axis('equal')
plt.show()
