# coding=utf-8

import logging
from datetime import datetime
from flask import Flask, json, render_template
from flask_ask import Ask, request, session, question, statement
<<IMPORTS>>

__author__ = 'Jordan Pizza'
__email__ = 'sales@speakeasier.com'

app = Flask(__name__)
ask = Ask(app, '/')
logging.getLogger("flask_ask").setLevel(logging.DEBUG)

# Session starter
#
# This intent is fired automatically at the point of launch (= when the session starts).
# Use it to register a state machine for things you want to keep track of, such as what the last intent was, so as to be
# able to give contextual help.

@ask.on_session_started
def start_session():
	"""
	Fired at the start of the session, this is a great place to initialise state variables and the like.
	"""
	logging.debug("Session started at {}".format(datetime.now().isoformat()))

# Launch intent
#
# This intent is fired automatically at the point of launch.
# Use it as a way to introduce your Skill and say hello to the user. If you envisage your Skill to work using the
# one-shot paradigm (i.e. the invocation statement contains all the parameters that are required for returning the
# result

@ask.launch
def handle_launch():
	"""
	(QUESTION) Responds to the launch of the Skill with a welcome statement and a card.

	Templates:
	* Initial statement: 'welcome'
	* Reprompt statement: 'welcome_re'
	* Card title: 'My Flask-Ask skill
	* Card body: 'welcome_card'
	"""

	welcome_text = render_template('welcome')
	welcome_re_text = render_template('welcome_re')
	welcome_card_text = render_template('welcome_card')

	return question(welcome_text).reprompt(welcome_re_text).standard_card(title="My Flask-Ask skill",
																		  text=welcome_card_text)


# Built-in intents
#
# These intents are built-in intents. Conveniently, built-in intents do not need you to define utterances, so you can
# use them straight out of the box. Depending on whether you wish to implement these in your application, you may keep
# or delete them/comment them out.
#
# More about built-in intents: http://d.pr/KKyx

@ask.intent('AMAZON.StopIntent')
def handle_stop():
	"""
	(STATEMENT) Handles the 'stop' built-in intention.
	"""
	farewell_text = render_template('stop_bye')
	return statement(farewell_text)


@ask.intent('AMAZON.CancelIntent')
def handle_cancel():
	"""
	(STATEMENT) Handles the 'cancel' built-in intention.
	"""
	farewell_text = render_template('cancel_bye')
	return statement(farewell_text)


@ask.intent('AMAZON.HelpIntent')
def handle_help():
	"""
	(QUESTION) Handles the 'help' built-in intention.

	You can provide context-specific help here by rendering templates conditional on the help referrer.
	"""

	help_text = render_template('help_text')
	return question(help_text)


@ask.intent('AMAZON.NoIntent')
def handle_no():
	"""
	(?) Handles the 'no' built-in intention.
	"""
	pass

@ask.intent('AMAZON.YesIntent')
def handle_yes():
	"""
	(?) Handles the 'yes'  built-in intention.
	"""
	pass


@ask.intent('AMAZON.PreviousIntent')
def handle_back():
	"""
	(?) Handles the 'go back!'  built-in intention.
	"""
	pass

@ask.intent('AMAZON.StartOverIntent')
def start_over():
	"""
	(QUESTION) Handles the 'start over!'  built-in intention.
	"""
	pass


# Ending session
#
# This intention ends the session.

@ask.session_ended
def session_ended():
	"""
	Returns an empty for `session_ended`.

	.. warning::

	The status of this is somewhat controversial. The `official documentation`_ states that you cannot return a response
	to ``SessionEndedRequest``. However, if it only returns a ``200/OK``, the quit utterance (which is a default test
	utterance!) will return an error and the skill will not validate.

	"""
	return statement("")

def lambda_handler(event, _context):
	event_type = event['request']['type']

	global logger
	logger = logging.getLogger("flask_ask")

	# Gets our API Endpoint and the API Access Token so we can get location
	global apiAccessToken
	global apiEndpoint
	try:
		apiAccessToken = event['context']['System']['apiAccessToken']
		apiEndpoint = event['context']['System']['apiEndpoint']
	except KeyError:
		# We need their permission to access their information
		print("Problem with Device Authorization")
		return requestUserInfo()

	logger.info(json.dumps(event))
	if event_type == "IntentRequest":
		intent_name = event['request']['intent']['name']

		global route

		if not "attributes" in event['session']:
			route = None
			event['session']['attributes'] = {}
			logger.info("No Route")
		else:
			if "route" in event['session']['attributes']:
				route = event['session']['attributes']["route"]
				logger.info("User Requested Route: %s" % (route))
			else:
				route = None


		dontRoute = ["AMAZON.StopIntent", "AMAZON.CancelIntent"]
		if not intent_name in dontRoute:
			dialog_state = ask.session.dialogState
			if dialog_state != "COMPLETED":
				delegate()

			if "originalIntentName" in event['session']['attributes']:
				del event['session']['attributes']['originalIntentName']

			<<ROUTING>>

			if intent_name == "AMAZON.FallbackIntent" and route == None:
				return question("Sorry, I didn't understand that. Would you like to learn about revenue marketing, Hear the latest blog, or contact TPG directly?")

			event['session']['attributes']['originalIntentName'] = intent_name

		logger.info("Routing to %s" % event['request']['intent']['name'])


	
	return ask.run_aws_lambda(event)