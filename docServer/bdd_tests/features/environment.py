from selenium import webdriver
from pyvirtualdisplay import Display
from django_behave.runner import DjangoBehaveTestSuiteRunner
# This is necessary for all installed apps to be recognized, for some reason.
import django

BEHAVE_DEBUG_ON_ERROR = False


def before_all(context):
    context.display = Display(visible=0, size=(1024, 768))
    context.display.start()
    django.setup()
    context.runner = DjangoBehaveTestSuiteRunner()
    context.browser = webdriver.Firefox()
    context.browser.implicitly_wait(15)
    context.server_url = 'http://localhost:8081'
     ### Take a TestRunner hostage.
    # We'll use thise later to frog-march Django through the motions
    # of setting up and tearing down the test environment, including
    # test databases.

def after_all(context):
    context.browser.quit()
    context.display.stop()

def before_feature(context, feature):
    pass

def after_feature(context, feature):
    pass

def after_step(context, step):
    if BEHAVE_DEBUG_ON_ERROR and step.status == "failed":
        # -- ENTER DEBUGGER: Zoom in on failure location.
        # NOTE: Use IPython debugger, same for pdb (basic python debugger).
        import ipdb
        ipdb.post_mortem(step.exc_traceback)

def before_scenario(context, scenario):
    # Set up the scenario test environment
    # context.runner.setup_test_environment()
    # We must set up and tear down the entire database between
    # scenarios. We can't just use db transactions, as Django's
    # TestClient does, if we're doing full-stack tests with Mechanize,
    # because Django closes the db connection after finishing the HTTP
    # response.
    context.old_db_config = context.runner.setup_databases()

def after_scenario(context, scenario):
    # Tear down the scenario test environment.
    context.runner.teardown_databases(context.old_db_config)
    # context.runner.teardown_test_environment()

