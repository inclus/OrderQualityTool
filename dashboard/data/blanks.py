import pydash

from dashboard.data.utils import NAME, timeit, build_cycle_formulation_score, values_for_records, NEW, EXISTING
from dashboard.helpers import CONSUMPTION_AND_PATIENTS, NOT_REPORTING, YES, NO

F1_QUERY = "Efavirenz (TDF/3TC/EFV)"
F2_QUERY = "Lamivudine (ABC/3TC) 60mg/30mg [Pack 60]"
F3_QUERY = "EFV) 200mg [Pack 90]"


def has_blank_in_fields(fields):
    def func(record):
        values = values_for_records(fields, [record])
        return pydash.some(values, lambda f: f is None)

    return func


class BlanksQualityCheck():
    def __init__(self, report):
        self.report = report

    test = CONSUMPTION_AND_PATIENTS
    formulations = [{NAME: 'DEFAULT'}]

    fields = ["opening_balance",
              "quantity_received",
              "art_consumption",
              "loses_adjustments",
              "estimated_number_of_new_patients"]

    @timeit
    def run(self):
        scores = dict()
        formulations = self.formulations
        for formulation in formulations:
            facilities = self.report.locs
            yes = 0
            no = 0
            not_reporting = 0
            total_count = len(facilities)
            formulation_name = formulation[NAME]
            for facility in facilities:
                result = NOT_REPORTING
                facility_name = facility[NAME]
                c_records = self.report.cs[facility_name]
                a_records = self.report.ads[facility_name]
                p_records = self.report.pds[facility_name]
                cr_count = len(c_records)
                ar_count = len(a_records)
                pr_count = len(p_records)

                number_of_consumption_record_blanks = len(pydash.select(
                    values_for_records(self.fields, c_records), lambda v: v is None))
                number_of_adult_records_with_blanks = len(
                    pydash.select(values_for_records([NEW, EXISTING], a_records),
                                  lambda v: v is None))
                number_of_paed_records_with_blanks = len(
                    pydash.select(values_for_records([NEW, EXISTING], p_records),
                                  lambda v: v is None))

                number_of_blanks = number_of_adult_records_with_blanks + number_of_consumption_record_blanks + number_of_paed_records_with_blanks

                if cr_count >= 24 and ar_count >= 22 and pr_count >= 7 and number_of_blanks <= 2:
                    yes += 1
                    result = YES
                elif cr_count > 0 or ar_count > 0 or pr_count > 0 or number_of_blanks > 3:
                    no += 1
                    result = NO
                elif cr_count == 0 and ar_count == 0 and pr_count == 0:
                    not_reporting += 1
                facility['scores'][self.test][formulation_name] = result

            out = build_cycle_formulation_score(formulation_name, yes, no, not_reporting, total_count)
            scores[formulation_name] = out
        return scores
