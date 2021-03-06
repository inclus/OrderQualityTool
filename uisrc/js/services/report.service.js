angular.module("services").service("ReportService", ["$http",
    function ($http) {
        var handleResponse = function (response) {
            return response.data;
        };
        var getCycles = function () {
            return $http.get("/api/cycles").then(handleResponse);
        };

        var getBestRankings = function (level, selectedCycle, formulation) {
            return $http.get("/api/test/ranking/best", {
                params: {
                    level: level,
                    cycle: selectedCycle,
                    formulation: formulation
                }
            }).then(handleResponse);
        };

        var getWorstRankings = function (level, selectedCycle, formulation) {
            return $http.get("/api/test/ranking/worst", {
                params: {
                    level: level,
                    cycle: selectedCycle,
                    formulation: formulation
                }
            }).then(handleResponse);
        };

        var getDataForTest = function (test, params) {
            return $http.get("/api/test/" + test, {
                params: params
            }).then(handleResponse);
        };

        var getScores = function (params) {
            return $http.get("/api/scores/", {
                params: params
            }).then(handleResponse);
        };

        var getFilters = function () {
            return $http.get("/api/filters/").then(handleResponse);
        };

        var getRankingsAccess = function () {
            return $http.get("/api/rankingsAccess/").then(handleResponse);
        };

        var getAdminStatus = function () {
            return $http.get("/api/access/admin").then(handleResponse);
        };

        return {
            "getCycles": getCycles,
            "getBestRankings": getBestRankings,
            "getWorstRankings": getWorstRankings,
            "getDataForTest": getDataForTest,
            "getScores": getScores,
            "getFilters": getFilters,
            "getRankingsAccess": getRankingsAccess,
            "getAdminStatus": getAdminStatus,
        };
    }
]);
