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

@parse.with_pattern(r"\d+")
def parse_number(text):
    return int(text)

register_type(Number=parse_number)

def wait_for(condition_function):
    start_time = time.time()
    while time.time() < start_time + 3:
        if condition_function():
            return True
        else:
            time.sleep(0.1)
            raise Exception(
                'Timeout waiting for {}'.format(condition_function.__name__)
            )


def wait_for_page_load(browser):
    old_page = browser.find_element_by_tag_name('html')

    yield

    def page_has_loaded():
        new_page = browser.find_element_by_tag_name('html')
        return new_page.id != old_page.id

    wait_for(page_has_loaded)


@given('a set of specific users')
def step_impl(context):
    for row in context.table:
        context.execute_steps('''
            given a user "''' + row['username'] + '''", "''' + row['first_name'] + '''", "''' + row['password'] + '''", "''' + row['email'] + '''""
        ''')


@then('I should see "{message_text}"')
def step_impl(context, message_text):
    assert context.browser.find_elements_by_xpath("//*[contains(text(), '" + message_text + "')]")


@given('a user "{username}", "{first_name}", "{password}", "{email}"')
def step_impl(context, username, first_name, password, email):
    u = User(username=username, first_name=first_name, email=email)
    u.set_password(password)
    u.save()

@given('a project "{project_name}" created by "{username}"')
def step_impl(context, project_name, username):
    u = User.objects.get(username=username)
    p = Project(name=project_name, created_by=u)
    p.save()



@given('"{username}" contributes to "{project_name}"')
def step_impl(context, username, project_name):
    p = Project.objects.get(name=project_name)
    u = User.objects.get(username=username)
    u.projects_contributed.add(p)
    u.save()

@given('"{username}" exports "{project_name}"`s graph')
def step_impl(context, username, project_name):
    p = Project.objects.get(name=project_name)
    u = User.objects.get(username=username)
    ProjectAdmin.export_graph(project=p, created_by_user=u)

@given('"{username}" sets "{project_name}"`s graph as a template')
def step_impl(context, username, project_name):
    p = Project.objects.get(name=project_name)
    u = User.objects.get(username=username)
    graph = p.graphs.first()
    graph.is_template = True
    graph.save()

@when('I navigate to the graph editor of "{project}"')
def step_impl(context, project):
    context.browser.get(context.server_url + "/projects")
    p = Project.objects.get(name=project)
    # with wait_for_page_load(context.browser):
    context.browser.find_element(By.LINK_TEXT, p.name).click()
    wait_for_page_load(context.browser)


@when('I navigate to my projects')
def step_impl(context):
    context.browser.get(context.server_url + "/projects")


@when('I insert me')
def step_impl(context):
    context.browser.execute_script("myDiagram.commandHandler.showContextMenu()")
    context.browser.find_element(By.LINK_TEXT, "Add User").click()
    form = context.browser.find_element_by_id('addUserModal')
    select = Select(form.find_element_by_tag_name("select"))
    select.select_by_visible_text("my_username")
    form.submit()


@when('I insert my partner')
def step_impl(context):
    context.browser.execute_script("myDiagram.commandHandler.showContextMenu()")
    context.browser.find_element(By.LINK_TEXT, "Add User").click()
    form = context.browser.find_element_by_id('addUserModal')
    select = Select(form.find_element_by_tag_name("select"))
    select.select_by_visible_text("partner")
    form.submit()


@when('I merge these two object nodes')
def impl(context):
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
        var myObjectNode = getNode('My Object');
        var partnerObjectNode = getNode('Partner Object');
        var robot = new Robot(myDiagram);
        robot.mouseDown(myObjectNode.location.x, myObjectNode.location.y, 0);
        robot.mouseUp(myObjectNode.location.x, myObjectNode.location.y, 100);
        partnerObjectNode.isSelected = true;
        robot.mouseDown(myObjectNode.location.x, myObjectNode.location.y, 200, {right: true});
        robot.mouseUp(myObjectNode.location.x, myObjectNode.location.y, 300, {right: true});
    """)
    context.browser.find_element(By.LINK_TEXT, "Merge").click()
    form = context.browser.find_element_by_id('mergeObjectsModal')
    form.find_element_by_id("merge-objects-name-input").send_keys("Merged Object")
    form.find_element_by_id("merge-objects-description-input").send_keys("Describing Merge")
    select = Select(form.find_element_by_tag_name("select"))
    select.select_by_visible_text("partner")
    form.submit()

@then('I should see my project')
def step_impl(context):
    assert context.browser.find_element(By.LINK_TEXT, 'my project')


@then('I should see myDiagram')
def step_impl(context):
    assert context.browser.find_element_by_id('myDiagram')


@when('I save')
def step_impl(context):
    context.browser.find_element_by_id("FileMenu").click()
    context.browser.find_element_by_id("save").click()


@then('I should see a save success message')
def step_impl(context):
    wait = WebDriverWait(context.browser, 1)
    wait.until(lambda driver: driver.find_element_by_class_name('ajs-success').is_displayed())
    assert True


@then('There should be three object nodes, one action nodes, one control node and four edges in the database')
def step_impl(context):
    nodes = {"ActionNode": 0, "ObjectNode": 0, "ControlNode": 0}
    for node in Project.objects.get(name='my project').graph.nodes.all():
        nodes[node.cast().__class__.__name__] += 1
    assert nodes["ActionNode"] == 1 and nodes["ObjectNode"] == 3 and nodes["ControlNode"] == 1


@then('I should these nodes to a fork node linked to a new action node linked to one new object node')
def impl(context):
    assert context.browser.execute_script("""
        function getNode(name, category) {
            var node;
            var it = myDiagram.nodes;
            var counter = 0;
            while (it.next()) {
                if (name != null) {
                    if (it.key.part.data.name == name && it.key.part.data.category == category) {
                        counter++;
                        node = it.key;
                    }
                } else {
                    if (it.key.part.data.category == category) {
                        counter++;
                        node = it.key;
                    }
                }

            }
            node = counter == 1 ? node : null;
            return node;
        }
        function getLink(src, tgt) {
            var link;
            var it = myDiagram.links;
            var counter = 0;
            while (it.next()) {
                if (it.key.part.data.from == src && it.key.part.data.to == tgt) {
                    counter++;
                    link = it.key;
                }
            }
            link = counter == 1 ? link : null;
            return link;
        }
        var myObjectNode = getNode('My Object', 'Object');
        var partnerObjectNode = getNode('Partner Object', 'Object');
        var mergedObject = getNode('Merged Object', 'Object');
        var actionObject = getNode('Merging My Object and Partner Object into Merged Object', 'Action');
        var fork = getNode(null, 'Fork');
        return getLink(myObjectNode.data.key, fork.data.key) != null &&
            getLink(partnerObjectNode.data.key, fork.data.key) != null &&
            getLink(fork.data.key, actionObject.data.key) != null &&
            getLink(actionObject.data.key, mergedObject.data.key) != null;
    """)