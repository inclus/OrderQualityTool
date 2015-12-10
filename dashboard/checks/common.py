from dashboard.models import CycleFormulationTestScore


class Check(object):
    def run(self, cycle):
        raise NotImplementedError()


class CycleFormulationCheck(Check):
    test = ''

    def run(self, cycle):
        raise NotImplementedError()

    def build_cycle_formulation_score(self, cycle, formulation, yes, no, not_reporting, total_count):
        score, _ = CycleFormulationTestScore.objects.get_or_create(cycle=cycle, test=self.test, formulation=formulation)
        no_rate, not_reporting_rate, yes_rate = self.calculate_percentages(no, not_reporting, total_count, yes)
        score.yes = yes_rate
        score.no = no_rate
        score.not_reporting = not_reporting_rate
        score.save()

    def calculate_percentages(self, no, not_reporting, total_count, yes):
        yes_rate = float(yes * 100) / float(total_count)
        no_rate = float(no * 100) / float(total_count)
        not_reporting_rate = float(not_reporting * 100) / float(total_count)
        return no_rate, not_reporting_rate, yes_rate
