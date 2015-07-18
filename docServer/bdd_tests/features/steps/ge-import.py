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

@when('I import "{node_title}" object node as "{new_node_title}" in "{user}" swimlane')
def impl(context, node_title, new_node_title, user):
    context.browser.execute_script("""
        function getSwimlane(user) {
            var node;
            var it = myDiagram.nodes;
            while (it.next()) {
                if (it.key.part.data.key == user) {
                    node = it.key;
                    break;
                }

            }
            return node;
        }
        var node = getSwimlane('""" + user + """');
        var robot = new Robot(myDiagram);
        robot.mouseDown(node.location.x, node.location.y + 50, 0);
        robot.mouseUp(node.location.x, node.location.y + 50, 100);
        robot.mouseDown(node.location.x, node.location.y, 200);
        robot.mouseUp(node.location.x, node.location.y, 300);
        robot.mouseDown(node.location.x, node.location.y, 400, {right: true});
        robot.mouseUp(node.location.x, node.location.y, 500, {right: true});
    """)
    context.browser.find_element(By.LINK_TEXT, "Import Artifact").click()
    form = context.browser.find_element_by_id('importObjectModal')
    name_input = form.find_element_by_id("import-object-name-input")
    name_input.send_keys(new_node_title)
    object_input = form.find_element_by_id("select-object-import")
    object_input.send_keys(node_title)
    form.submit()


@when('I import "{project}" template from "{user}" swimlane')
def impl(context, project, user):
    context.browser.execute_script("""
        function getSwimlane(user) {
            var node;
            var it = myDiagram.nodes;
            while (it.next()) {
                if (it.key.part.data.key == user) {
                    node = it.key;
                    break;
                }

            }
            return node;
        }
        var node = getSwimlane('""" + user + """');
        var robot = new Robot(myDiagram);
        robot.mouseDown(node.location.x, node.location.y + 50, 0);
        robot.mouseUp(node.location.x, node.location.y + 50, 100);
        robot.mouseDown(node.location.x, node.location.y, 200);
        robot.mouseUp(node.location.x, node.location.y, 300);
        robot.mouseDown(node.location.x, node.location.y, 400, {right: true});
        robot.mouseUp(node.location.x, node.location.y, 500, {right: true});
    """)
    context.browser.find_element(By.LINK_TEXT, "Import Template").click()
    form = context.browser.find_element_by_id('importTemplateModal')
    template_input = form.find_element_by_id("import-template")
    template_input.send_keys(project)
    form.submit()
