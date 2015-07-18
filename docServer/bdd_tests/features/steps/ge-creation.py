import os
import time

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

@when('I create "{node_title}" "{node_type}" node in "{username}" swimlane')
def impl(context, node_title, node_type, username):
	context.browser.execute_script("""
	var me = myDiagram.findNodeForKey('""" + username + """');
	var random = Math.random() * 100;
	var robot = new Robot(myDiagram);
	robot.mouseDown(me.location.x, me.location.y + random, 0, {right: true});
	robot.mouseUp(me.location.x, me.location.y + random, 100, {right: true});
	""")
	if node_type == "action":
		context.browser.find_element(By.LINK_TEXT, "Create Action").click()
		form = context.browser.find_element_by_id('editActionModal')
		form.find_element_by_id("action-name-input").send_keys(node_title)
	elif node_type == "object":
		context.browser.find_element(By.LINK_TEXT, "Create Artifact").click()
		form = context.browser.find_element_by_id('createObjectModal')
		form.find_element_by_id("new-object-name-input").send_keys(node_title)
	elif node_type == "comment":
		context.browser.find_element(By.LINK_TEXT, "Comment").click()
		form = context.browser.find_element_by_id('commentModal')
		form.find_element_by_id("comment-name-input").send_keys(node_title)
	form.submit()

@when('I create an object node for my partner')
def impl(context):
	context.browser.execute_script("""
	var partner = myDiagram.findNodeForKey('partner');
	var random = Math.random() * 100;
	var robot = new Robot(myDiagram);
	robot.mouseDown(partner.location.x, partner.location.y + random, 0, {right: true});
	robot.mouseUp(partner.location.x, partner.location.y + random, 100, {right: true});
	""")
	context.browser.find_element(By.LINK_TEXT, "Create Object").click()
	form = context.browser.find_element_by_id('createObjectModal')
	form.find_element_by_id("new-object-name-input").send_keys("Partner Object")
	file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "media/image2.jpeg")
	context.browser.find_element(By.NAME, "file").send_keys(file)
	wait = WebDriverWait(context.browser, 1)
	wait.until(lambda driver: form.find_element(By.CLASS_NAME, 'file-upload-success-message').is_displayed())
	form.submit()

@then('I should see "{node_name}" "{node_type}" node in "{swimlane}" swimlane')
def step_impl(context, node_name, node_type, swimlane):
	if node_type == "object":
		node_type = "Object"
	elif node_type == "action":
		node_type = "Action-In"
	elif node_type == "external action":
		node_type = "Action-Ex"
	elif node_type == "import action":
		node_type = "Action-Im"
	elif node_type == "comment":
		node_type = "Comment"
	assert context.browser.execute_script("""
		var found = false;
		var node_name = '""" + node_name + """';
		var node_type = '""" + node_type + """';
		var swimlane = '""" + swimlane + """';
		myDiagram.nodes.each(function(n) {
			if (n.part.data.name == node_name && n.part.data.category == node_type && n.part.data.group == swimlane) {
				found = true;
			}
		});
		return found;
	""")