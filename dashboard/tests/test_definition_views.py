from json import loads

from django_webtest import WebTest

from dashboard.tests.fake_definition import FakeDefinition, gen_adult_record, gen_paed_record, gen_consumption_record
from hamcrest import *


class PreviewLocationsViewTestCase(WebTest):
    def test_that_only_locations_with_data_show_up(self):
        url = "/api/tests/preview/locations"
        gen_adult_record()
        gen_adult_record(cycle="cycle2")
        gen_adult_record(name="loc2", cycle="cycle2")
        gen_adult_record(name="loc3", cycle="cycle3", existing=None, new=None)
        params = FakeDefinition().initial().get()
        response = self.app.post_json(url, user="testuser", params=params)
        json_response = response.content.decode('utf8')
        self.assertEqual(200, response.status_code)
        locations = loads(json_response).get('locations', [])
        self.assertEqual(2, len(locations))
        assert_that(locations, has_item(has_entries(
            {
                "name": equal_to("loc1"),
                "district": equal_to("dis1"),
                "cycles": equal_to(["cycle1", "cycle2"])
            }
        )))

        assert_that(locations, has_item(has_entries(
            {
                "name": equal_to("loc2"),
                "district": equal_to("dis1"),
                "cycles": equal_to(["cycle2"])
            }
        )))


class PreviewViewTestCase(WebTest):
    url = "/api/tests/preview"

    def test_that_a_sample_is_required(self):
        response = self.app.post_json(self.url, user="testuser", params=FakeDefinition().initial().get(),
                                      expect_errors=True)
        json_response = loads(response.content.decode('utf8'))
        self.assertEqual(400, response.status_code)
        assert_that(json_response, has_entry(equal_to("sample"), has_item(equal_to("This field is required."))))

    def test_that_the_factors_are_considered(self):
        gen_paed_record()
        params = FakeDefinition().sampled().model('Paed').factors(existing=2, new=5).get()
        response = self.app.post_json(self.url, user="testuser", params=params, expect_errors=True)
        json_response = loads(response.content.decode('utf8'))
        self.assertEqual(200, response.status_code)
        assert_that(json_response, has_entry(equal_to("groups"), has_item(
            has_entries(
                {
                    "name": equal_to('G1'),
                    "aggregation": "SUM",
                    "values": equal_to([['form_a', 10.0, 20.0]]),
                    "factored_values": equal_to([['form_a', 50.0, 40.0]]),
                    "headers": equal_to(['new', 'existing']),
                    "result": equal_to(90.0)
                }
            )
        )))

    def test_result_with_paed_records(self):
        gen_paed_record()
        params = FakeDefinition().sampled().model('Paed').get()
        response = self.app.post_json(self.url, user="testuser", params=params, expect_errors=True)
        json_response = loads(response.content.decode('utf8'))
        self.assertEqual(200, response.status_code)
        assert_that(json_response, has_entry(equal_to("groups"), has_item(
            has_entries(
                {
                    "name": equal_to('G1'),
                    "aggregation": "SUM",
                    "values": equal_to([['form_a', 10.0, 20.0]]),
                    "factored_values": equal_to([['form_a', 10.0, 20.0]]),
                    "headers": equal_to(['new', 'existing']),
                    "result": equal_to(30.0)
                }
            )
        )))

    def test_result_with_adult_records(self):
        gen_adult_record()
        params = FakeDefinition().sampled().get()
        response = self.app.post_json(self.url, user="testuser", params=params, expect_errors=True)
        json_response = loads(response.content.decode('utf8'))
        self.assertEqual(200, response.status_code)
        assert_that(json_response, has_entry(equal_to("groups"), has_item(
            has_entries(
                {
                    "name": equal_to('G1'),
                    "aggregation": "SUM",
                    "values": equal_to([['form_a', 1.0, 12.0]]),
                    "factored_values": equal_to([['form_a', 1.0, 12.0]]),
                    "headers": equal_to(['new', 'existing']),
                    "result": equal_to(13.0)
                }
            )
        )))

    def test_result_with_consumption_records(self):
        gen_consumption_record(opening_balance=10, closing_balance=20)
        params = FakeDefinition().sampled().fields("opening_balance", "closing_balance").model('Consumption').factors(
            opening_balance=1, closing_balance=10).get()
        response = self.app.post_json(self.url, user="testuser", params=params, expect_errors=True)
        json_response = loads(response.content.decode('utf8'))

        self.assertEqual(200, response.status_code)
        assert_that(json_response, has_entry(equal_to("groups"), has_item(
            has_entries(
                {
                    "name": equal_to('G1'),
                    "aggregation": "SUM",
                    "values": equal_to([['form_a', 10.0, 20.0]]),
                    "factored_values": equal_to([['form_a', 10.0, 200.0]]),
                    "headers": equal_to(['opening_balance', 'closing_balance']),
                    "result": equal_to(210.0)
                }
            )
        )))

    def test_two_facility_with_tracing_type(self):
        gen_consumption_record(formulation="form_tra", opening_balance=10, closing_balance=20)
        params = FakeDefinition().traced(tracer={"name": "trace1", "formulations": ["form_tra", "form_trb"]}).model(
            'Consumption').tracing_formulations("form_tra",
                                                "form_trb").fields(
            "opening_balance", "closing_balance").get()
        response = self.app.post_json(self.url, user="testuser", params=params, expect_errors=True)
        json_response = loads(response.content.decode('utf8'))

        self.assertEqual(200, response.status_code)
        assert_that(json_response, has_entry(equal_to("groups"), has_item(
            has_entries(
                {
                    "name": equal_to('G1'),
                    "aggregation": "SUM",
                    "values": equal_to([['form_tra', 10.0, 20.0]]),
                    "factored_values": equal_to([['form_tra', 10.0, 20.0]]),
                    "headers": equal_to(['opening_balance', 'closing_balance']),
                    "result": equal_to(30.0)
                }
            )
        )))

    def test_greater_than(self):
        gen_consumption_record(formulation="form1", opening_balance=10, closing_balance=20)
        gen_consumption_record(formulation="form2", opening_balance=40, closing_balance=30)
        definition_builder = FakeDefinition().sampled().formulations("form1", "form2")
        definition_builder.fields("opening_balance", "closing_balance")
        definition_builder.model('Consumption')
        definition_builder.is_greater_than(0.5)
        response = self.app.post_json(self.url, user="testuser", params=definition_builder.get(), expect_errors=True)
        json_response = loads(response.content.decode('utf8'))

        self.assertEqual(200, response.status_code)
        assert_that(json_response, has_entry(equal_to("groups"), has_item(
            has_entries(
                {
                    "name": equal_to('G1'),
                    "aggregation": "SUM",
                    "values": equal_to([['form1', 10.0, 20.0], ['form2', 40.0, 30.0]]),
                    "headers": equal_to(['opening_balance', 'closing_balance']),
                    "result": equal_to(100.0)
                }

            )
        )))
        assert_that(json_response, has_entry(equal_to("groups"), has_item(
            has_entries(
                {
                    "name": equal_to('G2'),
                    "aggregation": "SUM",
                    "values": equal_to([['form1', 10.0, 20.0], ['form2', 40.0, 30.0]]),
                    "headers": equal_to(['opening_balance', 'closing_balance']),
                    "result": equal_to(100.0)
                }

            )
        )))

        assert_that(json_response, has_entry(equal_to("result"), has_entries({"DEFAULT": equal_to("YES")})))

    def test_less_than(self):
        gen_consumption_record(formulation="form1", opening_balance=10, closing_balance=20)
        gen_consumption_record(formulation="form2", opening_balance=40, closing_balance=30)
        definition_builder = FakeDefinition().sampled().formulations("form1", "form2")
        definition_builder.fields("opening_balance", "closing_balance")
        definition_builder.model('Consumption')
        definition_builder.is_less_than(0.5)
        response = self.app.post_json(self.url, user="testuser", params=definition_builder.get(), expect_errors=True)
        json_response = loads(response.content.decode('utf8'))

        self.assertEqual(200, response.status_code)
        assert_that(json_response, has_entry(equal_to("groups"), has_item(
            has_entries(
                {
                    "name": equal_to('G1'),
                    "aggregation": "SUM",
                    "values": equal_to([['form1', 10.0, 20.0], ['form2', 40.0, 30.0]]),
                    "headers": equal_to(['opening_balance', 'closing_balance']),
                    "result": equal_to(100.0)
                }

            )
        )))
        assert_that(json_response, has_entry(equal_to("groups"), has_item(
            has_entries(
                {
                    "name": equal_to('G2'),
                    "aggregation": "SUM",
                    "values": equal_to([['form1', 10.0, 20.0], ['form2', 40.0, 30.0]]),
                    "headers": equal_to(['opening_balance', 'closing_balance']),
                    "result": equal_to(100.0)
                }

            )
        )))

        assert_that(json_response, has_entry(equal_to("result"), has_entries({"DEFAULT": equal_to("NO")})))
