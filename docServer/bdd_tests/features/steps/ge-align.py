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

@when('I "{action}" nodes')
def impl(context, action):
    context.browser.execute_script("""
        myDiagram.nodes.each(function(n) {
            n.isSelected = false
        });
    """)
    for row in context.table:
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
            var node = getNode('""" + row['name'] + """');
            node.isSelected = true;
        """)
    context.browser.find_element_by_id(action).click()

@then('nodes below should be "{action}"')
def impl(context, action):
    context.browser.execute_script("""
        myDiagram.nodes.each(function(n) {
            n.isSelected = false
        });
    """)
    for row in context.table:
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
            var node = getNode('""" + row['name'] + """');
            node.isSelected = true;
        """)
    if action=="top-alligned" or action=="bottom alligned":
        assert context.browser.execute_script("""
                var aligned = true;
                var y = myDiagram.selection.first().position.y;
                myDiagram.selection.each( function(n) {
                    if (n.position.y != y) {
                        aligned = false;
                    }
                    y = n.position.y;
                });
                return aligned;
            """)
    elif action=="left alligned":
        assert context.browser.execute_script("""
                var aligned = true;
                var x = myDiagram.selection.first().position.x;
                myDiagram.selection.each( function(n) {
                    if (n.position.x != x) {
                        aligned = false;
                    }
                    x = n.position.x;
                });
                return aligned;
            """)
    elif action=="right alligned":
        assert context.browser.execute_script("""
                var aligned = true;
                var x = myDiagram.selection.first().position.x + myDiagram.selection.first().actualBounds.width;
                myDiagram.selection.each( function(n) {
                    if (n.position.x + n.actualBounds.width != x) {
                        aligned = false;
                    }
                    x = n.position.x + n.actualBounds.width;
                });
                return aligned;
            """)
    elif action=="center-x alligned":
        assert context.browser.execute_script("""
                var aligned = true;
                var x = myDiagram.selection.first().position.x + myDiagram.selection.first().actualBounds.width / 2;
                myDiagram.selection.each( function(n) {
                    if (n.position.x + n.actualBounds.width / 2 != x) {
                        aligned = false;
                    }
                    x = n.position.x + n.actualBounds.width / 2;
                });
                return aligned;
            """)
    elif action=="center-y alligned":
        assert context.browser.execute_script("""
                var aligned = true;
                var y = myDiagram.selection.first().position.y + myDiagram.selection.first().actualBounds.height / 2;
                myDiagram.selection.each( function(n) {
                    if (n.position.y + n.actualBounds.height / 2 != y) {
                        aligned = false;
                    }
                    y = n.position.y + n.actualBounds.height / 2;
                });
                return aligned;
            """)
    elif action=="vertically distributed":
        assert context.browser.execute_script("""
                var verticallyDistributed = true;
                var selectedOrderedNodes = _.chain(myDiagram.selection.toArray()).
                    filter(function(n){ return n.category != "SwimLane" && n.category != ""; }).
                    sortBy(function(n) { return n.location.y; }).
                    value();
                if (selectedOrderedNodes.length > 2) {
                    var yIncrement = Math.abs(selectedOrderedNodes[0].location.y - selectedOrderedNodes[1].location.y);
                    for (i=0;i<selectedOrderedNodes.length;i++) {
                        if (i > 0) {
                            if (Math.abs(selectedOrderedNodes[i].location.y - selectedOrderedNodes[i-1].location.y) > yIncrement) {
                                verticallyDistributed = false;
                            }
                            yIncrement += yIncrement;
                        }
                    }
                }
                return verticallyDistributed;
            """)