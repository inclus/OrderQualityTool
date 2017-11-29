var assert = require('assert');
var sinon = require('sinon');
var testDefinitionController = require('./test.definition.component')[2];
var fakePromise = {then: sinon.spy()};
describe('TestDefinitionController', function () {
    describe('#newGroup()', function () {
        it('should set the default group name', function () {
            controller = testDefinitionController(sinon.spy(),{getAllFields: sinon.stub().returns(fakePromise)});
            controller.definition = {groups:[]};
            assert.equal("Group 1", controller.newGroup().name);
        });
        it('should set the unique default group name', function () {
            controller = testDefinitionController(sinon.spy(),{getAllFields: sinon.stub().returns(fakePromise)});
            controller.definition = {groups:[{}]};
            assert.equal("Group 2", controller.newGroup().name);
        });
    });
});