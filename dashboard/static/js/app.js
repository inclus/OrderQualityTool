var dashboard = angular.module('dashboard', ['ui.router', 'chart.js', 'ui.bootstrap', 'checklist-model']);
dashboard.config(['$stateProvider', '$urlRouterProvider',
    function($stateProvider, $urlRouterProvider) {
        $urlRouterProvider.otherwise('/reportingRate');
        $stateProvider
            .state('test', {
                url: '/:name',
                templateUrl: '/static/views/main.html',
                controller: 'HomeController'
            });
    }
]);