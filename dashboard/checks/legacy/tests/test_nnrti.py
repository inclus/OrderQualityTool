from unittest import TestCase

from parameterized import parameterized

from dashboard.checks.legacy.nn import NNRTIADULTSCheck, NNRTIPAEDCheck
from dashboard.data.entities import LocationData
from dashboard.helpers import NOT_REPORTING, YES, C_RECORDS, FORMULATION, NO, \
    COMBINED_CONSUMPTION

has_no_data = LocationData.migrate_from_dict({})
current_adult_initial = LocationData.migrate_from_dict({
    C_RECORDS: [
        {
            COMBINED_CONSUMPTION: 10,
            FORMULATION: "Zidovudine/Lamivudine (AZT/3TC) 300mg/150mg [Pack 60]"
        },
        {
            COMBINED_CONSUMPTION: 10,
            FORMULATION: "Tenofovir/Lamivudine (TDF/3TC) 300mg/300mg [Pack 30]"
        },
        {
            COMBINED_CONSUMPTION: 10,
            FORMULATION: "Abacavir/Lamivudine (ABC/3TC) 600mg/300mg [Pack 30]"
        },
        {
            COMBINED_CONSUMPTION: 10,
            FORMULATION: "Efavirenz (EFV) 600mg [Pack 30]"
        },
        {
            COMBINED_CONSUMPTION: 10,
            FORMULATION: "Nevirapine (NVP) 200mg [Pack 60]"
        },
        {
            COMBINED_CONSUMPTION: 10,
            FORMULATION: "Atazanavir/Ritonavir (ATV/r) 300mg/100mg [Pack 30]"
        }, {
            COMBINED_CONSUMPTION: 10,
            FORMULATION: "Lopinavir/Ritonavir (LPV/r) 200mg/50mg [Pack 120]"
        },
    ]
})
current_adult_all_zero = LocationData.migrate_from_dict({
    C_RECORDS: [
        {
            COMBINED_CONSUMPTION: 0,
            FORMULATION: "Zidovudine/Lamivudine (AZT/3TC) 300mg/150mg [Pack 60]"
        },
        {
            COMBINED_CONSUMPTION: 0,
            FORMULATION: "Tenofovir/Lamivudine (TDF/3TC) 300mg/300mg [Pack 30]"
        },
        {
            COMBINED_CONSUMPTION: 0,
            FORMULATION: "Abacavir/Lamivudine (ABC/3TC) 600mg/300mg [Pack 30]"
        },
        {
            COMBINED_CONSUMPTION: 0,
            FORMULATION: "Efavirenz (EFV) 600mg [Pack 30]"
        },
        {
            COMBINED_CONSUMPTION: 0,
            FORMULATION: "Nevirapine (NVP) 200mg [Pack 60]"
        },
        {
            COMBINED_CONSUMPTION: 0,
            FORMULATION: "Atazanavir/Ritonavir (ATV/r) 300mg/100mg [Pack 30]"
        }, {
            COMBINED_CONSUMPTION: 0,
            FORMULATION: "Lopinavir/Ritonavir (LPV/r) 200mg/50mg [Pack 120]"
        },
    ]
})
current_adult_either_all_blank = LocationData.migrate_from_dict({
    C_RECORDS: [
        {
            COMBINED_CONSUMPTION: None,
            FORMULATION: "Zidovudine/Lamivudine (AZT/3TC) 300mg/150mg [Pack 60]"
        },
        {
            COMBINED_CONSUMPTION: None,
            FORMULATION: "Tenofovir/Lamivudine (TDF/3TC) 300mg/300mg [Pack 30]"
        },
        {
            COMBINED_CONSUMPTION: None,
            FORMULATION: "Abacavir/Lamivudine (ABC/3TC) 600mg/300mg [Pack 30]"
        },
        {
            COMBINED_CONSUMPTION: 0,
            FORMULATION: "Efavirenz (EFV) 600mg [Pack 30]"
        },
        {
            COMBINED_CONSUMPTION: 0,
            FORMULATION: "Nevirapine (NVP) 200mg [Pack 60]"
        },
        {
            COMBINED_CONSUMPTION: 0,
            FORMULATION: "Atazanavir/Ritonavir (ATV/r) 300mg/100mg [Pack 30]"
        }, {
            COMBINED_CONSUMPTION: 0,
            FORMULATION: "Lopinavir/Ritonavir (LPV/r) 200mg/50mg [Pack 120]"
        },
    ]
})
current_adult_2 = LocationData.migrate_from_dict({
    C_RECORDS: [
        {
            COMBINED_CONSUMPTION: 10,
            FORMULATION: "Zidovudine/Lamivudine (AZT/3TC) 300mg/150mg [Pack 60]"
        },
        {
            COMBINED_CONSUMPTION: 10,
            FORMULATION: "Tenofovir/Lamivudine (TDF/3TC) 300mg/300mg [Pack 30]"
        },
        {
            COMBINED_CONSUMPTION: 10,
            FORMULATION: "Abacavir/Lamivudine (ABC/3TC) 600mg/300mg [Pack 30]"
        },
        {
            COMBINED_CONSUMPTION: 5,
            FORMULATION: "Efavirenz (EFV) 600mg [Pack 30]"
        },
        {
            COMBINED_CONSUMPTION: 5,
            FORMULATION: "Nevirapine (NVP) 200mg [Pack 60]"
        },
        {
            COMBINED_CONSUMPTION: 5,
            FORMULATION: "Atazanavir/Ritonavir (ATV/r) 300mg/100mg [Pack 30]"
        }, {
            COMBINED_CONSUMPTION: 5,
            FORMULATION: "Lopinavir/Ritonavir (LPV/r) 200mg/50mg [Pack 120]"
        },
    ]
})

current_paed_initial = LocationData.migrate_from_dict({
    C_RECORDS: [
        {
            COMBINED_CONSUMPTION: 38,
            FORMULATION: "Abacavir/Lamivudine (ABC/3TC) 60mg/30mg [Pack 60]"
        },
        {
            COMBINED_CONSUMPTION: 38,
            FORMULATION: "Zidovudine/Lamivudine (AZT/3TC) 60mg/30mg [Pack 60]"
        },
        {
            COMBINED_CONSUMPTION: 10,
            FORMULATION: "Efavirenz (EFV) 200mg [Pack 90]"
        },
        {
            COMBINED_CONSUMPTION: 10,
            FORMULATION: "Nevirapine (NVP) 50mg [Pack 60]"
        },
        {
            COMBINED_CONSUMPTION: 10,
            FORMULATION: "Lopinavir/Ritonavir (LPV/r) 80mg/20ml oral susp [Bottle 60ml]"
        },
        {
            COMBINED_CONSUMPTION: 10,
            FORMULATION: "Lopinavir/Ritonavir (LPV/r) 100mg/25mg"
        }
    ]
})
current_paed_all_zero = LocationData.migrate_from_dict({
    C_RECORDS: [
        {
            COMBINED_CONSUMPTION: 0,
            FORMULATION: "Abacavir/Lamivudine (ABC/3TC) 60mg/30mg [Pack 60]"
        },
        {
            COMBINED_CONSUMPTION: 0,
            FORMULATION: "Zidovudine/Lamivudine (AZT/3TC) 60mg/30mg [Pack 60]"
        },
        {
            COMBINED_CONSUMPTION: 0,
            FORMULATION: "Efavirenz (EFV) 200mg [Pack 90]"
        },
        {
            COMBINED_CONSUMPTION: 0,
            FORMULATION: "Nevirapine (NVP) 50mg [Pack 60]"
        },
        {
            COMBINED_CONSUMPTION: 0,
            FORMULATION: "Lopinavir/Ritonavir (LPV/r) 80mg/20ml oral susp [Bottle 60ml]"
        },
        {
            COMBINED_CONSUMPTION: 0,
            FORMULATION: "Lopinavir/Ritonavir (LPV/r) 100mg/25mg"
        }
    ]
})

current_paed_either_all_blank = LocationData.migrate_from_dict({
    C_RECORDS: [
        {
            COMBINED_CONSUMPTION: None,
            FORMULATION: "Abacavir/Lamivudine (ABC/3TC) 60mg/30mg [Pack 60]"
        },
        {
            COMBINED_CONSUMPTION: None,
            FORMULATION: "Zidovudine/Lamivudine (AZT/3TC) 60mg/30mg [Pack 60]"
        },
        {
            COMBINED_CONSUMPTION: None,
            FORMULATION: "Efavirenz (EFV) 200mg [Pack 90]"
        },
        {
            COMBINED_CONSUMPTION: None,
            FORMULATION: "Nevirapine (NVP) 50mg [Pack 60]"
        },
        {
            COMBINED_CONSUMPTION: None,
            FORMULATION: "Lopinavir/Ritonavir (LPV/r) 80mg/20ml oral susp [Bottle 60ml]"
        },
        {
            COMBINED_CONSUMPTION: None,
            FORMULATION: "Lopinavir/Ritonavir (LPV/r) 100mg/25mg"
        }
    ]
})


class NNRTICURRENTADULTSCheckTestCase(TestCase):
    @parameterized.expand([
        ("no data", has_no_data, NOT_REPORTING),
        ("> 0.7 < 1.429", current_adult_initial, YES),
        ("all zero", current_adult_all_zero, YES),
        ("either all blank", current_adult_either_all_blank, NO),
        ("> 1.429", current_adult_2, NO),
    ])
    def test_check(self, name, data, expected):
        check = NNRTIADULTSCheck()
        result = check.for_each_facility(data, check.combinations[0])
        self.assertEquals(result, expected)


class NNRTIPAEDCheckTestCase(TestCase):
    @parameterized.expand([
        ("no data", has_no_data, NOT_REPORTING),
        ("> 0.7 < 1.429", current_paed_initial, YES),
        ("all zero", current_paed_all_zero, YES),
        ("either all blank", current_paed_either_all_blank, NO),
    ])
    def test_check(self, name, data, expected):
        check = NNRTIPAEDCheck()
        result = check.for_each_facility(data, check.combinations[0])
        self.assertEquals(result, expected)
