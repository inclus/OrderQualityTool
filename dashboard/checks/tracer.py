import attr

from dashboard.models import TracingFormulations


@attr.s()
class Tracer(object):
    key = attr.ib()
    consumption_formulations = attr.ib(default=None)
    patient_formulations = attr.ib(default=None)
    extras = attr.ib(default={})

    @staticmethod
    def from_tracing_formulation(formulation):
        return Tracer(
            key=formulation.slug,
            consumption_formulations=formulation.consumption_formulations,
            patient_formulations=formulation.patient_formulations,
            extras=None,
        )

    def with_data(self, data):
        self.extras = data
        return self

    @staticmethod
    def from_dict(data):
        if data and "slug" in data:
            return Tracer(
                key=data.get("slug"),
                consumption_formulations=data.get("consumption_formulations"),
                patient_formulations=data.get("patient_formulations"),
            )

    @staticmethod
    def from_db():
        return [Tracer.F1(), Tracer.F2(), Tracer.F3()]

    @staticmethod
    def F1():
        return Tracer.from_tracing_formulation(TracingFormulations.get_tdf_adult())

    @staticmethod
    def F2():
        return Tracer.from_tracing_formulation(TracingFormulations.get_abc_paed())

    @staticmethod
    def F3():
        return Tracer.from_tracing_formulation(TracingFormulations.get_efv_paed())

    @staticmethod
    def Default():
        return Tracer(
            key="DEFAULT",
            consumption_formulations=None,
            patient_formulations=None,
            extras=None,
        )
