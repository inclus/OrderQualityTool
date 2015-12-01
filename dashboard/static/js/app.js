var dashboard = angular.module('dashboard', ['ui.router', 'chart.js', 'ui.bootstrap', 'checklist-model']);
dashboard.config(function($stateProvider, $urlRouterProvider) {
    $urlRouterProvider.otherwise('/reportingRate');
    $stateProvider
        .state('test', {
            url: '/:name',
            templateUrl: '/static/views/main.html',
            controller: function($scope, $stateParams, $uibModal, $http) {

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
        });
});

dashboard.controller('ReportingRateController', function($scope, $http) {
    var update = function(start, end) {
        $http.get('/api/test/reportingRate', {
            params: {
                start: start,
                end: end,
            }
        }).then(function(response) {
            var values = response.data.values;
            $scope.labels = _.map(values, 'cycle');
            var items = _.map(values, 'rate');
            $scope.series = ['Reporting Rate'];
            $scope.data = [items];
            $scope.options = {
                scaleOverride: true,
                scaleSteps: 10,
                scaleStepWidth: 10,
                scaleStartValue: 0,
                scaleLineColor: "#42BE73"
            };
            $scope.colors = ["#42BE73"];
        });
    };
    $scope.$watch('startCycle', function(start) {
        if (start) {
            update($scope.startCycle, $scope.endCycle);
        }

    }, true);

    $scope.$watch('endCycle', function(end) {
        if (end) {
            update($scope.startCycle.name, $scope.endCycle.name);
        }

    }, true);
});


dashboard.controller('WebBasedRateController', function($scope, $http) {

    var update = function(start, end) {
        $http.get('/api/test/webBased', {
            params: {
                start: start,
                end: end,
            }
        }).then(function(response) {
            var values = response.data.values;
            $scope.labels = _.map(values, 'cycle');
            var items = _.map(values, 'rate');
            $scope.series = ['Web Based Reporting Rate'];
            $scope.data = [items];
            $scope.options = {
                scaleOverride: true,
                scaleSteps: 10,
                scaleStepWidth: 10,
                scaleStartValue: 0,
                scaleLineColor: "#42BE73",
                strokeColor: "#42BE73",
            };
            $scope.colors = ["#42BE73"];
        });
    };
    $scope.$watch('startCycle', function(start) {
        if (start) {
            update($scope.startCycle.name, $scope.endCycle.name);
        }

    }, true);

    $scope.$watch('endCycle', function(end) {
        if (end) {
            update($scope.startCycle.name, $scope.endCycle.name);
        }

    }, true);
});