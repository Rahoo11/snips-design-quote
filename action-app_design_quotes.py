#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from snipsTools import SnipsConfigParser
from hermes_python.hermes import Hermes
from hermes_python.ontology import *
import io
import requests
import re

CONFIG_INI = "config.ini"
MQTT_IP_ADDR = "localhost"
MQTT_PORT = 1883
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT))

class DesignQuote(object):
    def __init__(self):
        # Get the configuration if needed
        try:
            self.config = SnipsConfigParser.read_configuration_file(CONFIG_INI)
        except :
            self.config = None

        # Start listening to MQTT
        self.start_blocking()

    # Helper function to remove all HTML from the return string
    # https://stackoverflow.com/questions/9662346/python-code-to-remove-html-tags-from-a-string
    def cleanHtml(self, raw_html):
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        return cleantext
        
    # Main method. Fetches the quote and returns it to be spoken.
    def getQuote_callback(self, hermes, intent_message):
        # terminate the session first if not continue
        hermes.publish_end_session(intent_message.session_id, "")
        
        print '[Received] intent: {}'.format(intent_message.intent.intent_name)
        
        # get a random design quote
        design_quote = requests.get("https://quotesondesign.com/wp-json/posts?filter[orderby]=rand&filter[posts_per_page]=1").json()[0]["content"]
        sanitized_design_quote = self.cleanHtml(design_quote)

        # Read out the quote that was returned
        hermes.publish_start_session_notification(intent_message.site_id, sanitized_design_quote, "design_quote_app")

    # Intent passthrough function.
    # TODO: Extend this to allow for more filtering functions
    def master_intent_wrapper(self, hermes, intent_message):
        self.getQuote_callback(hermes, intent_message)

    # --> Register callback function and start MQTT
    def start_blocking(self):
        with Hermes(MQTT_ADDR) as h:
            h.subscribe_intents(self.master_intent_wrapper).start()

if __name__ == "__main__":
    DesignQuote()
