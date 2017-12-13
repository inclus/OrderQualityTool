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

});