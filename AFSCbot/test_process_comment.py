import unittest
from process_comment import get_enlisted_regex_matches, get_officer_regex_matches, break_up_regex
from read_csv_files import get_AFSCs, get_prefixes, get_afsc_links

#####################
""" Unit tests """
#####################


class EnlistedRegexMatch(unittest.TestCase):
    def test_normal_afsc(self):
        comment = "1W051"
        matches = get_enlisted_regex_matches(comment)
        str_matches = break_up_regex(matches)
        self.assertEqual(len(str_matches), 1)
        self.assertEqual(str_matches[0]["whole_match"], "1W051")
        self.assertEqual(str_matches[0]["prefix"], "")
        self.assertEqual(str_matches[0]["afsc"], "1W051")
        self.assertEqual(str_matches[0]["skill_level"], "5")
        self.assertEqual(str_matches[0]["suffix"], "")

    def test_lowercase_afsc(self):
        comment = "k1w051c"
        matches = get_enlisted_regex_matches(comment)
        str_matches = break_up_regex(matches)
        self.assertEqual(len(str_matches), 1)
        self.assertEqual(str_matches[0]["whole_match"], "K1W051C")
        self.assertEqual(str_matches[0]["prefix"], "K")
        self.assertEqual(str_matches[0]["afsc"], "1W051")
        self.assertEqual(str_matches[0]["skill_level"], "5")
        self.assertEqual(str_matches[0]["suffix"], "C")

    def test_match_two_afsc(self):
        comment = "I once saw a 1W051 who thought he was a 1W091."
        matches = get_enlisted_regex_matches(comment)
        str_matches = break_up_regex(matches)

        self.assertEqual(len(str_matches), 2)
        self.assertEqual(str_matches[0]["whole_match"], "1W051")
        self.assertEqual(str_matches[0]["prefix"], "")
        self.assertEqual(str_matches[0]["afsc"], "1W051")
        self.assertEqual(str_matches[0]["skill_level"], "5")
        self.assertEqual(str_matches[0]["suffix"], "")

        self.assertEqual(str_matches[1]["whole_match"], "1W091")
        self.assertEqual(str_matches[1]["prefix"], "")
        self.assertEqual(str_matches[1]["afsc"], "1W091")
        self.assertEqual(str_matches[1]["skill_level"], "9")
        self.assertEqual(str_matches[1]["suffix"], "")

    def test_match_multiple_afsc(self):
        comment = "Q1A371 Q1A1X1 K1B4X1 T1C671"
        matches = get_enlisted_regex_matches(comment)
        str_matches = break_up_regex(matches)

        self.assertEqual(len(str_matches), 4)
        self.assertEqual(str_matches[0]["whole_match"], "Q1A371")
        self.assertEqual(str_matches[0]["prefix"], "Q")
        self.assertEqual(str_matches[0]["afsc"], "1A371")
        self.assertEqual(str_matches[0]["skill_level"], "7")
        self.assertEqual(str_matches[0]["suffix"], "")

        self.assertEqual(str_matches[1]["whole_match"], "Q1A1X1")
        self.assertEqual(str_matches[1]["prefix"], "Q")
        self.assertEqual(str_matches[1]["afsc"], "1A1X1")
        self.assertEqual(str_matches[1]["skill_level"], "X")
        self.assertEqual(str_matches[1]["suffix"], "")

        self.assertEqual(str_matches[2]["whole_match"], "K1B4X1")
        self.assertEqual(str_matches[2]["prefix"], "K")
        self.assertEqual(str_matches[2]["afsc"], "1B4X1")
        self.assertEqual(str_matches[2]["skill_level"], "X")
        self.assertEqual(str_matches[2]["suffix"], "")

        self.assertEqual(str_matches[3]["whole_match"], "T1C671")
        self.assertEqual(str_matches[3]["prefix"], "T")
        self.assertEqual(str_matches[3]["afsc"], "1C671")
        self.assertEqual(str_matches[3]["skill_level"], "7")
        self.assertEqual(str_matches[3]["suffix"], "")

    def test_normal_prefix(self):
        comment = "K3E491"
        matches = get_enlisted_regex_matches(comment)
        str_matches = break_up_regex(matches)
        self.assertEqual(len(str_matches), 1)
        self.assertEqual(str_matches[0]["whole_match"], "K3E491")
        self.assertEqual(str_matches[0]["prefix"], "K")
        self.assertEqual(str_matches[0]["afsc"], "3E491")
        self.assertEqual(str_matches[0]["skill_level"], "9")
        self.assertEqual(str_matches[0]["suffix"], "")

    def test_normal_suffix(self):
        comment = "2A334L"
        matches = get_enlisted_regex_matches(comment)
        str_matches = break_up_regex(matches)
        self.assertEqual(len(str_matches), 1)
        self.assertEqual(str_matches[0]["whole_match"], "2A334L")
        self.assertEqual(str_matches[0]["prefix"], "")
        self.assertEqual(str_matches[0]["afsc"], "2A334")
        self.assertEqual(str_matches[0]["skill_level"], "3")
        self.assertEqual(str_matches[0]["suffix"], "L")

    def test_normal_prefix_and_suffix(self):
        comment = "K3N1X1Q"
        matches = get_enlisted_regex_matches(comment)
        str_matches = break_up_regex(matches)
        self.assertEqual(len(str_matches), 1)
        self.assertEqual(str_matches[0]["whole_match"], "K3N1X1Q")
        self.assertEqual(str_matches[0]["prefix"], "K")
        self.assertEqual(str_matches[0]["afsc"], "3N1X1")
        self.assertEqual(str_matches[0]["skill_level"], "X")
        self.assertEqual(str_matches[0]["suffix"], "Q")

    def test_afsc_with_3_zeros(self):
        # should skill level return 0 or X or blank?
        comment = "9J000"
        matches = get_enlisted_regex_matches(comment)
        str_matches = break_up_regex(matches)
        self.assertEqual(len(str_matches), 1)
        self.assertEqual(str_matches[0]["whole_match"], "9J000")
        self.assertEqual(str_matches[0]["prefix"], "")
        self.assertEqual(str_matches[0]["afsc"], "9J000")
        self.assertEqual(str_matches[0]["skill_level"], "0")
        self.assertEqual(str_matches[0]["suffix"], "")

        comment = "8P100"
        matches = get_enlisted_regex_matches(comment)
        str_matches = break_up_regex(matches)
        self.assertEqual(len(str_matches), 1)
        self.assertEqual(str_matches[0]["whole_match"], "8P100")
        self.assertEqual(str_matches[0]["prefix"], "")
        self.assertEqual(str_matches[0]["afsc"], "8P100")
        self.assertEqual(str_matches[0]["skill_level"], "0")
        self.assertEqual(str_matches[0]["suffix"], "")

    def test_block_of_text(self):
        comment = "here look at that 1C4X1 he is so cool"
        matches = get_enlisted_regex_matches(comment)
        str_matches = break_up_regex(matches)
        self.assertEqual(len(str_matches), 1)
        self.assertEqual(str_matches[0]["whole_match"], "1C4X1")
        self.assertEqual(str_matches[0]["prefix"], "")
        self.assertEqual(str_matches[0]["afsc"], "1C4X1")
        self.assertEqual(str_matches[0]["skill_level"], "X")
        self.assertEqual(str_matches[0]["suffix"], "")

    def test_similar_to_afsc(self):
        comment = "1W0X"
        matches = get_enlisted_regex_matches(comment)
        str_matches = break_up_regex(matches)
        self.assertEqual(len(str_matches), 0)

        comment = "1W01"
        matches = get_enlisted_regex_matches(comment)
        str_matches = break_up_regex(matches)
        self.assertEqual(len(str_matches), 0)

        comment = "AW0X1"
        matches = get_enlisted_regex_matches(comment)
        str_matches = break_up_regex(matches)
        self.assertEqual(len(str_matches), 0)

        comment = "1WOX1"
        matches = get_enlisted_regex_matches(comment)
        str_matches = break_up_regex(matches)
        self.assertEqual(len(str_matches), 0)

    def test_shred_is_number(self):
        comment = "1W0X12"
        matches = get_enlisted_regex_matches(comment)
        str_matches = break_up_regex(matches)
        self.assertEqual(len(str_matches), 1)
        self.assertEqual(str_matches[0]["whole_match"], "1W0X1")
        self.assertEqual(str_matches[0]["prefix"], "")
        self.assertEqual(str_matches[0]["afsc"], "1W0X1")
        self.assertEqual(str_matches[0]["skill_level"], "X")
        self.assertEqual(str_matches[0]["suffix"], "")

        comment = "1W0X123"
        matches = get_enlisted_regex_matches(comment)
        str_matches = break_up_regex(matches)
        self.assertEqual(len(str_matches), 1)
        self.assertEqual(str_matches[0]["whole_match"], "1W0X1")
        self.assertEqual(str_matches[0]["prefix"], "")
        self.assertEqual(str_matches[0]["afsc"], "1W0X1")
        self.assertEqual(str_matches[0]["skill_level"], "X")
        self.assertEqual(str_matches[0]["suffix"], "")

    def test_prefix_is_number(self):
        comment = "11W0X1"
        matches = get_enlisted_regex_matches(comment)
        str_matches = break_up_regex(matches)
        self.assertEqual(len(str_matches), 0)

        comment = "121W0X1"
        matches = get_enlisted_regex_matches(comment)
        str_matches = break_up_regex(matches)
        self.assertEqual(len(str_matches), 0)

    def test_afsc_within_other_words(self):
        comment = "someletters1T0X1moreletters"
        matches = get_enlisted_regex_matches(comment)
        str_matches = break_up_regex(matches)

        self.assertEqual(len(str_matches), 0)

    def test_afsc_with_punctuation(self):
        comment = "1S071."
        matches = get_enlisted_regex_matches(comment)
        str_matches = break_up_regex(matches)
        self.assertEqual(len(str_matches), 1)
        self.assertEqual(str_matches[0]["whole_match"], "1S071")
        self.assertEqual(str_matches[0]["prefix"], "")
        self.assertEqual(str_matches[0]["afsc"], "1S071")
        self.assertEqual(str_matches[0]["skill_level"], "7")
        self.assertEqual(str_matches[0]["suffix"], "")

        comment = "1S071,"
        matches = get_enlisted_regex_matches(comment)
        str_matches = break_up_regex(matches)
        self.assertEqual(len(str_matches), 1)

        comment = "1S071?"
        matches = get_enlisted_regex_matches(comment)
        str_matches = break_up_regex(matches)
        self.assertEqual(len(str_matches), 1)

        comment = "1S071,"
        matches = get_enlisted_regex_matches(comment)
        str_matches = break_up_regex(matches)
        self.assertEqual(len(str_matches), 1)

    def test_afsc_in_hyperlink(self):
        comment = "https://www.reddit.com/r/AirForce/wiki/jobs/1a8x1"
        matches = get_enlisted_regex_matches(comment)
        str_matches = break_up_regex(matches)
        self.assertEqual(len(str_matches), 0)

        comment = "https://www.reddit.com/r/AirForce/wiki/jobs/1a8x1/other"
        matches = get_enlisted_regex_matches(comment)
        str_matches = break_up_regex(matches)
        self.assertEqual(len(str_matches), 0)

        comment = "https://www.1a8x1.com"
        matches = get_enlisted_regex_matches(comment)
        str_matches = break_up_regex(matches)
        self.assertEqual(len(str_matches), 0)


class OfficerRegexMatch(unittest.TestCase):
    def test_normal_afsc(self):
        comment = "12HX"
        matches = get_officer_regex_matches(comment)
        str_matches = break_up_regex(matches)
        self.assertEqual(len(str_matches), 1)
        self.assertEqual(str_matches[0]["whole_match"], "12HX")
        self.assertEqual(str_matches[0]["prefix"], "")
        self.assertEqual(str_matches[0]["afsc"], "12HX")
        self.assertEqual(str_matches[0]["skill_level"], "X")
        self.assertEqual(str_matches[0]["suffix"], "")

    def test_lowercase_afsc(self):
        comment = "12hx"
        matches = get_officer_regex_matches(comment)
        str_matches = break_up_regex(matches)
        self.assertEqual(len(str_matches), 0)

        comment = "12h"
        matches = get_officer_regex_matches(comment)
        str_matches = break_up_regex(matches)
        self.assertEqual(len(str_matches), 0)

        comment = "12s"
        matches = get_officer_regex_matches(comment)
        str_matches = break_up_regex(matches)
        self.assertEqual(len(str_matches), 0)

    def test_afsc_sentence(self):
        comment = "Look at that 12HX. More like a Q13AX."
        matches = get_officer_regex_matches(comment)
        str_matches = break_up_regex(matches)
        self.assertEqual(len(str_matches), 2)
        self.assertEqual(str_matches[0]["whole_match"], "12HX")
        self.assertEqual(str_matches[0]["prefix"], "")
        self.assertEqual(str_matches[0]["afsc"], "12HX")
        self.assertEqual(str_matches[0]["skill_level"], "X")
        self.assertEqual(str_matches[0]["suffix"], "")

        self.assertEqual(str_matches[1]["whole_match"], "Q13AX")
        self.assertEqual(str_matches[1]["prefix"], "Q")
        self.assertEqual(str_matches[1]["afsc"], "13AX")
        self.assertEqual(str_matches[1]["skill_level"], "X")
        self.assertEqual(str_matches[1]["suffix"], "")

    def test_multiple_afsc(self):
        comment = "13A 15WX 16GX"
        matches = get_officer_regex_matches(comment)
        str_matches = break_up_regex(matches)

        self.assertEqual(len(str_matches), 3)
        self.assertEqual(str_matches[0]["whole_match"], "13A")
        self.assertEqual(str_matches[0]["prefix"], "")
        self.assertEqual(str_matches[0]["afsc"], "13A")
        self.assertEqual(str_matches[0]["skill_level"], "")
        self.assertEqual(str_matches[0]["suffix"], "")

        self.assertEqual(str_matches[1]["whole_match"], "15WX")
        self.assertEqual(str_matches[1]["prefix"], "")
        self.assertEqual(str_matches[1]["afsc"], "15WX")
        self.assertEqual(str_matches[1]["skill_level"], "X")
        self.assertEqual(str_matches[1]["suffix"], "")

        self.assertEqual(str_matches[2]["whole_match"], "16GX")
        self.assertEqual(str_matches[2]["prefix"], "")
        self.assertEqual(str_matches[2]["afsc"], "16GX")
        self.assertEqual(str_matches[2]["skill_level"], "X")
        self.assertEqual(str_matches[2]["suffix"], "")

    def test_prefix_is_a_number(self):
        comment = "112HX 9913AX"
        matches = get_officer_regex_matches(comment)
        str_matches = break_up_regex(matches)
        self.assertEqual(len(str_matches), 0)

    def test_suffix_is_a_number(self):
        comment = "12HX5 13AX66"
        matches = get_officer_regex_matches(comment)
        str_matches = break_up_regex(matches)
        self.assertEqual(len(str_matches), 2)
        self.assertEqual(str_matches[0]["whole_match"], "12HX")
        self.assertEqual(str_matches[0]["prefix"], "")
        self.assertEqual(str_matches[0]["afsc"], "12HX")
        self.assertEqual(str_matches[0]["skill_level"], "X")
        self.assertEqual(str_matches[0]["suffix"], "")

        self.assertEqual(str_matches[1]["whole_match"], "13AX")
        self.assertEqual(str_matches[1]["prefix"], "")
        self.assertEqual(str_matches[1]["afsc"], "13AX")
        self.assertEqual(str_matches[1]["skill_level"], "X")
        self.assertEqual(str_matches[1]["suffix"], "")

    def test_surrounded_by_text(self):
        comment = "fdsfjdf12HX123123  12HXasfsdf   asdfsdf12HX"
        matches = get_officer_regex_matches(comment)
        str_matches = break_up_regex(matches)
        self.assertEqual(len(str_matches), 1)
        self.assertEqual(str_matches[0]["whole_match"], "12HX")
        self.assertEqual(str_matches[0]["prefix"], "")
        self.assertEqual(str_matches[0]["afsc"], "12HX")
        self.assertEqual(str_matches[0]["skill_level"], "X")
        self.assertEqual(str_matches[0]["suffix"], "")

    def test_punctuation(self):
        comment = "13BX, 14NX, and 16GX! What about W11F5H?"
        matches = get_officer_regex_matches(comment)
        str_matches = break_up_regex(matches)
        self.assertEqual(len(str_matches), 4)
        self.assertEqual(str_matches[0]["whole_match"], "13BX")
        self.assertEqual(str_matches[0]["prefix"], "")
        self.assertEqual(str_matches[0]["afsc"], "13BX")
        self.assertEqual(str_matches[0]["skill_level"], "X")
        self.assertEqual(str_matches[0]["suffix"], "")

        self.assertEqual(str_matches[1]["whole_match"], "14NX")
        self.assertEqual(str_matches[1]["prefix"], "")
        self.assertEqual(str_matches[1]["afsc"], "14NX")
        self.assertEqual(str_matches[1]["skill_level"], "X")
        self.assertEqual(str_matches[1]["suffix"], "")

        self.assertEqual(str_matches[2]["whole_match"], "16GX")
        self.assertEqual(str_matches[2]["prefix"], "")
        self.assertEqual(str_matches[2]["afsc"], "16GX")
        self.assertEqual(str_matches[2]["skill_level"], "X")
        self.assertEqual(str_matches[2]["suffix"], "")

        self.assertEqual(str_matches[3]["whole_match"], "W11F5H")
        self.assertEqual(str_matches[3]["prefix"], "W")
        self.assertEqual(str_matches[3]["afsc"], "11F5")
        self.assertEqual(str_matches[3]["skill_level"], "5")
        self.assertEqual(str_matches[3]["suffix"], "H")

    def test_afsc_in_hyperlink(self):
        comment = "https://www.reddit.com/r/AirForce/wiki/jobs/13BX"
        matches = get_officer_regex_matches(comment)
        str_matches = break_up_regex(matches)
        self.assertEqual(len(str_matches), 0)

        comment = "https://www.reddit.com/r/AirForce/wiki/jobs/13BX/other"
        matches = get_officer_regex_matches(comment)
        str_matches = break_up_regex(matches)
        self.assertEqual(len(str_matches), 0)

        comment = "https://www.13BX.com"
        matches = get_officer_regex_matches(comment)
        str_matches = break_up_regex(matches)
        self.assertEqual(len(str_matches), 0)


"""
Some of these tests may fail because the csv files update.
In that case, double check if any titles have changed.
"""

'''
global test_prefix_dict
global test_afsc_dict

test_afsc_dict = get_AFSCs()
test_afsc_dict = get_afsc_links(test_afsc_dict)
test_prefix_dict = get_prefixes()
'''

class OfficerProcessComment(unittest.TestCase):

    def test_setup_prefix_dict(self):
        print(test_prefix_dict)

    def test_normal_afsc(self):
        print(self._prefix_dict)
        comment = "12HX"
        matches = get_officer_regex_matches(comment)
        str_matches = break_up_regex(matches)
        self.assertEqual(len(str_matches), 1)
        self.assertEqual(str_matches[0]["whole_match"], "12HX")
        self.assertEqual(str_matches[0]["prefix"], "")
        self.assertEqual(str_matches[0]["afsc"], "12HX")
        self.assertEqual(str_matches[0]["skill_level"], "X")
        self.assertEqual(str_matches[0]["suffix"], "")



unittest.main(module=__name__)