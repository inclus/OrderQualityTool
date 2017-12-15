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

var newModel = function (id, name, metaData, typeId) {
    return {
        id: id,
        name: name,
        selectId: typeId + id,
        fields: ModelHelper.getFields(id, metaData),
        formulations: ModelHelper.getFormulations(id, metaData),
        hasTrace: false
    };
};

var newTracingModel = function (id, name, metaData, typeId) {
    var model = newModel(id, name, metaData, typeId);
    model.hasTrace = true;
    model.tracingFormulations = ModelHelper.getTracingFormulations(id, metaData);
    return model;
};
module.exports = {
    newTracingModel: newTracingModel,
    newModel: newModel
};