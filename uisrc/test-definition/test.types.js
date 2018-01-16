var models = require("./models");
var BaseTest = Object.create(null);

FacilityTest = function (metaData) {
    return {
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
        },
        id: "FacilityTwoGroups",
        name: "Facility with 2 Groups of data",
        comparisons: [
            {id: "LessThan", name:"Differ By LessThan X %"},
            {id: "AreEqual", name:"Are Equal"},
            {id: "NoNegatives", name:"Has No Negatives"},
            {id: "NoBlanks", name:"Has No Blanks"},
        ],
        cycles:
            [
                {id: "Current", name: "Current Cycle"},
                {id: "Next", name: "Next Cycle"},
                {id: "Previous", name: "Previous Cycle"}],
        calculations:
            [
                {id: "SUM", name: "Sum"},
                {id: "AVG", name: "Average"},
                {id: "VALUE", name: "Values"}
            ],
        models:
            [
                models.newModel("Adult", "Adult Records", metaData, "FacilityTwoGroups"),
                models.newModel("Paed", "Paed Records", metaData, "FacilityTwoGroups"),
                models.newModel("Consumption", "Consumption Records", metaData, "FacilityTwoGroups")
            ]
    };
};

var FacilityTestWithTracingFormulation = function (metaData) {
    var test = FacilityTest(metaData);
    test.id = "FacilityTwoGroupsAndTracingFormulation";
    test.name = "Facility with 2 Groups And Tracing Formulation";
    test.models = [
        models.newTracingModel("Adult", "Adult Records", metaData, "FacilityTwoGroupsAndTracingFormulation"),
        models.newTracingModel("Paed", "Paed Records", metaData, "FacilityTwoGroupsAndTracingFormulation"),
        models.newTracingModel("Consumption", "Consumption Records", metaData, "FacilityTwoGroupsAndTracingFormulation")
    ];
    return test;
};

var SingleGroupFacilityTest = function (metaData) {
    var test = FacilityTest(metaData);
    test.id = "FacilityOneGroup";
    test.name = "Facility with 1 Group";
    test.getGroups = function (metaData) {
        return [
            test.newGroup(1, metaData),
        ];
    };
    
    test.calculations = [
        {id: "VALUE", name: "Values"}
    ];
    
    test.comparisons = [
        {id: "NoNegatives", name:"Has No Negatives"},
        {id: "NoBlanks", name:"Has No Blanks"},
    ];
    return test;
};

var getTypeFromJson = function (metaData, typeData) {
    if (typeData.id === "FacilityTwoGroups") {
        return FacilityTest(metaData);
    }
    if (typeData.id === "FacilityTwoGroupsAndTracingFormulation") {
        return FacilityTestWithTracingFormulation(metaData);
    }

    if (typeData.id === "FacilityOneGroup") {
        return SingleGroupFacilityTest(metaData);
    }
};

var buildDefinition = function (inputValue, metaData) {
    var definition = JSON.parse(inputValue);
    definition.type = getTypeFromJson(metaData, definition.type);
    return definition;
};

module.exports = {
    FacilityTest: FacilityTest,
    FacilityTestWithTracingFormulation: FacilityTestWithTracingFormulation,
    SingleGroupFacilityTest: SingleGroupFacilityTest,
    buildDefinition: buildDefinition
};