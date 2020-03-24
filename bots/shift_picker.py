from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from personal.winter_break_2019.month_dict import month_dict  # This line must be changed to path
from personal.winter_break_2019.quickstart import schedule_matcher  # This line must be changed to path
from personal.winter_break_2019.emailer import *  # This line must be changed to path
import datetime
import calendar
import argparse
import getpass


class ShiftPicker:
    def __init__(self, username, password, sender, receiver):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
        self.driver = webdriver.Chrome(options=chrome_options)
        self.employee_set = set()
        self.username = username
        self.password = password
        self.email_sender = sender
        self.email_receiver = receiver

    def log_in(self):
        self.driver.get("https://whentowork.com/logins.htm")
        self.driver.find_element_by_id("username").send_keys(self.username)
        self.driver.find_element_by_id("password").send_keys(self.password)
        self.driver.find_element_by_xpath("/html/body/div[1]/div/div/div/div/form/div/button").click()

    @staticmethod
    def find_day(date):
        """
        Find day from date
        :param date: 'dd mm yyyy'
        :return:day
        :rtype str
        """
        day = datetime.datetime.strptime(date, '%d %m %Y').weekday()
        return calendar.day_name[day]

    def shift_iterator(self):
        """
        Iterates over shifts from one month

        :rtype month: str
        :rtype date: list
        :rtype time: list
        :rtype indices: list
        :return: month of shift, date of shit (list), time of shift (list),
        indices on shifts (list [[y,x]...])
        """
        month, year = self.driver.find_element_by_xpath('//*[@id="calbtn"]/nobr/span').text.split()

        xpath_txt = '// *[ @ id = "maincontent"] / table[1] / tbody / tr[2] / td / table[{}] / tbody / tr / td[{}]'
        xpath_x_nums = ['1', '2', '3', '4', '5', '6', '7']
        xpath_y_nums = ['1', '3', '5', '7', '9', '11', '13']

        date, time, indicess = [], [], []
        for x in xpath_x_nums:
            for y in xpath_y_nums:
                try:
                    xpath_info = self.driver.find_element_by_xpath(xpath_txt.format(y, x)).text
                except NoSuchElementException:
                    continue

                if len(xpath_info) > 10:
                    dt = month_dict[month][y][x]
                    date.append(dt)
                    info_parsed = xpath_info.splitlines()
                    time.append(info_parsed[1])
                    indicess.append([y, x])

                    # Handles up to four shifts posted each day
                    info_parsed_len = len(info_parsed)
                    if info_parsed_len > 6:
                        date.append(dt)
                        time.append(info_parsed[7])
                        indicess.append([y, x])
                    elif info_parsed_len > 5:
                        date.append(dt)
                        time.append(info_parsed[5])
                        indicess.append([y, x])
                    elif info_parsed_len > 4:
                        date.append(dt)
                        time.append(info_parsed[3])
                        indicess.append([y, x])

        return month, date, time, indicess

    @staticmethod
    def check_schedule(year_val, month_val, date_val, hour_valss):
        minus_count = 0
        old_date_num = None
        confss = []
        for ii, date_num in enumerate(date_val):
            date_num = int(date_num)
            if date_num == old_date_num:
                minus_count += 1
            old_date_num = date_num

            ii -= minus_count
            hour_vals = hour_valss[ii].split('-')

            hour_val_1 = int(hour_vals[0][:-3])
            am_pm_1 = hour_vals[0][-3:]

            if am_pm_1 == 'pm':
                hour_val_1 = (hour_val_1 + 12) % 24

            hour_val_2 = int(hour_vals[1][:-2])
            am_pm_2 = hour_vals[1][-2:]

            if am_pm_2 == 'pm':
                hour_val_2 = (hour_val_2 + 12) % 24

            conflict = schedule_matcher(year_val, month_val, date_num, hour_val_1, year_val, month_val, date_num,
                                        hour_val_2)

            confss.append(conflict)

        return confss

    @staticmethod
    def contains_any(string_val, set_v):
        """"" Check whether sequence str contains ANY of the items in set. """
        return 1 in [c in string_val for c in set_v]

    def employee_listing(self):
        # Get curreent employee list
        self.driver.find_element_by_xpath('//*[@id="emptop"]/tbody/tr/td[7]').click()
        xpath_txt_employee = '// *[ @ id = "maincontent"] / table[1] / tbody / tr[2] / td / table / tbody / tr[{}] / ' \
                             'td[1]'
        index = 4
        while True:
            try:
                xpath_info_employee = self.driver.find_element_by_xpath(xpath_txt_employee.format(index)).text.split()
                xpath_info_employee_copy = xpath_info_employee
                xpath_info_employee = [x.lower() for x in xpath_info_employee]
                xpath_info_employee.extend(xpath_info_employee_copy)
                self.employee_set.update(xpath_info_employee)
            except NoSuchElementException:
                break
            index += 1

        self.driver.find_element_by_xpath('//*[@id="emptop"]/tbody/tr/td[5]').click()
        self.driver.find_element_by_xpath('//*[@id="emptopnav"]/table/tbody/tr/td[3]/table/tbody/tr[2]/td[4]').click()

        return None

    def shift_picker(self):
        """Picks shift, if no employee names are found in comments, no conflict exits with calender events"""

        month_1, date_1, time_1, indices_1 = self.shift_iterator()
        self.driver.find_element_by_xpath('//*[@id="calbtn"]/nobr/span/a[2]').click()  # going to next month
        month_2, date_2, time_2, indices_2 = self.shift_iterator()

        # Converting date time to appropriate format
        if month_1 == 'December':
            year_1 = 2019
            year_2 = 2020
        else:
            year_1, year_2 = 2020, 2020

        months = [month_1, month_2]
        times = [time_1, time_2]

        month_to_num = {name: num for num, name in enumerate(calendar.month_name) if num}
        month_1 = month_to_num[month_1]
        month_2 = month_to_num[month_2]

        conflicts_1 = self.check_schedule(year_1, month_1, date_1, time_1)
        conflicts_2 = self.check_schedule(year_2, month_2, date_2, time_2)

        indices = [indices_1, indices_2]
        for i, confs in enumerate([conflicts_1, conflicts_2]):
            # problem here
            xclick_additional = ''
            old_indx = [0, 0]
            for j, indx in enumerate(indices[i]):
                if indx == old_indx:
                    xclick_additional += '/ divmyshiftontb '
                else:
                    xclick_additional = ''

                old_indx = indx

                if len(confs[j]) == 0:
                    xpath_click = '// *[ @ id = "maincontent"] / table[1] / tbody / tr[2] / td / table[{}] / tbody / ' \
                                  'tr / td[{}]/ divmyshiftontb {}/ a'.format(indx[0], indx[1], xclick_additional)

                    self.driver.find_element_by_xpath(xpath_click).click()

                    switched = False
                    try:  # Don't pick up if employee name in comment
                        window_after = self.driver.window_handles[1]
                        self.driver.switch_to.window(window_after)
                        switched = True
                        comment = self.driver.find_element_by_xpath(
                            '/html/body/div/table[1]/tbody/tr[2]/td/table/tbody/tr[6]/'
                            'td[2]').text

                        if self.contains_any(comment, self.employee_set):
                            continue

                    except NoSuchElementException:
                        pass

                    try:  # Finally picks shift
                        self.driver.find_element_by_xpath('/html/body/div/table[2]/tbody/tr[2]/td/b/a').click()

                        # email subject for later
                        day_val = month_dict[months[i]][indx[0]][indx[1]]
                        subject = '{}/{}/{}'.format(months[i], day_val, times[i][j])

                        # lets load our previously picked shifts, so we don't pick it again
                        with open('pick_store.pkl', 'rb') as f:
                            my_list = pickle.load(f)

                        if subject in my_list:
                            # Cancel button
                            self.driver.find_element_by_xpath('//*[@id="customconfirm"]/div[3]/button[2]').click()
                        else:
                            # Confirm pick up button
                            self.driver.find_element_by_xpath('//*[@id="customconfirm"]/div[3]/button[1]').click()
                            my_list.append(subject)
                            # lets store our picked shift, so we don't pick it again
                            with open('pick_store.pkl', 'wb') as f:
                                pickle.dump(my_list, f)

                        # lets also send an email to user about requested shift
                        msgg = create_message(self.email_sender, self.email_receiver, subject, 'happy :)')
                        srvcc = get_service()
                        send_message(srvcc, "me", msgg)

                    except NoSuchElementException:
                        pass

                    if switched:
                        window_before = self.driver.window_handles[0]
                        self.driver.switch_to.window(window_before)

        self.driver.find_element_by_xpath('//*[@id="calbtn"]/nobr/a').click()


class Password:
    """Class for getting user password"""

    DEFAULT = 'Prompt if not specified'

    def __init__(self, value):
        if value == self.DEFAULT:
            value = getpass.getpass('W2W Password: ')
        self.value = value

    def __str__(self):
        return self.value


if __name__ == '__main__':
    """Chrome driver MUST be installed to run. This code was designed to be run on  linux operating systems"""
    # Let's get the w2w username and password
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-u', '--username', help='Specify username', default=getpass.getuser())
    parser.add_argument('-p', '--password', type=Password, help='Specify password', default=Password.DEFAULT)
    parser.add_argument('-s', '--sender_email', help='Sender email')
    parser.add_argument('-r', '--receiver_email', help='receiver_email')

    args = parser.parse_args()

    # lets start working
    worker = ShiftPicker(args.username, str(args.password), args.sender_email, args.receiver_email)
    worker.log_in()
    worker.employee_listing()  # Lets get the employee names to make sure we don't pick up pre assigned shifts
    worker.shift_picker()

    # driver.close()
