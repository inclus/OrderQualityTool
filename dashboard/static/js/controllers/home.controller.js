angular.module('dashboard').controller('HomeController', ['$scope', '$stateParams', '$uibModal', '$http',
    function($scope, $stateParams, $uibModal, $http) {

        $scope.displayCycle = function(cycle) {
            return "CYCLE " + cycle.number + " '" + cycle.year;
        };
        $scope.bestPerforming = 'District';
        $scope.selectBest = function(name) {
            $scope.bestPerforming = name;
        };

        $scope.worstPerforming = 'District';
        $scope.selectWorst = function(name) {
            $scope.worstPerforming = name;
        };
        $http.get('/api/cycles').then(function(response) {
            $scope.cycles = response.data.values;
            $scope.startCycle = $scope.cycles[6 - 1];
            $scope.endCycle = $scope.selectedCycle = response.data.most_recent_cycle;
            console.log('cycle', $scope.endCycle, $scope.selectedCycle);
        });

        $scope.$watch('startCycle', function(start) {
            if (start) {
                var pos = _.findIndex($scope.cycles, function(item) {
                    return item == start;
                });
                $scope.endCycles = $scope.cycles.slice(0, pos + 1);
            }

        }, true);

        var updateWorstList = function() {
            $http.get('/api/test/reportingRate/worstDistricts', {
                params: {
                    level: $scope.worstPerforming,
                    cycle: $scope.selectedCycle
                }
            }).then(function(response) {
                $scope.worstDistricts = response.data.values;
            });
        };

        var updateBestList = function() {
            $http.get('/api/test/reportingRate/bestDistricts', {
                params: {
                    level: $scope.bestPerforming,
                    cycle: $scope.selectedCycle
                }
            }).then(function(response) {
                $scope.bestDistricts = response.data.values;
            });
        };

        $scope.$watch('selectedCycle', function(cycle) {
            if (cycle) {
                updateWorstList();
                updateBestList();
            }
        });

        $scope.$watch('bestPerforming', function() {
            updateBestList();
        });


        $scope.$watch('worstPerforming', function() {
            updateWorstList();
        });

        $scope.currentTest = $stateParams.name;
        var templates = {
            "reportingRate": "/static/views/reporting_rate.html",
            "webVsPaper": "/static/views/web_vs_paper.html",
            "guidlineAdherenceRate": "/static/views/guidlineAdherenceRate.html",
            "addTests": "/static/views/addTests.html",
        };

        $scope.template = templates[$scope.currentTest];

        $http.get('/api/test/metrics').then(function(response) {
            var web = response.data.webBased;
            var reporting = response.data.webBased;
            $scope.tests = [{
                name: "reportingRate",
                description: "Reporting Rate",
                metric: reporting + "%"
            }, {
                name: "webVsPaper",
                description: "Web VS Paper Reporting",
                metric: web + "%"
            }, {
                name: "guidlineAdherenceRate",
                description: "GuideLine Adherence Rate",
                metric: web + "%"
            }];
        });

        $scope.open = function() {

            var testSelectModal = $uibModal.open({
                templateUrl: '/static/views/choose_tests.html',
                controller: 'TestSelectionController',
                resolve: {
                    tests: function() {
                        return $scope.tests;
                    }
                }
            });

            testSelectModal.result.then(function(selectedItem) {
                $scope.selected = selectedItem;
            }, function() {});
        };
    }
])