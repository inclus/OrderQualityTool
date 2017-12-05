var assert = require('assert');
var sinon = require('sinon');
var testDefinitionController = require('./test.definition.component')[2];
var fakePromise = {then: sinon.spy()};
describe('TestDefinitionController', function () {
    describe('#newGroup()', function () {
        it('should set the default group name', function () {
            controller = testDefinitionController(sinon.spy(), {getAllFields: sinon.stub().returns(fakePromise)});
            controller.definition = {groups: []};
            assert.equal("G1", controller.newGroup().name);
        });
        it('should set the unique default group name', function () {
            controller = testDefinitionController(sinon.spy(), {getAllFields: sinon.stub().returns(fakePromise)});
            controller.definition = {groups: [{}]};
            assert.equal("G2", controller.newGroup().name);
        });
    });

    describe('main_regex', function () {
        var scenarios = [
            {test: "G1 < 5", match: true},
            {test: "G1 2", match: false},
            {test: "G1", match: false},
            {test: "LJAJK", match: false},
            {test: "LJAJK", match: false},
            {test: "LJAJK", match: false},
            {test: "G1 < 0.13", match: true},
            {test: "G1 * 5 > 10", match: true},
            {test: "G1 * 5.192 > 10", match: true},
            {test: "G1 * 0.192 > 10", match: true},
            {test: "G1 * 0.192 >= 10", match: true},
            {test: "G1 > 0.434 * 10", match: true},
            {test: "G1 < G2", match: true},
            {test: "G1 <= G2", match: true},
            {test: "G1 <= G101", match: false},
            {test: "G1 < 5", match: true},
            {test: "G1 < 5", match: true},
            {test: "G1 < 5", match: true},
        ];
        scenarios.forEach(function (scenario) {
            var test = 'should check input' + scenario.test;
            it(test,  function () {
                controller = testDefinitionController(sinon.spy(), {getAllFields: sinon.stub().returns(fakePromise)});
                match = controller.main_regex.exec(scenario.test)
                assert.equal(scenario.match, match != null);
            });
        })


    });
});