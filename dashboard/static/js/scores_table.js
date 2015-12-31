$(document).ready(function() {
    var tableId = '#score-tables';
    var oTable = $(tableId).DataTable({
        "processing": true,
        "serverSide": true,
        "ordering": false,
        "fixedColumns": {
            leftColumns: 4
        },
        "scrollX": '100%',
        "scrollCollapse": true,
        "bLengthChange": false,
        "ajax": {
            "url": "/api/table/scores",
            "type": "POST",
            "data": function(d) {
                d.cycle = $('#cycle_select').val();
                d.warehouse = $('#warehouse_select').val();
                d.ip = $('#ip_select').val();
                d.formulation = $('#formulation_select').val();
                d.district = $('#district_select').val();
            }
        }
    });
    $(tableId).on('draw.dt', function() {
        $("td:contains('PASS')").addClass('score_PASS');
        $("td:contains('FAIL')").addClass('score_FAIL');
    });
    var selectIds = [
        '#district_select',
        '#warehouse_select',
        '#ip_select',
        '#cycle_select',
        '#formulation_select'
    ];
    var tags = {};
    var displayTags = function() {
        var tagsToDisplay = [];
        _.forIn(tags, function(value, key) {
            if (value) {
                tagsToDisplay.push({
                    'value': value
                })
            }
        });
        var template = $.templates("{{for tags}}<span class='filter-tag'>{{:value}}</span>{{/for}}");
        var html = template.render({
            tags: tagsToDisplay
        });
        $('#tags').html(html);
    };
    $('#resetFilter').click(function() {
        _.forEach(selectIds, function(id) {
            var firstValue = $(id + " option:first").val();
            $(id).select2('val', firstValue);
        });
    });
    _.forEach(selectIds, function(id) {
        var name = $(id).attr('name');
        $(id).select2();
        $(id).on('change', function(ev) {
            oTable.draw();
            var selectedValue = $(ev.target).val();
            var filter = $(ev.target).attr('name');
            tags[filter] = selectedValue;
            displayTags()
        });
    });

    _.forEach(['#cycle_select', '#formulation_select'], function(id) {
        var firstValue = $(id + " option:first").val();
        $(id).select2('val', firstValue);
    });

});