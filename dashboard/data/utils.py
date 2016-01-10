import json
import logging
import time

import pydash

from dashboard.helpers import NO, NOT_REPORTING, YES, NAME, EXISTING, NEW
from dashboard.models import CycleFormulationScore

logger = logging.getLogger(__name__)


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        print ('%r  %2.2f sec' % (method.__name__, te - ts))
        return result

    return timed


def clean_name(row):
    full_name = row[0].value
    replace_template = "_" + row[5].value.strip()
    return full_name.strip().replace(replace_template, "")


def reduce_to_values(records):
    def func(total, field):
        total.extend(pydash.pluck(records, field))
        return total

    return func


def values_for_records(fields, records):
    return pydash.reduce_(fields, reduce_to_values(records), [])


def get_consumption_totals(fields, records):
    return pydash.chain(values_for_records(fields, records)).reject(
            lambda x: x is None).sum().value()


def get_patient_total(records):
    return get_consumption_totals([NEW, EXISTING], records)


def calculate_percentages(no, not_reporting, total_count, yes):
    if total_count > 0:
        yes_rate = float(yes * 100) / float(total_count)
        no_rate = float(no * 100) / float(total_count)
        not_reporting_rate = float(not_reporting * 100) / float(total_count)
    else:
        no_rate = not_reporting_rate = yes_rate = 0
    return no_rate, not_reporting_rate, yes_rate


def build_cycle_formulation_score(formulation, yes, no, not_reporting, total_count):
    no, not_reporting, yes = calculate_percentages(no, not_reporting, total_count, yes)
    return {NO: no, NOT_REPORTING: not_reporting, YES: yes}


def has_blank(records, fields):
    return pydash.some(values_for_records(fields, records), lambda x: x is None)


def has_all_blanks(records, fields):
    return pydash.every(values_for_records(fields, records), lambda x: x is None)


def write_to_disk(report, file_out):
    with open(file_out, "w") as outfile:
        json.dump(report.cs, outfile)
    return report


class QCheck:
    combinations = []
    test = ""

    def __init__(self, report):
        self.report = report

    def score(self):
        formulation_scores = list()
        scores = self.run()
        print (self.test, scores)
        for key, value in scores.items():
            formulation_scores.append(
                    CycleFormulationScore(cycle=self.report.cycle, combination=key, yes=value[YES], no=value[NO],
                                          not_reporting=value[NOT_REPORTING], test=self.test))
        return formulation_scores

    def run(self):
        scores = dict()
        for combination in self.combinations:
            self.for_each_combination(combination, scores)
        return scores

    def for_each_combination(self, combination, scores):
        facilities = self.report.locs
        yes = 0
        no = 0
        not_reporting = 0
        total_count = len(facilities)
        formulation_name = combination[NAME]
        for facility in facilities:
            result, no, not_reporting, yes = self.for_each_facility(facility, no, not_reporting, yes, combination)
            facility['scores'][self.test][formulation_name] = result
        out = build_cycle_formulation_score(formulation_name, yes, no, not_reporting, total_count)
        scores[formulation_name] = out

    def for_each_facility(self, facility, no, not_reporting, yes, combination):
        raise NotImplementedError


def facility_not_reporting(facility):
    return facility['status'].strip() != 'Reporting'


def facility_has_single_order(facility):
    not_multiple = facility['Multiple'].strip() != 'Multiple orders'
    return not_multiple