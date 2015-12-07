from django.test import TestCase

from dashboard.checks.different_orders_over_time import get_next_cycle, DifferentOrdersOverTime
from dashboard.helpers import DIFFERENT_ORDERS_OVER_TIME
from dashboard.models import FacilityCycleRecord, FacilityConsumptionRecord, CycleFormulationTestScore
from locations.models import Facility


class DifferentOrdersOverTimeTestCase(TestCase):
    def test_gen_next_cycle(self):
        values = [('Jan - Feb 2013', 'Mar - Apr 2013'), ('Nov - Dec 2013', 'Jan - Feb 2014'), ('Mar - Apr 2014', 'May - Jun 2014')]
        for v in values:
            self.assertEqual(get_next_cycle(v[0]), v[1])

    def test_check(self):
        names = ["FA1", "FA2", "FA3"]
        names_without_data = ["FA4", "FA5"]
        consumption_regimens = ["CREG-%s" % n for n in range(1, 26)]
        cycles = ["Jan - Feb 2013", "Mar - Apr 2013"]
        consumption_data = {}
        consumption_data['opening_balance'] = 3
        consumption_data['quantity_received'] = 4.5
        consumption_data['pmtct_consumption'] = 4.5
        consumption_data['art_consumption'] = 4.5
        consumption_data['loses_adjustments'] = 4.5
        consumption_data['closing_balance'] = 4.5
        consumption_data['months_of_stock_of_hand'] = 4
        consumption_data['quantity_required_for_current_patients'] = 4.5
        consumption_data['estimated_number_of_new_patients'] = 4.5
        consumption_data['estimated_number_of_new_pregnant_women'] = 4.5
        consumption_data['total_quantity_to_be_ordered'] = 4.5
        consumption_data['notes'] = None
        i = 0
        for cycle in cycles:
            for name in names:
                facility, _ = Facility.objects.get_or_create(name=name)
                record, _ = FacilityCycleRecord.objects.get_or_create(cycle=cycle, facility=facility, reporting_status=True)
                consumption_data['facility_cycle'] = record
                for reg in consumption_regimens:
                    consumption_data['formulation'] = reg
                    FacilityConsumptionRecord.objects.create(**consumption_data)

            for name in names_without_data:
                facility, _ = Facility.objects.get_or_create(name=name)
                record, _ = FacilityCycleRecord.objects.get_or_create(cycle=cycle, facility=facility, reporting_status=True)
            i += 1

        DifferentOrdersOverTime().run(cycles[0])
        score = CycleFormulationTestScore.objects.filter(test=DIFFERENT_ORDERS_OVER_TIME, cycle=cycles[0])[0]
        self.assertEquals(score.yes, 60.0)
        self.assertEquals(score.no, 0.0)
        self.assertEquals(score.not_reporting, 40.0)
