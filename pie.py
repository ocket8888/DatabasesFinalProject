#!/usr/bin/env python3


###################################################
###				ARGUMENT PARSING				###
###################################################
import argparse as ap

#Just describes the program and how to use it.
parser = ap.ArgumentParser(\
	description="Compares student lives from a british survey via pie chart. Also outputs line-separated numerical data to stdout in the format:"
		"<answer>\\t<number of this answer>\\t<percent of total constituted by this answer>%"
		"where '\\t' indicates a tab character.",\
	usage="%(prog)s [-l | -h | -s <question> | -c <question> <answer> <other question>] [-x]",\
	epilog="Each entry output using `-l` or `--list` ends with 'keyword=\"<keyword>\"', which specifies the keyword to use when this entry is the"
		"<question> or <other question> argument. <answer> arguments should be given exactly; use quotes to enclose strings that contain spaces."
		"Same thing applies to the way-too-many keywords that have spaces in them due to poor life choices by the data maintainers."
		"Exit codes:"
			"0 indicates normal exit,"
			"1 indicates manual command-line argument validation failed, and a message will be printed saying why,"
			"2 is reserved for errors encountered by the `argparse.ArgumentParser.parse_args()` function, so errors should be verbose,"
			"3 indicates that a library is missing, and will display a message advising which library is missing and possible ways to install it,"
			"4 means that the directory is missing something (probably `list.psql`),"
			"5 is used for any and all database connection-related errors")

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


from sys import stderr
try:
	from psycopg2 import connect
except ImportError as e:
	print("You don't appear to have psycopg2 installed. Try `sudo apt install python3-psycopg2` or `sudo -H pip3 install psycopg2` and then run this program again.", file=stderr)
	exit(3)

#list all the questions from the survey along with their descriptions and column names
#could probably be one hideous, nested list comprehension, but this is hard enough to read as it is
#and any halfway decent python compiler will make that optimization for us.
if args.list:
	output = list()
	try:
		#open some resources
		listSQL = open("list.psql")
		#pls no hack
		connection = connect(host="mprussak.bounceme.net",\
                  dbname="final_project",\
                  user="brennan",\
                  password="403_password_brennan")
		db = connection.cursor()

		#get the output
		db.execute(listSQL.read().strip())
		output = [entry[0] for entry in db.fetchall()]

	except Exception as e:
		code=5
		if type(e) is FileNotFoundError:
			print("Your directory appears corrupted; try downloading again.", file=stderr)
			code=4
		else:
			print("Something wicked happened when trying to read from the database", file=stderr)
		print(e, file=stderr)
		exit(code)

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
def shortDescription(description):
	'''This just gets rid of extraneous information in question descriptions'''
	shorter = description.replace(" (integer)","")
	shorter = shorter.replace(" (categorical)","")
	shorter = shorter.replace("1-2-3-4-5", "-")
	return shorter


try:
	#open resources
	#pls no hack
	connection = connect(host="mprussak.bounceme.net",\
              dbname="final_project",\
              user="brennan",\
              password="403_password_brennan")
	db = connection.cursor()

	#Execute query on a single question
	if args.single:
		#description
		db.execute(
			"""SELECT description FROM columns WHERE name=%s;"""
			(args.single[0],))
		desc = "Breakdown of Students' Answers to\n'"+shortDescription(db.fetchone()[0])+"'"

		#results
		db.execute("SELECT %s FROM results;" % args.single[0])

	#Execute query on a comparison of questions
	elif args.compare:
		print(args.compare)
		#description
		db.execute(
			"""SELECT a.description AS q1, b.description AS q2
				FROM columns AS a
				INNER JOIN
					(SELECT description FROM columns WHERE name=%s) AS b
				ON a.name=%s;""",
			(args.compare[2], args.compare[0]))
		descriptions = db.fetchone()
		desc = "Breakdown of Students' Answers to\n'"+shortDescription(descriptions[1])+\
		"'\nwho also Answered\n'"+shortDescription(descriptions[0])+\
		"'\nwith '"+args.compare[1]+"'"

		#results
		query = "SELECT %s FROM results WHERE %s" % (args.compare[2], args.compare[0])
		db.execute(query+"=%s;", (args.compare[1]))

	#fetch and format results
	fetchedData = db.fetchall()
	dataToAnalyze = [result[0] if result[0] else "Didn't Answer" for result in fetchedData]
	print(dataToAnalyze)

except Exception as e:
	print("Something wicked happened when trying to read from the database", file=stderr)
	print(e, file=stderr)
	exit(5)
finally:
	db.close()
	connection.close()


###################################################
### 				DATA OUTPUT					###
###################################################

#				  OUTPUT ON STDOUT				  #

from collections import Counter as count
formattedResults = count(dataToAnalyze)
total = len(dataToAnalyze)
print("\n".join([key+"\t"+str(formattedResults[key])+"\t"+str(formattedResults[key]*100.0/total)+"%" for key in sorted(formattedResults)]))


#				  PIE CHART OUTPUT				  #

try:
	from matplotlib import pyplot as plt
except ImportError as e:
	print("You don't appear to have matplotlib installed. Try `sudo apt install python3-matplotlib` or `sudo -H pip3 install matplotlib` and then run this program again.", file=stderr)
	exit(3)

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
fig1.suptitle(desc, fontsize=(24 if args.single else 20), fontweight='bold')

#This sets up the plot, and returns `<?>, <text based on data>, <text generated automatically>`
patches, texts, autotexts = ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.2f%%', shadow=True, startangle=45)

#all the pie chart text is way too tiny by default
for i in range(0,len(texts)):
	texts[i].set_fontsize(15)
	autotexts[i].set_fontsize(15)

#These last two lines set the aspect ratio (to 'equal' which guarantees that the pie chart is a circle) and shows the plot window, respectively.
ax1.axis('equal')
plt.show()
