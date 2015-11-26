var dashboard = angular.module('dashboard', ['ui.router', 'chart.js', 'ui.bootstrap', 'checklist-model']);
dashboard.config(function($stateProvider, $urlRouterProvider) {
    $urlRouterProvider.otherwise('/reportingRate');
    $stateProvider
        .state('test', {
            url: '/:name',
            templateUrl: '/static/views/main.html',
            controller: function($scope, $stateParams, $uibModal, $http) {
                $http.get('/api/cycles').then(function(response) {
                    $scope.cycles = response.data.values;
                    $scope.selectedCycle = $scope.cycles[0];
                });
                $scope.updateLists = function() {
                    $http.get('/api/test/reportingRate/bestDistricts', {
                        params: {
                            cycle: $scope.selectedCycle
                        }
                    }).then(function(response) {
                        $scope.bestDistricts = response.data.values;
                    });
                    $http.get('/api/test/reportingRate/worstDistricts', {
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

                $scope.tests = [{
                    name: "reportingRate",
                    description: "Reporting Rate",
                    metric: "X%"
                }, {
                    name: "webVsPaper",
                    description: "Web VS Paper Reporting",
                    metric: "X%"
                }];
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
    $http.get('/api/test/reportingRate').then(function(response) {
        var values = response.data.values;
        $scope.labels = _.map(values, 'cycle');
        var items = _.map(values, 'rate');
        $scope.series = ['Reporting Rate'];
        $scope.data = [items];
        $scope.options = {
            scaleOverride: true,
            scaleSteps: 10,
            scaleStepWidth: 10,
            scaleStartValue: 0
        };
    });
});


dashboard.controller('WebBasedRateController', function($scope, $http) {
    $http.get('/api/test/webBased').then(function(response) {
        var values = response.data.values;
        $scope.labels = _.map(values, 'cycle');
        var items = _.map(values, 'rate');
        $scope.series = ['Web Based Reporting Rate'];
        $scope.data = [items];
        $scope.options = {
            scaleOverride: true,
            scaleSteps: 10,
            scaleStepWidth: 10,
            scaleStartValue: 0
        };
    });
});

dashboard.controller('TestSelectionController', function($scope, tests, $uibModalInstance) {
    $scope.allTests = [{
        name: "reportingRate",
        description: "Reporting Rate",
        metric: "X%"
    }, {
        name: "webVsPaper",
        description: "Web VS Paper Reporting",
        metric: "X%"
    }];
    $scope.ok = function() {
        $uibModalInstance.close($scope.selectedTests);
    };

    $scope.cancel = function() {
        $uibModalInstance.dismiss('cancel');
    };
    $scope.selectedTests = tests;
});