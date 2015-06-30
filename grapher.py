#!/usr/bin/env python3
""" Automated Graphing of Facebook Messaging Data """

import json
import pprint
from collections import namedtuple, OrderedDict
import os
import datetime
from dateutil.parser import parse
import pickle as pkl
import numpy as np
import pandas as pd
import matplotlib.pyplot as pyplot
import matplotlib.dates as mdates
from matplotlib import cm

__author__ = "Rohan Pandit"
__copyright__ = "Copyright {0}".format(datetime.date.today().year)

pp = pprint.PrettyPrinter(indent=4)

Message = namedtuple("Message", ['person', 'timestamp', 'content'])

def main():
	os.chdir("Messages")

	"""
	messages = loadMessages()
	messages += loadHangouts()
	messages += loadHangouts('2')
	pkl.dump(messages, open("../messages.pkl", 'wb'))
	"""

	messages = pkl.load(open("../messages.pkl", 'rb'))
	print("Total Messages: ", len(messages), "\n")

	start_date = parse('7/26/14')
	end_date = parse('6/20/15')
	delta = (end_date - start_date).days
	
	people_msgs = {}

	for msg in messages:
		if msg.person in people_msgs.keys():
			if start_date < msg.timestamp < end_date:
				idx = (msg.timestamp - start_date).days
				people_msgs[msg.person][idx] += 1
		else:
			people_msgs[msg.person] = np.zeros(delta)

	people_msgs = OrderedDict( sorted(people_msgs.items(), key=lambda i: -sum(i[1])) )

	data = pd.DataFrame(people_msgs, index=pd.date_range(start_date, periods=delta))
	top10 = data.iloc[:,:15]
	print(top10.describe())
	mean = data.mean().sum()
	print("Mean: ", mean)	

	toPlot = cumMsgPlot(data, 10)
	
	ax = toPlot.plot(title="Cumulative Messaging Data (Top 10)")

	pyplot.show()
	plotTotalMessages(messages, start_date, end_date)

def cumMsgPlot(data, x):
	sum_data = data.apply(np.cumsum)
	return sum_data.iloc[:,:x]

def totalMsgsTopXPlot(data, x): #bar graph
	sum_data = data.iloc[:,:x].sum(axis=0)
	return sum_data

def numTalkedToPlot(data, min_messages=1, rolling=1):
	talkedTo = data[ min_messages > data ]
	talkedTo = pd.isnull(talkedTo)
	toPlot = talkedTo.iloc[:,:].sum(axis=1)
	return pd.rolling_mean(toPlot, rolling)

def topXPlot(data, x, rolling=1):
	others = data.iloc[:,:x].sum(axis=1)
	top = data.iloc[:,x:]
	top['Other'] = others
	return pd.rolling_mean(top, rolling)

def everyonePlot(data, rolling=1):
	sum_data = data.iloc[:,:].sum(axis=1)
	return pd.rolling_mean(sum_data, rolling)

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

		if str(decoded_json['other_user_fbid']) in people.keys():
			person = getPerson(decoded_json['other_user_fbid'])
		else:
			person = str(decoded_json['other_user_fbid'])
			if person == 'None':
				person = decoded_json['author'][5:]
				if str(person) in people.keys():
					person = getPerson(person)
		try:
			timestamp = parse(decoded_json['timestamp_datetime'])
 			#TODO: Fix dates for last week 
		except ValueError:
			timestamp = parseDate(decoded_json['timestamp_datetime'])
		try:
			content = decoded_json['body']
		except KeyError:
			content = ""

		if person == 'None':
			pp.pprint(decoded_json)
			quit()

		messages.append(Message(person, timestamp, content))

	return messages

def loadHangouts(a=''):
	messages = []
	decoded_json = json.loads(open("Hangouts%s.json"%a).read())

	len_convo = lambda i: len(i['conversation_state']['event'])
	convos = sorted(decoded_json["conversation_state"], key=len_convo)

	for convo in convos:
		for msg in convo["conversation_state"]["event"]:
			try:
				person = getPerson(msg['conversation_id']['id'])
			except KeyError:
				person = str(msg['conversation_id']['id'])

			timestamp = datetime.datetime.fromtimestamp(int(msg['timestamp'])//1000000)

			try:
				content = msg['chat_message']['message_content']['segment'][0]['text']
			except KeyError:
				content = ""

			if person == 'UgxG4T1spRtMbhsFK854AaABAQ':
				print(content)

			messages.append(Message(person, timestamp, content))

	print("Total Hangouts: ", len(messages))
	return messages


def plotTotalMessages(messages, start_date, end_date):
	start_date = parse(start_date)
	end_date = parse(end_date)
	print(start_date, end_date)

	record = {"":0}
	date = ""

	for msg in messages:
		msg_date = "{0}/{1}/{2}".format(msg.timestamp.month, msg.timestamp.day, msg.timestamp.year)

		if start_date < parse(msg_date) < end_date:

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

	dates = list(map(parse, list(record.keys())))
	numMessages = list(record.values())
	
	years = mdates.YearLocator()
	months = mdates.MonthLocator()
	yearsFormat = mdates.DateFormatter('%Y')

	fig, ax = pyplot.subplots()
	ax.plot(dates, numMessages)

	"""
	#format ticks
	ax.xaxis.set_major_locator(years)
	ax.xaxis.set_major_locator(yearsFormat)
	ax.xaxis.set_minor_locator(months)

	ax.set_xlim(min(dates), max(dates))

	ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
	ax.grid(True)
	fig.autofmt_xdate()
	"""

	pyplot.show()

	#pp.pprint(record)

############### Utility Functions ################

def parseDate(timestamp):
	timestamp = timestamp.split(" ")
	if timestamp[0] == "Today":
		return datetime.date.today()


def getPerson(_id):
	return people[str(_id)]

people = {
		#fill this out yourself :)
		}

if __name__ == "__main__": main()
