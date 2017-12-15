var models = require("./models");
var BaseTest = Object.create(null);

BaseTest.prototype = {
    newGroup:
        function (groupNumber) {
            return {
                cycle: this.cycles[0],
                model: this.models[0],
                aggregation: this.calculations[0],
                selected_fields: [],
                selected_formulations: [],
                name: "G" + groupNumber
            };

        },
    getGroups: function (metaData) {
        return [
            this.newGroup(1, metaData),
            this.newGroup(2, metaData)
        ];
    }
};
var FacilityTest = function (metaData) {
    return Object.create(BaseTest.prototype, {
        id: {
            value: "FacilityTwoGroups",
            writable: true,
            enumerable: true
        },
        name: {
            value: "Facility with 2 Groups of data",
            writable: true,
            enumerable: true
        },
        cycles: {
            value:
                [
                    {id: "Current", name: "Current Cycle"},
                    {id: "Next", name: "Next Cycle"},
                    {id: "Previous", name: "Previous Cycle"}
                ],
            enumerable: true

        },
        calculations: {
            value: [
                {id: "SUM", name: "Sum"},
                {id: "AVG", name: "Average"}
            ],
            enumerable: true

        },
        models: {
            value: [
                models.newModel("Adult", "Adult Records", metaData),
                models.newModel("Paed", "Paed Records", metaData),
                models.newModel("Consumption", "Consumption Records", metaData)
            ],
            enumerable: true,
            writable: true
        }

    });
};

var FacilityTestWithTracingFormulation = function (metaData) {
    return Object.create(FacilityTest(metaData), {
        id: {
            value: "FacilityTwoGroupsAndTracingFormulation",
            writable: true,
            enumerable: true
        },
        name: {
            value: "Facility with 2 Groups And Tracing Formulation",
            writable: true,
            enumerable: true
        },
        models: {
            value: [
                models.newTracingModel("Adult", "Adult Records", metaData),
                models.newTracingModel("Paed", "Paed Records", metaData),
                models.newTracingModel("Consumption", "Consumption Records", metaData)
            ],
            writable: true,
            enumerable: true
        }
    });
};

var getTypeFromJson = function (metaData, typeData) {
    if (typeData.id === "FacilityTwoGroups") {
        return FacilityTest(metaData);
    }
    if (typeData.id === "FacilityTwoGroupsAndTracingFormulation") {
        return FacilityTestWithTracingFormulation(metaData);
    }
};

var buildDefinition = function (inputValue, metaData) {
    var definition = JSON.parse(inputValue);
    definition.type = getTypeFromJson(metaData, definition.type);
    if (definition.groups) {
        definition.groups.forEach(function (group) {
            group.model = models.newModel(group.model.id, group.model.name, metaData);
        });
    }
    return definition;
};

module.exports = {
    FacilityTest: FacilityTest,
    FacilityTestWithTracingFormulation: FacilityTestWithTracingFormulation,
    buildDefinition: buildDefinition
};