#!/usr/bin/env python3
""" Automated Graphing of Facebook Messaging Data """

import json
import sys
import pprint
from collections import namedtuple
import os
import datetime
import pprint

__author__ = "Rohan Pandit"
__copyright__ = "Copyright {0}".format(datetime.date.today().year)

pp = pprint.PrettyPrinter(indent=4)

def main():
	os.chdir("Messages")

	messages = loadMessages()
	graphTotalMessages(messages)


def loadMessages():
	decoded_jsons = []
	for _id in os.listdir():
		encoded_jsons = open(_id + "/complete.json","r").read()
		decoded_jsons += json.loads(encoded_jsons)

	Message = namedtuple("Message", ['person', 'day', 'time'])
	messages = []

	for decoded_json in decoded_jsons:
		person = getPerson(decoded_json['other_user_fbid'])
		day = getDay(decoded_json['timestamp_absolute'])
		time = getTime(decoded_json['timestamp_datetime'])

		messages.append(Message(person, day, time))

	return messages

def graphTotalMessages(messages):
	record = {"Tuesday":0}
	date = "Tuesday"

	for msg in messages:
		if date == msg.day:
			record[date] += 1
		else:
			date = msg.day
			record[date] = 1

	pp.pprint(record)


############### Utility Functions ################

def getDay(timestamp):
	return timestamp

def getTime(timestamp):
	return timestamp

def getPerson(_id):
	return person[_id]

person = {
		100004255182066:'Ankit',
		100001629407080:'Alison',
		100000761719884:'Kevlin',
		1087116501:'Nick M.'
		}

if __name__ == "__main__": main()