#!/usr/bin/env python3

import argparse as ap

#Argument Parsing
parser = ap.ArgumentParser(description='Compares student lives from a british survey via pie chart.', usage="%(prog)s [-l | -h | <question> <answer> <other question>]", epilog="Each entry output using `-l` or `--list` ends with 'keyword=\"<keyword>\"', which specifies the keyword to use when this entry is the <question> or <other_question> argument. <answer> arguments should be given exactly; use quotes to enclose strings that contain spaces. Same thing applies to the way-too-many keywords that have spaces in them due to poor life choices by the data maintainers.")
parser.add_argument('-l', '--list', action='store_true', help="Lists the available questions and the possible respective answer ranges, and exit.")
parser.add_argument("question", default=None, type=str, nargs='?', help="The question to see related info for.")
parser.add_argument("answer", default=None, type=str, nargs='?', help="The answer to the question from <question>.")
parser.add_argument("other_question", default=None, type=str, nargs='?', help="A question to show a breakdown for, given that students also answered <question> with <answer>")

args = parser.parse_args()

if args.list:
	descriptions = open("qdescripts").read().strip().split("\n")
	colnames = [line.split("\",\"")[1] for line in open("columns.csv").read().strip().split("\n")]
	output = [descriptions[i]+", keyword=\""+colnames[i] for i in range(0,len(descriptions))]
	print('\n'.join(output))
	exit()
