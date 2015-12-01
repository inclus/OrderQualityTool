angular.module('dashboard').controller('HomeController', ['$scope', '$stateParams', '$uibModal', '$http',
    function($scope, $stateParams, $uibModal, $http) {

        $scope.displayCycle = function(cycle) {
            return "CYCLE " + cycle.number + " '" + cycle.year;
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

        $scope.updateLists = function() {
            var test = $stateParams.name;
            $http.get('/api/test/' + test + '/bestDistricts', {
                params: {
                    cycle: $scope.selectedCycle
                }
            }).then(function(response) {
                $scope.bestDistricts = response.data.values;
            });
            $http.get('/api/test/' + test + '/worstDistricts', {
                params: {
                    cycle: $scope.selectedCycle
                }
            }).then(function(response) {
                $scope.worstDistricts = response.data.values;
            });
        };

        $scope.$watch('selectedCycle', function(cycle) {
            if (cycle) {
                $scope.updateLists();
            }
        });

        $scope.currentTest = $stateParams.name;
        var templates = {
            "reportingRate": "/static/views/reporting_rate.html",
            "webVsPaper": "/static/views/web_vs_paper.html"
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