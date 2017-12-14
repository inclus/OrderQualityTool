require('./app.js');

require('angular-mocks/ngMock');

describe('metadataService', function () {
    beforeEach(function () {
        angular.mock.module('testDefinition')
    });

    var serivce_under_test, httpBackend;

    beforeEach(inject(['metadataService', '$httpBackend', function (metadata, $httpBackend) {
        serivce_under_test = metadata;
        httpBackend = $httpBackend;
    }]));

    describe('getConsumptionFields', function () {
        it('should get consumption fields', function () {
            httpBackend.whenGET("/api/fields/consumption").respond({
                values: ["TDF", "EFV"]
            });
            serivce_under_test.getConsumptionFields().then(function (fields) {
                expect(fields).toEqual(["TDF", "EFV"])
            });
            httpBackend.flush();
        });
    });


    describe('getPatientFields', function () {
        it('should get patient record fields', function () {
            httpBackend.whenGET("/api/fields/patients").respond({
                values: ["new", "existing"]
            });
            serivce_under_test.getPatientFields().then(function (fields) {
                expect(fields).toEqual(["new", "existing"])
            });
            httpBackend.flush();
        });
    });

    describe('getFormulations', function () {
        it('should get formulations for model', function () {
            httpBackend.whenGET("/api/formulations/adult").respond({
                values: ["abc", "def"]
            });
            serivce_under_test.getFormulations('adult').then(function (fields) {
                expect(fields).toEqual(["abc", "def"])
            });
            httpBackend.flush();
        });
    });

    describe('getAllFields', function () {
        it('should get all the fields', function () {
            httpBackend.whenGET("/api/formulations/adult").respond({
                values: ["adult_a", "adult_b"]
            });
            httpBackend.whenGET("/api/formulations/paed").respond({
                values: ["paed_a", "paed_b"]
            });
            httpBackend.whenGET("/api/formulations/consumption").respond({
                values: ["consump_a", "consump_b"]
            });
            httpBackend.whenGET("/api/fields/consumption").respond({
                values: ["closing_balance", "opening_balance"]
            });
            httpBackend.whenGET("/api/fields/patients").respond({
                values: ["new", "existing"]
            });
            httpBackend.whenGET("api/tests/tracing/consumption").respond({});
            httpBackend.whenGET("api/tests/tracing/patients").respond({});
            serivce_under_test.getAllFields().then(function (data) {
                expect(data.formulationsConsumption).toEqual(["consump_a", "consump_b"]);
                expect(data.formulationsPaed).toEqual(["paed_a", "paed_b"]);
                expect(data.formulationsAdult).toEqual(["adult_a", "adult_b"]);
                expect(data.fieldsConsumption).toEqual(["closing_balance", "opening_balance"]);
                expect(data.fieldsAdult).toEqual(["new", "existing"]);
                expect(data.fieldsPaed).toEqual(["new", "existing"]);
            });
            httpBackend.flush();
        });
    });

    describe('previewDefinition', function () {
        it('should post the definition', function () {
            httpBackend.whenPOST("/api/tests/preview").respond({
                "value": "preview"
            });
            serivce_under_test.previewDefinition({}).then(function (data) {
                expect(data).toEqual({value: 'preview'})
            });
            httpBackend.flush();
        })
    });
});