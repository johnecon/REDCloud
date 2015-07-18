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

@when('I archive "{node_title}" "{node_type}" node')
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
        robot.mouseDown(node.location.x, node.location.y + 50, 0);
        robot.mouseUp(node.location.x, node.location.y + 50, 100);
        robot.mouseDown(node.location.x, node.location.y, 200);
        robot.mouseUp(node.location.x, node.location.y, 300);
        robot.mouseDown(node.location.x, node.location.y, 400, {right: true});
        robot.mouseUp(node.location.x, node.location.y, 500, {right: true});
    """)
    context.browser.find_element(By.LINK_TEXT, "Archive").click()
    context.browser.find_element(By.CLASS_NAME, "btn-primary").click()
