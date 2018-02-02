var chartsController = ["$scope", "chartsService", function ($scope, chartsService) {
    var ctrl = this;
    ctrl.select = function (test) {
        ctrl.selectedTest = test;
        var regimen = null;
        if (ctrl.selectedRegimen) {
            regimen = ctrl.selectedRegimen.name;
        }
        chartsService.buildOptions(test, ctrl.selectedDistrict, ctrl.selectedIp, ctrl.selectedWarehouse, ctrl.startCycle, ctrl.endCycle, regimen).then(function (options) {
            ctrl.options = options;
        });

        if (test.sampled) {
            ctrl.selectedRegimen = test.regimens[0];
        } else {
            ctrl.selectedRegimen = null;
        }

    };
    chartsService.getTests().then(function (data) {
        ctrl.featuredTests = data.featured;
        ctrl.otherTests = data.other;
        ctrl.select(data.featured[0]);
    });

    $scope.$watchGroup(
        ["ctrl.selectedDistrict",
            "ctrl.selectedIp",
            "ctrl.selectedWarehouse",
            "ctrl.startCycle",
            "ctrl.endCycle",
            "ctrl.selectedRegimen"], function (newValues) {
            chartsService.getMetrics({
                district: newValues[0],
                ip: newValues[1],
                warehouse: newValues[2]
            }).then(function (metrics) {
                ctrl.featuredTests.forEach(function (test) {
                    test.metric = metrics[test.name];
                });
            });
            if (ctrl.selectedTest) {
                chartsService.buildOptions(
                    ctrl.selectedTest,
                    ctrl.selectedDistrict,
                    ctrl.selectedIp,
                    ctrl.selectedWarehouse,
                    ctrl.startCycle,
                    ctrl.endCycle,
                    ctrl.selectedRegimen).then(function (options) {
                    ctrl.options = options;
                });
            }
        });

    return ctrl;
}];
var init = function (module) {
    module.component("qdbCharts", {
        template: require("./charts.html"),
        controller: chartsController,
        controllerAs: "ctrl",
        bindings: {
            startCycle: "=",
            endCycle: "=",
            selectedIp: "=",
            selectedWarehouse: "=",
            selectedDistrict: "="
        }
    });
};
module.exports = init;