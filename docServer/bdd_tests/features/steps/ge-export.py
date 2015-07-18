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

@when('I export "{node_title}" object node to "{package_name}"')
def impl(context, node_title, package_name):
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
        myDiagram.nodes.each(function(n) {
            n.isSelected = false;
        });
        node.isSelected = true;
        robot.mouseDown(node.location.x, node.location.y, 400, {right: true});
        robot.mouseUp(node.location.x, node.location.y, 500, {right: true});
    """)
    context.browser.find_element(By.LINK_TEXT, "Export").click()
    form = context.browser.find_element_by_id('exportObjectsModal')
    name_input = form.find_element_by_id("export-objects-name-input")
    name_input.send_keys(Keys.BACKSPACE*20)
    name_input.send_keys(Keys.DELETE*20)
    name_input.send_keys(package_name)
    form.submit()

@when('I export "{node_title}" and "{node_title_two}" object nodes to "{package_name}"')
def impl(context, node_title, node_title_two, package_name):
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
        var secondNode = getNode('""" + node_title_two + """');
        myDiagram.nodes.each(function(n) {
            n.isSelected = false;
        });
        node.isSelected = true;
        secondNode.isSelected = true;
        var robot = new Robot(myDiagram);
        robot.mouseDown(node.location.x, node.location.y, 200, {right: true});
        robot.mouseUp(node.location.x, node.location.y, 300, {right: true});
    """)
    # wait = WebDriverWait(context.browser, 20)
    # wait.until(lambda driver: False)
    context.browser.find_element(By.LINK_TEXT, "Export").click()
    form = context.browser.find_element_by_id('exportObjectsModal')
    name_input = form.find_element_by_id("export-objects-name-input")
    name_input.send_keys(Keys.BACKSPACE*20)
    name_input.send_keys(Keys.DELETE*20)
    name_input.send_keys(package_name)
    form.submit()