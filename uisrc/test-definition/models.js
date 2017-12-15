ModelHelper = {
    getFields: function (id, metaData) {
        var key = "fields" + id;
        if (metaData && key in metaData) {
            return metaData[key];
        }
        return [];
    },
    getFormulations: function (id, metaData) {
        var key = "formulations" + id;
        if (metaData && key in metaData) {
            return metaData[key];
        }
        return [];
    },
    getTracingFormulations: function (id, metaData) {
        var key = "tracing" + id;
        if (metaData && key in metaData) {
            return metaData[key];
        }
        return [];
    }
};

var newModel = function (id, name, metaData) {
    return Object.create({}, {
        id: {
            value: id,
            writable: true,
            enumerable: true
        },
        name: {
            value: name,
            writable: true,
            enumerable: true
        },
        fields: {
            value: ModelHelper.getFields(id, metaData),
            enumerable: true
        },
        formulations: {
            value: ModelHelper.getFormulations(id, metaData),
            enumerable: true
        },
        hasTrace: {
            value: false,
            writable: true,
            enumerable: true
        },
        tracingFormulations: {
            value: [],
            writable: true,
            enumerable: true
        }
    });
};

var newTracingModel = function (id, name, metaData) {
    return Object.create(newModel(id, name, metaData), {
        hasTrace: {
            value: true,
            enumerable: true
        },
        tracingFormulations: {
            value: ModelHelper.getTracingFormulations(id, metaData),
            enumerable: true
        }
    });
};

module.exports = {
    newTracingModel: newTracingModel,
    newModel: newModel
};