var chartService = ["$http", "$q",
    function ($http, $q) {
        var handleResponse = function (response) {
            return response.data;
        };
        var getDataForTest = function (test, params) {
            return $http.get("/api/test/" + test, {
                params: params
            }).then(handleResponse);
        };
        var getMetrics = function (params) {
            return $http.get("/api/test/metrics", {params: params}).then(handleResponse);
        };
        var getTests = function () {
            return $http.get("/api/test/list").then(handleResponse);
        };

        var buildOptions = function (test, district, ip, warehouse, startCycle, endCycle, regimen) {
            return getDataForTest(test.id, {
                start: startCycle,
                end: endCycle,
                ip: ip.ip,
                regimen: regimen,
                warehouse: warehouse.warehouse,
                district: district.district
            }).then(function (data) {
                var values = data.values;
                return options = {
                    data: values,
                    chart: {
                        legend: {
                            position: "right"
                        },

                        grid: {
                            y: {
                                show: true
                            }
                        },
                        axis: {
                            y: {
                                max: 100,
                                min: 0,
                                tick: {
                                    count: 5
                                },
                                padding: {
                                    top: 0,
                                    bottom: 0
                                }
                            }
                        }
                    },
                    dimensions: {
                        cycle: {
                            axis: "x",
                            type: "line"
                        },
                        yes: {
                            axis: "y",
                            type: "line",
                            name: "Pass",
                            color: "#27ae60",
                            dataType: "numeric",
                            displayFormat: d3.format(".1f")
                        },
                        no: {
                            axis: "y",
                            type: "line",
                            name: "Fail",
                            color: "red",
                            dataType: "numeric",
                            displayFormat: d3.format(".1f")
                        },
                        not_reporting: {
                            axis: "y",
                            type: "line",
                            color: "gray",
                            name: "Insufficient Data",
                            dataType: "numeric",
                            displayFormat: d3.format(".1f")
                        }
                    }
                };
            });
        };
        return {
            "getTests": getTests,
            "getMetrics": getMetrics,
            "buildOptions": buildOptions
        };
    }
];

var init = function (module) {
    module.service("chartsService", chartService);
};
module.exports = init;
