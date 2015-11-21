var dashboard = angular.module('dashboard', ['ui.router', 'chart.js']);
dashboard.config(function($stateProvider, $urlRouterProvider) {
    $urlRouterProvider.otherwise('/');
    $stateProvider
        .state('home', {
            url: '/',
            templateUrl: '/static/views/home.html',
            controller: function($scope) {
                $scope.labels = ["January", "February", "March", "April", "May", "June", "July"];
                $scope.series = ['Series A', 'Series B'];
                $scope.data = [
                    [65, 59, 80, 81, 56, 55, 40],
                    [28, 48, 40, 19, 86, 27, 90]
                ];
                $scope.onClick = function(points, evt) {
                    console.log(points, evt);
                };
            }
        });
});
