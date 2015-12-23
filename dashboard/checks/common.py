from dashboard.models import CycleFormulationScore, Score

NOT_APPLICABLE = "DEFAULT"


class Check(object):
    test = ''

    def run(self, cycle):
        raise NotImplementedError()

    def record_result_for_facility(self, record, result, formulation_name=NOT_APPLICABLE, test=None):
        if test:
            f_test = test
        else:
            f_test = self.test
        score_record, _ = Score.objects.get_or_create(name=self.get_facility(record),
                                                      cycle=record.cycle,
                                                      district=self.get_district(record),
                                                      warehouse=self.get_warehouse(record),
                                                      ip=self.get_ip(record))

        json_value = getattr(score_record, f_test, dict())
        if json_value == '':
            json_value = dict()
        json_value[formulation_name] = result
        setattr(score_record, f_test, json_value)
        score_record.save()

    def get_ip(self, record):
        return record.facility.ip.name if record.facility.ip else ""

    def get_warehouse(self, record):
        return record.facility.warehouse.name if record.facility.warehouse  else ""

    def get_district(self, record):
        return record.facility.district.name if record.facility.district  else ""

    def get_facility(self, record):
        return record.facility.name


class CycleFormulationCheck(Check):
    def run(self, cycle):
        raise NotImplementedError()

    def build_cycle_formulation_score(self, cycle, formulation, yes, no, not_reporting, total_count):
        score, _ = CycleFormulationScore.objects.get_or_create(cycle=cycle, test=self.test, formulation=formulation)
        no_rate, not_reporting_rate, yes_rate = self.calculate_percentages(no, not_reporting, total_count, yes)
        score.yes = yes_rate
        score.no = no_rate
        score.not_reporting = not_reporting_rate
        score.save()

    def calculate_percentages(self, no, not_reporting, total_count, yes):
        if total_count > 0:
            yes_rate = float(yes * 100) / float(total_count)
            no_rate = float(no * 100) / float(total_count)
            not_reporting_rate = float(not_reporting * 100) / float(total_count)
        else:
            no_rate = not_reporting_rate = yes_rate = 0
        return no_rate, not_reporting_rate, yes_rate
