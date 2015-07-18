from behave import *
from selenium.webdriver.common.by import By

@when('I syncronize "{node_one}" with "{node_two}"')
def impl(context, node_one, node_two):
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
        var node_one = getNode('""" + node_one + """');
        var node_two = getNode('""" + node_two + """');
        var robot = new Robot(myDiagram);
        myDiagram.nodes.each(function(n) {
            n.isSelected = false;
        });
        node_one.isSelected = true;
        node_two.isSelected = true;
        robot.mouseDown(node_one.location.x, node_one.location.y, 200, {right: true});
        robot.mouseUp(node_one.location.x, node_one.location.y, 300, {right: true});
    """)
    context.browser.find_element(By.LINK_TEXT, "Synchronize").click()
    form = context.browser.find_element_by_class_name('btn-primary').click()