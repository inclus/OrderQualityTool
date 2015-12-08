from dashboard.checks.common import Check
from dashboard.helpers import to_date, format_range, DIFFERENT_ORDERS_OVER_TIME
from dashboard.models import FacilityCycleRecord, FacilityConsumptionRecord, CycleFormulationTestScore


def get_next_cycle(cycle):
    current_cycle_date = to_date(cycle)
    start_month = current_cycle_date.replace(months=1)
    end_month = current_cycle_date.replace(months=2)
    next_cycle = format_range(start_month, end_month)
    return next_cycle


class DifferentOrdersOverTime(Check):
    def run(self, cycle):
        next_cycle = get_next_cycle(cycle)
        formulations = [
            {"name": "TDF/3TC/EFV (Adult)", "consumption_query": "Efavirenz (TDF/3TC/EFV)"},
            {"name": "ABC/3TC (Paed)", "consumption_query": "Lamivudine (ABC/3TC) 60mg/30mg [Pack 60]"},
            {"name": "EFV200 (Paed)", "consumption_query": "EFV) 200mg [Pack 90]"}
        ]
        for formulation in formulations:
            name = formulation["consumption_query"]
            no = 0
            yes = 0
            not_reporting = 0
            total_count = FacilityCycleRecord.objects.filter(cycle=cycle).count()
            for facility_record in FacilityCycleRecord.objects.filter(cycle=cycle):
                current_values = FacilityConsumptionRecord.objects.filter(facility_cycle=facility_record, formulation__icontains=name).order_by().values('opening_balance', 'art_consumption', 'estimated_number_of_new_patients')
                new_values = FacilityConsumptionRecord.objects.filter(facility_cycle__facility=facility_record.facility, facility_cycle__cycle=next_cycle, formulation__icontains=name).order_by().values('opening_balance', 'art_consumption', 'estimated_number_of_new_patients')
                if len(current_values) == 0 or len(new_values) == 0 or not facility_record.reporting_status:
                    not_reporting += 1
                else:
                    combined_list = current_values[0].values() + new_values[0].values()
                    diff = list(set(new_values[0].values()) - set(current_values[0].values()))
                    if len(diff) > 1 or None in combined_list:
                        no += 1
                    else:
                        yes += 1
            score, _ = CycleFormulationTestScore.objects.get_or_create(cycle=cycle, test=DIFFERENT_ORDERS_OVER_TIME, formulation=name)
            yes_rate = float(yes * 100) / float(total_count)
            no_rate = float(no * 100) / float(total_count)
            not_reporting_rate = float(not_reporting * 100) / float(total_count)
            score.yes = yes_rate
            score.no = no_rate
            score.not_reporting = not_reporting_rate
            score.save()
