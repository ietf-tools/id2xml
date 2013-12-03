from __future__ import absolute_import
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver import ActionChains
from selenium.common.exceptions import NoSuchElementException
from ietf.utils import TestCase

class SeleniumTestCase(TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(30)
        self.base_url = "http://localhost:8000"
        self.verificationErrors = []
        self.accept_next_alert = True

    def test_seltest1_python(self):
        driver = self.driver
        driver.maximize_window()
        driver.get(self.base_url + "/meeting/83/schedule/mtg_83/edit")

        print "The test web server has to run with user wnl who owns mtg83"
        print "Starting test"
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

        print "clicking forces"
        driver.find_element_by_css_selector("#session_2230 > tbody > #meeting_event_title > th.meeting_obj").click()
        action_chain1 = ActionChains(driver)
        action_chain2 = ActionChains(driver)

        forces = driver.find_element_by_css_selector("#session_2180 > tbody > #meeting_event_title > th.meeting_obj")

        monday_room_253  = driver.find_element_by_css_selector("#room208_2012-03-26_1510")
        friday_room_252A = driver.find_element_by_css_selector("#room209_2012-03-30_1230")
        print "moving to Friday"
        action_chain1.drag_and_drop(forces, friday_room_252A).perform()
        # how can we know it really worked, if we can't control the test server directly?

        time.sleep(5)

        print "moving to Monday"
        # Have to find it again since we moved it
        forces = driver.find_element_by_css_selector("#session_2180 > tbody > #meeting_event_title > th.meeting_obj")
        action_chain2.drag_and_drop(forces, monday_room_253).perform()
        time.sleep(15)

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

if __name__ == "__main__":
    unittest.main()

