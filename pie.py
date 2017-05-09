#!/usr/bin/env python3

import argparse as ap

#Argument Parsing
parser = ap.ArgumentParser(description='Compares student lives from a british survey via pie chart.', usage="%(prog)s [-l | -h | <question> <answer> <other question>]")
parser.add_argument('-l', '--list', action='store_true', help="Lists the available questions and the possible respective answer ranges")
parser.add_argument("question", default=None, type=str, nargs='?', help="The question to see related info for.")
parser.add_argument("answer", default=None, type=str, nargs='?', help="The answer to the question from <question>.")
parser.add_argument("other_question", default=None, type=str, nargs='?', help="A question to show a breakdown for, given that students also answered <question> with <answer>")

args = parser.parse_args()

if args.list:
	print("listing questions")