#!/usr/bin/env python3
""" Automated Graphing of Facebook Messaging Data """

import json
import sys
import pprint
from collections import namedtuple, OrderedDict
import os
import datetime
from dateutil.parser import parse
import pprint
import pickle as pkl

__author__ = "Rohan Pandit"
__copyright__ = "Copyright {0}".format(datetime.date.today().year)

pp = pprint.PrettyPrinter(indent=4)

Message = namedtuple("Message", ['person', 'year', 'month', 'day', 'hour'])

def main():
	os.chdir("Messages")

	#messages = loadMessages()
	#messages += loadHangouts()
	#pkl.dump(messages, open("../messages.pkl", 'wb'))
	messages = pkl.load(open("../messages.pkl", 'rb'))

	print("Total Messages: ", len(messages))

	graphTotalMessages(messages)


def loadMessages():
	decoded_jsons = []
	for _id in os.listdir():
		if _id[0] != '.' and _id[0] != '_' and _id[0] != 'H' and _id[0] != 'm': 
			try:
				encoded_jsons = open(_id + "/0-40000.json","r").read()
			except FileNotFoundError:
				try:
					encoded_jsons = open(_id + "/0-23000.json","r").read()	
				except FileNotFoundError:
					print("exception! ", _id)

			decoded_jsons += json.loads(encoded_jsons)["payload"]["actions"]


	print("Total FB Messages: ", len(decoded_jsons))
	messages = []

	for decoded_json in decoded_jsons:
		try:
			person = getPerson(decoded_json['other_user_fbid'])
		except KeyError:
			person = decoded_json['other_user_fbid']
		try:
			time = parse(decoded_json['timestamp_datetime'])
 			#TODO: Fix dates for last week 
		except ValueError:
			time = parseDate(decoded_json['timestamp_datetime'])
	
		messages.append(Message(person, int(str(time.year)[2:]), time.month, time.day, time.hour))

	return messages

def loadHangouts():
	messages = []
	decoded_json = json.loads(open("Hangouts.json").read())

	len_convo = lambda i: len(i['conversation_state']['event'])
	convos = sorted(decoded_json["conversation_state"], key=len_convo)

	for convo in convos:
		for msg in convo["conversation_state"]["event"]:
			try:
				person = getPerson(msg['sender_id']['chat_id'])
			except KeyError:
				person = msg['sender_id']['chat_id']

			time = datetime.datetime.fromtimestamp(int(msg['timestamp'])//1000000)

			messages.append(Message(person, int(str(time.year)[2:]), time.month, time.day, time.hour))

	print("Total Hangouts: ", len(messages))
	return messages


def graphTotalMessages(messages):
	record = {"6/23/15":0}
	date = "6/23/15"
	count = 0

	for msg in messages:
		msg_date = "{0}/{1}/{2}".format(msg.month, msg.day, msg.year)

		if date == msg_date:
			record[date] += 1
		else:
			old_date = date
			date = msg_date

			if date in record.keys():
				record[date] += 1
			else:
				record[date] = 1

	record = OrderedDict( sorted( record.items(), key=lambda t: int(parse(t[0]).strftime("%s")) ) )
	pp.pprint(record)

############### Utility Functions ################

def parseDate(timestamp):
	timestamp = timestamp.split(" ")
	if timestamp[0] == "Today":
		return datetime.date.today()


def getPerson(_id):
	return person[_id]

person = {
		100004255182066:'Ankit',
		100001629407080:'Alison',
		100000761719884:'Kevlin',
		100000403221435:'Pranay',
		100003238442927:'Vivek',
		100004081027353:'Rayana',
		100001128002655:'Michael You',
		100004468539961:'Srijith',
		100007730717911:'Philip Cho',
		100004496133045:'Matthew Kaufer',
		1702257415:'Andrew Huang',
		100006199622129:'Anusha',
		100005386399371:"Edward 'little shit' Shen",
		1795540795:'Sashank',
		100003272403235:'Tarun P.',
		100002452600456:'Joseph',
		100000756424022:'Jonathan',
		100003296135651:'Cheryl',
		100000471096235:'Josh Learn',
		100000830703634:'Kaushik V.',
		1497942558:'Avi',
		100004831269618:'Tarun K.',
		100003672744570:'Matthew S.',
		100004537931899:'Rachel',
		738046326264846:'Sheptiller',
		1396634270650233:'Puzzle Hunt',
		331888930354309:'Orgo',
		836256343110704:'Dags',
		943279359048126:'Dags',
		484394795045364:'Dags',
		1604705696418394:'Sheptiller',
		711430812206486:'Church of Acio',
		1417642561853941:'TJ Hunt',
		550377098381585:'Derp City',
		789573971100453:'Rachel',
		'UgxCAFWks7t61MHbACN4AaABAQ':'Dilip'
		}

if __name__ == "__main__": main()