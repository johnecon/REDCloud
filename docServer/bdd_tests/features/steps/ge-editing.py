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

@when('I change the color of "{swimlane}" swimlane to "{color}"')
def impl(context, swimlane, color):
    context.browser.execute_script("""
        function getSwimlane(name) {
            var node;
            var it = myDiagram.nodes;
            while (it.next()) {
                if (it.key.part.data.key == name) {
                    node = it.key;
                    break;
                }

            }
            return node;
        }
        var node = getSwimlane('""" + swimlane + """');
        var robot = new Robot(myDiagram);
        robot.mouseDown(node.location.x, node.location.y + 50, 0);
        robot.mouseUp(node.location.x, node.location.y + 50, 100);
        robot.mouseDown(node.location.x, node.location.y, 200);
        robot.mouseUp(node.location.x, node.location.y, 300);
        robot.mouseDown(node.location.x, node.location.y, 400, {right: true});
        robot.mouseUp(node.location.x, node.location.y, 500, {right: true});
    """)
    context.browser.find_element(By.LINK_TEXT, "Edit").click()
    form = context.browser.find_element_by_id('editSwimLaneModal')
    color_picker = form.find_element_by_id("color_picker")
    color_picker.send_keys(Keys.BACKSPACE*10)
    color_picker.send_keys(color)
    form.submit()


@then('The color of "{swimlane}" should be "{color}"')
def impl(context, swimlane, color):
    context.browser.execute_script("""
        function getSwimlane(name) {
            var node;
            var it = myDiagram.nodes;
            while (it.next()) {
                if (it.key.part.data.key == name) {
                    node = it.key;
                    break;
                }

            }
            return node;
        }
        var node = getSwimlane('""" + swimlane + """');
        var robot = new Robot(myDiagram);
        robot.mouseDown(node.location.x, node.location.y + 50, 0);
        robot.mouseUp(node.location.x, node.location.y + 50, 100);
        robot.mouseDown(node.location.x, node.location.y, 200);
        robot.mouseUp(node.location.x, node.location.y, 300);
        robot.mouseDown(node.location.x, node.location.y, 400, {right: true});
        robot.mouseUp(node.location.x, node.location.y, 500, {right: true});
    """)
    context.browser.find_element(By.LINK_TEXT, "Edit").click()
    form = context.browser.find_element_by_id('editSwimLaneModal')
    assert form.find_element_by_id("color_picker").get_attribute('value') == color
    form.submit()

@then('I should not be able to edit "{node_title}" "{node_type}" node in "{username}" swimlane')
def impl(context, node_title, node_type, username):
    context.browser.execute_script("""
        function getNode(name) {
            var node;
            var it = myDiagram.nodes;
            while (it.next()) {
                if (it.key.part.data.name == name) {
                    node = it.key;
                    break;
                }

            }
            return node;
        }
        var node = getNode('""" + node_title + """');
        var robot = new Robot(myDiagram);
        robot.mouseDown(node.location.x, node.location.y + 50, 0);
        robot.mouseUp(node.location.x, node.location.y + 50, 100);
        robot.mouseDown(node.location.x, node.location.y, 200);
        robot.mouseUp(node.location.x, node.location.y, 300);
        robot.mouseDown(node.location.x, node.location.y, 400, {right: true});
        robot.mouseUp(node.location.x, node.location.y, 500, {right: true});
    """)
    context.browser.find_element(By.LINK_TEXT, "Edit").click()
    form = context.browser.find_element_by_id('editObjectModal') if node_type == "object" else context.browser.find_element_by_id('editActionModal')
    name_input = form.find_element_by_id("edit-object-name-input") if node_type == "object" else form.find_element_by_id("action-name-input")
    assert name_input.get_attribute('disabled')
    form.submit()


@when('I change "{node_title}" "{node_type}" node in "{username}" swimlane name to "{new_node_title}"')
def impl(context, node_title, node_type, username, new_node_title):
    context.browser.execute_script("""
        function getNode(name) {
            var node;
            var it = myDiagram.nodes;
            while (it.next()) {
                if (it.key.part.data.name == name) {
                    node = it.key;
                    break;
                }

            }
            return node;
        }
        var node = getNode('""" + node_title + """');
        var robot = new Robot(myDiagram);
        robot.mouseDown(node.location.x, node.location.y + 50, 0);
        robot.mouseUp(node.location.x, node.location.y + 50, 100);
        robot.mouseDown(node.location.x, node.location.y, 200);
        robot.mouseUp(node.location.x, node.location.y, 300);
        robot.mouseDown(node.location.x, node.location.y, 400, {right: true});
        robot.mouseUp(node.location.x, node.location.y, 500, {right: true});
    """)
    context.browser.find_element(By.LINK_TEXT, "Edit").click()
    if node_type == "object":
        form = context.browser.find_element_by_id('editObjectModal')
        name_input = form.find_element_by_id("edit-object-name-input")
    elif node_type == "action":
        form = context.browser.find_element_by_id('editActionModal')
        name_input = form.find_element_by_id("action-name-input")
    elif node_type == "comment":
        form = context.browser.find_element_by_id('editCommentModal')
        name_input = form.find_element_by_id("edit-comment-name-input")
    name_input.send_keys(Keys.BACKSPACE*20)
    name_input.send_keys(Keys.DELETE*20)
    name_input.send_keys(new_node_title)
    form.submit()
