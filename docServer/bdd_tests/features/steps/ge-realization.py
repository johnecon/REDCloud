import os
import time

from behave import *
from selenium.webdriver.common.keys import Keys
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

@when('I realize "{node_title}" "{node_type}" node')
def impl(context, node_title, node_type):
    node_type_id = "Object" if node_type == "object" else "Action"
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
        robot.mouseDown(node.location.x, node.location.y, 100, {right: true});
        robot.mouseUp(node.location.x, node.location.y, 200, {right: true});
    """)
    context.browser.find_element(By.LINK_TEXT, "Realize").click()
    form = context.browser.find_element_by_id('realize' + node_type_id + 'Modal')
    name_input = form.find_element_by_id("realize-" + node_type + "-name-input")
    name_input.send_keys(Keys.BACKSPACE*20)
    name_input.send_keys(Keys.DELETE*20)
    name_input.send_keys("Realized " + node_title)
    form.find_element_by_id("realize-" + node_type + "-description-input").send_keys("Realize Object Description")
    form.submit()


@when('I submit the prompted "{node_type}" realization form')
def impl(context, node_type):
    node_type_id = "Object" if node_type == "object" else "Action"
    wait = WebDriverWait(context.browser, 1)
    wait.until(lambda driver: driver.find_element_by_id('realize' + node_type_id + 'Modal').is_displayed())
    assert True
    form = context.browser.find_element_by_id('realize' + node_type_id + 'Modal')
    form.submit()