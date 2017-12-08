require('./app.js');

require('angular-mocks/ngMock');

var withSuccessfulPromise = function ($q, result) {
    return function () {
        var deferred = $q.defer();
        deferred.resolve(result);
        return deferred.promise;
    }
};
describe('testDefinition component', function () {
    beforeEach(function () {
        angular.mock.module('testDefinition')
    });

    var element, scope, metadataService;

    beforeEach(inject(function ($rootScope, $compile, _metadataService_, $q) {
        metadataService = _metadataService_;
        var fakeData = {
            consumption_fields: ["closing_balance", "opening_balance"],
            patient_fields: ["new", "existing"],
            formulations_adult: ["form_adult"],
            formulations_paed: ["form_paed"],
            formulations_consumption: ["form_consump"]
        };
        spyOn(metadataService, "getAllFields").and.callFake(withSuccessfulPromise($q, fakeData));
        scope = $rootScope.$new();
        var rawElement = angular.element('<test-definition></test-definition>');
        element = $compile(rawElement)(scope);
        scope.$apply();
    }));

    describe('reset', function () {
        it('should add two groups', function () {
            controller = element.controller('testDefinition');
            controller.definition = {};
            controller.reset();
            expect(controller.definition.groups.length).toEqual(2);
            expect(controller.definition.groups[0].name).toEqual('G1');
            expect(controller.definition.groups[1].name).toEqual('G2');
        });
    });

    describe('setFields', function () {
        it('should set the fields to consumption if the selected model is consumption', function () {
            controller = element.controller('testDefinition');
            expect(controller.fields[1]).toEqual(['new', 'existing']);
            controller.setFields(1, {id: "Consumption"});
            expect(controller.fields[1]).toEqual(['closing_balance', 'opening_balance']);
        });

        it('should set the fields to patients if the selected model is paed', function () {
            controller = element.controller('testDefinition');
            expect(controller.fields[1]).toEqual(['new', 'existing']);
            controller.setFields(1, {id: "Paed"});
            expect(controller.fields[1]).toEqual(['new', 'existing']);
        });

        it('should set the fields to patients if the selected model is adult', function () {
            controller = element.controller('testDefinition');
            expect(controller.fields[1]).toEqual(['new', 'existing']);
            controller.setFields(1, {id: "Adult"});
            expect(controller.fields[1]).toEqual(['new', 'existing']);
        });


        it('should set the formulations to paed_formulations if the selected model is paed', function () {
            controller = element.controller('testDefinition');
            expect(controller.formulations[1]).toEqual(['form_adult']);
            controller.setFields(1, {id: "Paed"});
            expect(controller.formulations[1]).toEqual(['form_paed']);
        });

        it('should set the formulations to adult_formulations if the selected model is adult', function () {
            controller = element.controller('testDefinition');
            expect(controller.formulations[1]).toEqual(['form_adult']);
            controller.setFields(1, {id: "Adult"});
            expect(controller.formulations[1]).toEqual(['form_adult']);
        });

        it('should set the formulations to consumption_formulations if the selected model is consumption', function () {
            controller = element.controller('testDefinition');
            expect(controller.formulations[1]).toEqual(['form_adult']);
            controller.setFields(1, {id: "Consumption"});
            expect(controller.formulations[1]).toEqual(['form_consump']);
        });
    });


});