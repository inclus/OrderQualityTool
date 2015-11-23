var dashboard = angular.module('dashboard', ['ui.router', 'chart.js']);
dashboard.config(function($stateProvider, $urlRouterProvider) {
    $urlRouterProvider.otherwise('/');
    $stateProvider
        .state('test', {
            url: '/:name',
            templateUrl: '/static/views/main.html',
            controller: function($scope, $stateParams) {
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
            }
        });
});

dashboard.controller('ReportingRateController', function($scope, $http) {
    $http.get('/api/test/reportingRate').then(function(response) {
        var values = response.data.values;
        $scope.labels = _.map(values, 'cycle');
        var items = _.map(values, 'count');
        $scope.series = ['Number of Facilities Reporting'];
        $scope.data = [items];
    });

});
