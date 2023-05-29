# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import re
import datetime
from itemadapter import ItemAdapter


class FormatRewardAmountPipeline:
    """
        class to format reward amount
    """
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        if adapter.get('reward_amount'):
            reward_amount = adapter['reward_amount']
            adapter['reward_amount'] = reward_amount.replace("Up to ", "")

        return item


class ListtoStringPipeline:
    """
        class to convert list to string
    """
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        if adapter.get('about'):
            about_list = adapter['about']
            adapter['about'] = " ".join(about_list)

        if adapter.get('associated_location'):
            association_list = adapter['associated_location']
            adapter['associated_location'] = " ".join(association_list)

        return item


class FormatDatePipeline:
    """
        class to remove tabs, newline characters and format date value
    """
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        if adapter.get('date_of_birth'):
            dob = adapter['date_of_birth']

            clean_dob = re.sub(r'[\n\t]', "", dob).strip()
            clean_dob_string = self.remove_unwanted_strings(clean_dob)

            try:
                clean_dob_string = self.get_date_format(clean_dob_string)
            except ValueError:
                try:
                    formated_dob_list = self.format_dob_list(clean_dob)
                    clean_dob_string = "; ".join(formated_dob_list)
                except Exception:
                    pass

            adapter['date_of_birth'] = clean_dob_string

        return item

    def format_dob_list(self, clean_dob):
        """To format date if more than one date fouind

        Args:
            clean_dob (strin): dob string to be formatted

        Returns:
            list: A list of formatted date strings
        """
        old_dob_list = clean_dob.split(";")
        new_dob_list = []
        for dob in old_dob_list:
            try:
                new_dob = self.get_date_format(dob.strip())
            except ValueError:
                new_dob = dob
            new_dob_list.append(new_dob)
        return new_dob_list

    def get_date_format(self, string):
        """To get required date format

        Args:
            string (str): string to be converted

        Returns:
            string: required date format
        """
        date_string = datetime.datetime.strptime(string, "%B %d, %Y")
        return date_string.strftime("%Y-%m-%d")

    def remove_unwanted_strings(self, string):
        """To remove unwanted strings

        Args:
            string (str): string to be cleaned

        Returns:
            str: cleaned string
        """
        unwanted_strings = [
            "Between", "Estimated", "Approximately"
        ]
        for word in unwanted_strings:
            if word in string:
                string = string.replace(word, "")
        return string
