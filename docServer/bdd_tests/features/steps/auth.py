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

@when('I log in as "{username}" "{password}"')
def step_impl(context, username, password):
    try:
        context.browser.get(context.server_url + '/account/login/')
        wait = WebDriverWait(context.browser, 0.1).until(EC.alert_is_present(),
                                       'Timed out waiting for PA creation ' +
                                       'confirmation popup to appear.')
        alert = context.browser.switch_to_alert()
        alert.accept()
    except TimeoutException:
        pass
    form = context.browser.find_element_by_id('login_form')
    context.browser.find_element_by_id('id_username').send_keys(username)
    context.browser.find_element_by_id('id_password').send_keys(password)
    form.submit()


@when('I sign up as "{username}", "{password}", "{email}"')
def step_impl(context, username, password, email):
    try:
        context.browser.get(context.server_url + '/account/signup/')
        wait = WebDriverWait(context.browser, 0.1).until(EC.alert_is_present(),
                                       'Timed out waiting for PA creation ' +
                                       'confirmation popup to appear.')
        alert = context.browser.switch_to_alert()
        alert.accept()
    except TimeoutException:
        pass
    form = context.browser.find_element_by_id('signup_form')
    context.browser.find_element_by_id('id_username').send_keys(username)
    context.browser.find_element_by_id('id_password').send_keys(password)
    context.browser.find_element_by_id('id_password_confirm').send_keys(password)
    context.browser.find_element_by_id('id_email').send_keys(email)
    form.submit()


@then('I should see a login error message')
def step_impl(context):
    wait = WebDriverWait(context.browser, 1)
    wait.until(lambda driver: driver.find_element_by_class_name('alert-danger').is_displayed())
    assert True


@then('log in for "{username}" should be successful')
def step_impl(context, username):
    assert context.browser.find_element(By.LINK_TEXT, username)