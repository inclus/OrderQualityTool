from dashboard.models import AdultPatientsRecord, PAEDPatientsRecord, Consumption


def gen_adult_record(
    name="loc1",
    district="dis1",
    formulation="form_a",
    cycle="cycle1",
    existing=12,
    new=1,
):
    AdultPatientsRecord.objects.create(
        name=name,
        district=district,
        formulation=formulation,
        existing=existing,
        new=new,
        cycle=cycle,
    )


def gen_paed_record(
    name="loc1",
    district="dis1",
    formulation="form_a",
    cycle="cycle1",
    existing=20,
    new=10,
):
    PAEDPatientsRecord.objects.create(
        name=name,
        district=district,
        formulation=formulation,
        existing=existing,
        new=new,
        cycle=cycle,
    )


def gen_consumption_record(
    name="loc1", district="dis1", formulation="form_a", cycle="cycle1", **fields
):
    Consumption.objects.create(
        name=name, district=district, formulation=formulation, cycle=cycle, **fields
    )
