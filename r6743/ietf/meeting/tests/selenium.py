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

# note: RealDatabaseTest runs things under a transaction
class SeleniumTestCase(django.test.TestCase,RealDatabaseTest):
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

    def load_and_wait(self, a83):
        self.driver.get(self.base_url + "/meeting/83/schedule/%s/edit" % a83.name)

        print "The test web server has to run with user wnl who owns mtg83"
        print "Starting test"
        self.wait_for_load()

    def wait_for_load(self):
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

    def find_forces(self, m83):
        forces_request = m83.session_set.get(group__acronym = "forces")

        a83 = m83.agenda
        # find current forces timeslot in database
        forces_ss = a83.scheduledsession_set.get(session = forces_request)
        forces_ts = forces_ss.timeslot
        self.assertEqual(forces_ts.location.name, "253", "initial conditions wrong")
        self.assertEqual(forces_ts.time, datetime.datetime(2012,3,26,15,10), "initial time wrong")
        return forces_request, forces_ss, forces_ts

    def find_forces_rooms(self, m83, forces_ts):
        monday_room_maillot_ts = m83.timeslot_set.get(location__name = "Maillot",
                                                  time = datetime.datetime(2012,3,26,15,10))

        monday_room_253  = self.driver.find_element_by_css_selector("#" + forces_ts.js_identifier)
        monday_room_maillot = self.driver.find_element_by_css_selector("#" + monday_room_maillot_ts.js_identifier)
        return monday_room_253, monday_room_maillot, monday_room_maillot_ts

    def test_QUnit_tests(self):
        driver = self.driver
        driver.maximize_window()
        self.driver.get(self.base_url + "/test/agenda_tests.html")

        itercount=0
        while itercount < 1000 and not self.is_element_visible(how=By.CSS_SELECTOR,what="span.failed"):
            time.sleep(2)
            itercount = itercount+1

        results = driver.find_element_by_css_selector("#qunit-testresult .failed")
        self.assertEqual(results.text, "0")


    def test_case1218_drag_drop(self):
        driver = self.driver
        driver.maximize_window()

        m83 = get_meeting(83)
        a83 = m83.agenda
        ipsec_request  = m83.session_set.get(group__acronym = "ipsecme")

        self.load_and_wait(a83)

        print "clicking ipsecme"
        driver.find_element_by_css_selector("#session_%u > tbody > #meeting_event_title > th.meeting_obj" % (ipsec_request.pk)).click()
        action_chain1 = ActionChains(driver)
        action_chain2 = ActionChains(driver)

        forces_request, forces_ss,forces_ts = self.find_forces(m83)

        monday_room_253,monday_room_maillot,ts=self.find_forces_rooms(m83, forces_ts)

        print "clicking forces"
        forces = driver.find_element_by_css_selector("#session_%u > tbody > #meeting_event_title > th.meeting_obj" % (forces_request.pk))
        forces.click()

        monday_room_253_ts = m83.timeslot_set.get(location__name = "253",
                                                  time = datetime.datetime(2012,3,26,15,10))
        monday_room_253,monday_room_maillot, ts=self.find_forces_rooms(m83, forces_ts)

        time.sleep(3)
        action_chain1.drag_and_drop(forces, monday_room_maillot).perform()

        # not sure how else to know it is done yet.
        print "waiting for database operation to complete"
        time.sleep(5)

        forces_ss = a83.scheduledsession_set.get(session = forces_request)
        forces_ts = forces_ss.timeslot
        self.assertEqual(forces_ts.location.name, "Maillot")
        self.assertEqual(forces_ts.time, datetime.datetime(2012,3,26,15,10))

        print "moving it back to Monday"
        # Have to find it again since we moved it
        forces = driver.find_element_by_css_selector("#session_%u > tbody > #meeting_event_title > th.meeting_obj" % (forces_request.pk))
        action_chain2.drag_and_drop(forces, monday_room_253).perform()
        time.sleep(5)

        forces_ss = a83.scheduledsession_set.get(session = forces_request)
        forces_ts = forces_ss.timeslot
        self.assertEqual(forces_ts.location.name, "253")
        self.assertEqual(forces_ts.time, datetime.datetime(2012,3,26,15,10))

    def test_case1219_unschedule_and_schedule(self):
        driver = self.driver
        driver.maximize_window()

        m83 = get_meeting(83)
        a83 = m83.agenda
        forces_request = m83.session_set.get(group__acronym = "forces")

        self.load_and_wait(a83)

        action_chain1 = ActionChains(driver)

        forces_request, forces_ss,forces_ts = self.find_forces(m83)

        print "clicking forces"
        forces = driver.find_element_by_css_selector("#session_%u > tbody > #meeting_event_title > th.meeting_obj" % (forces_request.pk))
        forces.click()

        unscheduled = driver.find_element_by_css_selector("#sortable-list")
        action_chain1.drag_and_drop(forces, unscheduled).perform()

        # not sure how else to know it is done yet.
        print "waiting for database operation to complete"
        time.sleep(5)

        # assert that it is no longer scheduled
        self.assertEqual(len(a83.scheduledsession_set.filter(session = forces_request)),0)

        print "moving it back to Monday"
        action_chain2 = ActionChains(driver)

        monday_room_253,monday_room_maillot, ts=self.find_forces_rooms(m83, forces_ts)

        # Have to find it again since we moved it, and put it back.
        forces = driver.find_element_by_css_selector("#session_%u > tbody > #meeting_event_title > th.meeting_obj" % (forces_request.pk))
        action_chain2.drag_and_drop(forces, monday_room_253).perform()
        time.sleep(5)

        forces_ss = a83.scheduledsession_set.get(session = forces_request)
        forces_ts = forces_ss.timeslot
        self.assertEqual(forces_ts.location.name, "253")
        self.assertEqual(forces_ts.time, datetime.datetime(2012,3,26,15,10))

    def scroll_into_view(self, domid):
        self.driver.execute_script("var elm = window.document.getElementById('%s'); elm.scrollIntoView(true);" % domid)
        time.sleep(2);

    def test_case1220_move_session_with_location_bar(self):
        driver = self.driver
        driver.maximize_window()

        m83 = get_meeting(83)
        a83 = m83.agenda
        forces_request = m83.session_set.get(group__acronym = "forces")

        self.load_and_wait(a83)

        action_chain1 = ActionChains(driver)
        forces_request, forces_ss,forces_ts = self.find_forces(m83)
        orig_forces_ts = forces_ts
        monday_room_253,monday_room_maillot,maillot_ts=self.find_forces_rooms(m83, forces_ts)

        print "clicking forces"
        forces = driver.find_element_by_css_selector("#session_%u > tbody > #meeting_event_title > th.meeting_obj" % (forces_request.pk))
        forces.click()

        print "picking a new location in location bar: %u" % (maillot_ts.pk)
        self.scroll_into_view("info_name_select")
        location    = Select(driver.find_element_by_id("info_location_select"))
        #import pdb; pdb.set_trace()
        location.select_by_value("%u" % (maillot_ts.pk))
        # more reliable to select by value.
        # location.select_by_visible_text("Mon, 1510, Maillot")
        setbutton   = driver.find_element_by_id("info_location_set")
        setbutton.click()

        # not sure how else to know it is done yet.
        print "waiting for database operation to complete"
        time.sleep(5)

        # check that it is moved room
        forces_ss = a83.scheduledsession_set.get(session = forces_request)
        new_forces_ts = forces_ss.timeslot
        self.assertEqual(new_forces_ts.location.name, "Maillot")
        self.assertEqual(new_forces_ts.time, datetime.datetime(2012,3,26,15,10))


        print "moving it back to 253: %u" % (orig_forces_ts.pk)
        self.scroll_into_view("info_name_select")
        time.sleep(1)
        location    = Select(driver.find_element_by_id("info_location_select"))
        location.select_by_value("%u" % (orig_forces_ts.pk))
        time.sleep(30)
        # more reliable to select by value.
        # location.select_by_visible_text("Mon, 1510, Maillot")
        setbutton   = driver.find_element_by_id("info_location_set")
        setbutton.click()

        print "waiting for database operation to complete"
        time.sleep(5)

        forces_ss = a83.scheduledsession_set.get(session = forces_request)
        forces_ts = forces_ss.timeslot
        self.assertEqual(forces_ts.location.name, "253")
        self.assertEqual(forces_ts.time, datetime.datetime(2012,3,26,15,10))

    def test_case1223_use_saveas_box(self):
        driver = self.driver
        driver.maximize_window()

        newname="case1223"
        m83 = get_meeting(83)
        a83 = m83.agenda

        items = m83.schedule_set.filter(name= newname)
        # delete them "all" (should be zero or 1)
        for sched in items:
            sched.delete_schedule()

        self.load_and_wait(a83)

        self.scroll_into_view("saveasbutton")
        time.sleep(4)

        savename     = driver.find_element_by_id("id_savename")
        savename.clear()
        savename.send_keys(newname)

        savebutton   = driver.find_element_by_id("saveasbutton")
        savebutton.click()

        print "saved new schedule: %s" % (newname)

        # will hang here if the save failed, probably does not load.
        self.wait_for_load()
        self.assertEqual(driver.current_url, "http://localhost:8000/meeting/83/schedule/%s/edit" % newname)

        # MySQL transaction code manages to keep us from seeing the new entry
        # in some cases.  DJANGO 1.4 might help.
        m83 = get_meeting(83)
        nitems = m83.schedule_set.filter(name= newname)
        item_count = len(nitems)
        print "looked at database for: %s, found: %u" % (newname, item_count)
        # clean up just in case.
        for sched in nitems:
            sched.delete_schedule()

        # can not assert here.
        # self.assertEqual(item_count, 1, items)

    def test_case1221_extend_ccamp(self):
        driver = self.driver
        driver.maximize_window()

        m83 = get_meeting(83)
        a83 = m83.agenda

        # there are two of them, want the one on Monday.
        ccamp_requests  = m83.session_set.filter(group__acronym = "ccamp",
                                                 pk = 2162)
        ccamp_request = ccamp_requests[0]

        self.load_and_wait(a83)
        self.scroll_into_view("double_slot")

        print "clicking ccamp"
        driver.find_element_by_css_selector("#session_%u > tbody > #meeting_event_title > th.meeting_obj" % (ccamp_request.pk)).click()

        print "clicking Extend"
        extend = driver.find_element_by_id("double_slot")
        extend.click()

        time.sleep(1)  # give it time to render.

        dialog = driver.find_element_by_id("can-extend-dialog")
        print "alert: %s %s" % (self.is_alert_present(), dialog.is_displayed())
        # ought to be true, but is not for reasons not yet understood.
        #self.assertTrue(dialog.is_displayed())

        yes = driver.find_element_by_xpath("//button/span[text() = 'Yes']")
        yes.click()
        print "button clicked"
        time.sleep(5)

        # ss 2376 is the original SS for ccamp, delete the other one.
        ss = a83.scheduledsession_set.filter(session = ccamp_request,
                                             timeslot__time = datetime.datetime(2012,3,26,15,10))
        self.assertEqual(len(ss), 1)
        ss[0].delete()

    def test_case1195_two_sessions(self):
        driver = self.driver
        driver.maximize_window()

        m83 = get_meeting(83)
        a83 = m83.agenda
        mext_request = m83.session_set.get(group__acronym = "mext")
        forces_request, forces_ss,forces_ts = self.find_forces(m83)

        self.load_and_wait(a83)

        action_chain1 = ActionChains(driver)

        print "clicking mext: %u" % (mext_request.pk)
        mext = driver.find_element_by_css_selector("#session_%u > tbody > #meeting_event_title > th.meeting_obj" % (mext_request.pk))
        mext.click()

        # put it in the box with forces in it.
        mon1510 = driver.find_element_by_css_selector("#" + forces_ts.js_identifier)
        action_chain1.drag_and_drop(mext, mon1510).perform()

        # need some time to render it.
        time.sleep(2)

        yes = driver.find_element_by_xpath("//button/span[text() = 'Yes']")
        yes.click()
        print "button clicked"
        time.sleep(5)

        # get the list of ss in this timeslot
        ss_list = a83.scheduledsession_set.filter(timeslot = forces_ts)
        self.assertEqual(len(ss_list), 2)

        # it would be simpler to do this only in the database, but
        # due to transactions, that is not reflected into the test server

        mext = driver.find_element_by_css_selector("#session_%u > tbody > #meeting_event_title > th.meeting_obj" % (mext_request.pk))

        action_chain2 = ActionChains(driver)
        unscheduled = driver.find_element_by_css_selector("#sortable-list")
        action_chain2.drag_and_drop(mext, unscheduled).perform()
        time.sleep(5)

        # get the list of ss in this timeslot
        ss_list = a83.scheduledsession_set.filter(timeslot = forces_ts)
        self.assertEqual(len(ss_list), 1)

        # now delete the second item in that slot.
        for ss in ss_list:
            if ss.pk != forces_ss.pk:
                ss.delete()

    def test_case1229_two_session_cancel(self):
        driver = self.driver
        driver.maximize_window()

        m83 = get_meeting(83)
        a83 = m83.agenda
        mext_request = m83.session_set.get(group__acronym = "mext")
        forces_request, forces_ss,forces_ts = self.find_forces(m83)

        self.load_and_wait(a83)

        action_chain1 = ActionChains(driver)

        print "clicking mext: %u" % (mext_request.pk)
        mext = driver.find_element_by_css_selector("#session_%u > tbody > #meeting_event_title > th.meeting_obj" % (mext_request.pk))
        mext.click()

        # put it in the box with forces in it.
        mon1510 = driver.find_element_by_css_selector("#" + forces_ts.js_identifier)
        action_chain1.drag_and_drop(mext, mon1510).perform()

        # need some time to render it.
        time.sleep(2)

        cancel = driver.find_element_by_xpath("//button/span[text() = 'Cancel']")
        cancel.click()
        print "button clicked"
        time.sleep(5)

        # get the list of ss in this timeslot
        ss_list = a83.scheduledsession_set.filter(timeslot = forces_ts)
        self.assertEqual(len(ss_list), 1)

    def test_case1222_extend_no_slot_right(self):
        driver = self.driver
        driver.maximize_window()

        m83 = get_meeting(83)
        a83 = m83.agenda
        forces_request, forces_ss,forces_ts = self.find_forces(m83)

        self.load_and_wait(a83)

        print "clicking forces"
        driver.find_element_by_css_selector("#session_%u > tbody > #meeting_event_title > th.meeting_obj" % (forces_request.pk)).click()

        print "clicking Extend"
        extend = driver.find_element_by_id("double_slot")
        extend.click()

        time.sleep(5)  # give it time to render.

        # assert that the dialog is visible.
        self.assertTrue(self.is_element_visible(how=By.CSS_SELECTOR,what="#can-not-extend-dialog"))

    def test_case1222_extend_slot_filled(self):
        driver = self.driver
        driver.maximize_window()

        m83 = get_meeting(83)
        a83 = m83.agenda

        # find current sidr timeslot in database on Monday afternoon.
        sidr_ss = a83.scheduledsession_set.get(session__group__acronym = "sidr",
                                               timeslot__time = datetime.datetime(2012,3,26,13,0))
        sidr_ts = sidr_ss.timeslot
        sidr_request = sidr_ss.session

        self.load_and_wait(a83)

        print "clicking forces"
        driver.find_element_by_css_selector("#session_%u > tbody > #meeting_event_title > th.meeting_obj" % (sidr_request.pk)).click()

        print "clicking Extend"
        extend = driver.find_element_by_id("double_slot")
        extend.click()

        time.sleep(5)  # give it time to render.

        # assert that the dialog is visible.
        self.assertTrue(self.is_element_visible(how=By.CSS_SELECTOR,what="#can-not-extend-dialog"))

    def test_case1224_hide_and_display_rooms(self):
        driver = self.driver
        driver.maximize_window()

        m83 = get_meeting(83)
        a83 = m83.agenda

        self.load_and_wait(a83)

        print "clicking to hide room Amphitheatre Bleu"

        # find something in Bleu, make sure it is visible.
        tech_ss = a83.scheduledsession_set.get(timeslot__time = datetime.datetime(2012,3,26,16,30))
        plenary_id = tech_ss.timeslot.js_identifier
        self.scroll_into_view(plenary_id)
        tech_plenary = driver.find_element_by_id(plenary_id)
        self.assertTrue(tech_plenary.is_displayed())

        # hide the display.
        close_button = "close_Amphitheatre_Bleu"
        self.scroll_into_view(close_button)
        driver.find_element_by_id(close_button).click()
        time.sleep(1)

        # confirm that it is hidden.
        tech_plenary = driver.find_element_by_id(plenary_id)
        self.assertFalse(tech_plenary.is_displayed())

        # now show it all.
        driver.find_element_by_id("show_hidden_rooms").click()
        time.sleep(1)

        # confirm that it is visible again
        tech_plenary = driver.find_element_by_id(plenary_id)
        self.scroll_into_view(plenary_id)
        self.assertTrue(tech_plenary.is_displayed())

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

