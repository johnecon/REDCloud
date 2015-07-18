import os
import time
from selenium.webdriver.common.keys import Keys
from behave import *
from django.contrib.auth.models import User
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import UnexpectedAlertPresentException, TimeoutException
from docServer.admin import ProjectAdmin
from docServer.models.project import Project
from behave import register_type, given
from selenium.webdriver.support import expected_conditions as EC
import parse

@when('I toogle "{function}"')
def impl(context, function):
	if function == 'snapping':
		element_id = 'snap'
	elif function == 'grid':
		element_id = 'grid'
	context.browser.find_element_by_id("MenuOptions").click()
	context.browser.find_element_by_id(element_id).click()

@then('"{function}" should be "{status}"')
def impl(context, function, status):
	if status == "enabled":
		if function == 'snapping':
			assert context.browser.execute_script("""
			return myDiagram.toolManager.draggingTool.isGridSnapEnabled && myDiagram.toolManager.resizingTool.isGridSnapEnabled;
			""")
		elif function == 'grid':
			assert context.browser.execute_script("""
			return myDiagram.grid.visible;
			""")
	elif status == "disabled":
		if function == 'snapping':
			assert not context.browser.execute_script("""
			return myDiagram.toolManager.draggingTool.isGridSnapEnabled && myDiagram.toolManager.resizingTool.isGridSnapEnabled;
			""")
		elif function == 'grid':
			assert not context.browser.execute_script("""
			return myDiagram.grid.visible;
			""")
	

	            
