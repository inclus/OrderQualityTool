$(document).ready(function() {
    var tableId = '#score-tables';
    var oTable = $(tableId).DataTable({
        "processing": true,
        "serverSide": true,
        "ordering": true,
        "fixedColumns": {
            leftColumns: 4
        },
        "aoColumnDefs": [{
            'bSortable': false,
            'aTargets': [0, 1, 2, 3,4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]
        }],
        "scrollX": '100%',
        "scrollCollapse": true,
        "bLengthChange": true,
        "ajax": {
            "url": "/api/table/scores",
            "type": "POST",
            "data": function(d) {
                d.cycle = $('#cycle_select').val();
                d.warehouse = $('#warehouse_select').val();
                d.ip = $('#ip_select').val();
                d.formulation = $('#formulation_select').val();
                var list_of_districts = $('#district_select').val();
                if (list_of_districts) {
                    var districts_text = list_of_districts.join(",");
                    d.district = districts_text;
                }

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
                if (key == "district") {
                    for (var i = 0; i < value.length; i++) {
                        tagsToDisplay.push({
                            'value': value[i]
                        })
                    };
                } else {
                    tagsToDisplay.push({
                        'value': value
                    });
                }

            }
        });
        var template = $.templates("{{for tags}}<span class='filter-tag'>{{:value}}</span>{{/for}}<a href='#' id='resetFilter' class='btn btn-sm reset-tag'>Reset</a>");
        var html = template.render({
            tags: tagsToDisplay
        });
        $('#tags').html(html);
        $('#resetFilter').click(function() {
            _.forEach(selectIds, function(id) {
                var firstValue = $(id + " option:first").val();
                $(id).select2('val', firstValue);
            });
        });

    };
    
    _.forEach(selectIds, function(id) {
        var name = $(id).attr('name');
        if (id == '#district_select') {
            $(id).select2({
                placeholder: "ALL DISTRICTS"
            });
        } else {
            $(id).select2();
        }


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

    $("[name='score-tables_length']").removeClass();

});
