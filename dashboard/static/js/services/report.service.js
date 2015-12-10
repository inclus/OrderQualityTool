angular.module('dashboard').service('ReportService', ['$http',
    function($http) {
        var handleResponse = function(response) {
            return response.data;
        };
        var getCycles = function() {
            return $http.get('/api/cycles').then(handleResponse);
        };

        var getMetrics = function() {
            return $http.get('/api/test/metrics').then(handleResponse);
        };

        var getBestRankings = function(level, selectedCycle) {
            return $http.get('/api/test/ranking/best', {
                params: {
                    level: level,
                    cycle: selectedCycle
                }
            }).then(handleResponse);
        };

        var getWorstRankings = function(level, selectedCycle) {
            return $http.get('/api/test/ranking/best', {
                params: {
                    level: level,
                    cycle: selectedCycle
                }
            }).then(handleResponse);
        };

        return {
            "getCycles": getCycles,
            "getMetrics": getMetrics,
            "getBestRankings": getBestRankings,
            "getWorstRankings": getWorstRankings
        };
    }
])