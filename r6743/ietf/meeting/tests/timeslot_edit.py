from __future__ import absolute_import
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver import ActionChains
from selenium.common.exceptions import NoSuchElementException
import django.test
from ietf.utils import TestCase
from ietf.utils.test_utils import RealDatabaseTest

from ietf.meeting.helpers import get_meeting, get_schedule
import datetime

class TimeslotEditTestCase(django.test.TestCase,RealDatabaseTest):
    def setUp(self):
        self.setUpRealDatabase()
        self.driver = webdriver.Firefox()
        fp = webdriver.FirefoxProfile()
        fp.set_preference("webdriver.firefox.profile", "selenium")
        fp.update_preferences()
        self.driver.implicitly_wait(30)
        self.base_url = "http://localhost:8000"
        self.verificationErrors = []
        self.accept_next_alert = True

    def load_and_wait(self):
        self.driver.get(self.base_url + "/meeting/83/timeslots/edit")

        print "The test web server has to run with user wnl who owns mtg83"
        print "Starting test"
        self.wait_for_load()

    def wait_for_load(self):
        time.sleep(1)
        if not self.is_element_visible(how=By.CSS_SELECTOR,what="#pageloaded"):
            itercount=0
            while itercount < 1000 and not self.is_element_visible(how=By.CSS_SELECTOR,what="#spinner"):
                time.sleep(2)
                itercount = itercount+1
            self.assertTrue(self.is_element_visible(how=By.CSS_SELECTOR,what="#spinner"))
            print "Found page loading"

            itercount=0
            while itercount < 1000 and self.is_element_visible(how=By.CSS_SELECTOR,what="#spinner"):
                time.sleep(2)
                itercount = itercount+1
            self.assertFalse(self.is_element_visible(how=By.CSS_SELECTOR,what="#spinner"))
        print "Found page loaded"

    def test_timeslots_loaded(self):
        driver = self.driver
        driver.maximize_window()
        self.load_and_wait()

    # XXX should refactor selenium.py and this file into a superclass.
    def is_element_present(self, how, what):
        try:
            self.driver.find_element(by=how, value=what)
        except NoSuchElementException, e:
            return False
        return True

    def is_element_visible(self, how, what):
        try:
           element = self.driver.find_element(by=how, value=what)
        except NoSuchElementException, e:
            return False
        return element.is_displayed()

    def is_alert_present(self):
        try:
            self.driver.switch_to_alert()
        except NoAlertPresentException, e:
            return False
        return True

    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally:
            self.accept_next_alert = True

    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)
        self.tearDownRealDatabase()

if __name__ == "__main__":
    unittest.main()

