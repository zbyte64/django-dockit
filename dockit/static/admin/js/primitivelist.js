(function($) {
    $(document).ready(function() {
        $('.primitivelistfield').each(function() {
            var rows = '#'+$(this).attr('id')+' .list-row';
            var reinitDateTimeShortCuts = function() {
                // Reinitialize the calendar and clock widgets by force, yuck.
                if (typeof DateTimeShortcuts != "undefined") {
                    $(".datetimeshortcuts").remove();
                    DateTimeShortcuts.init();
                }
            }
            var updateSelectFilter = function() {
                // If any SelectFilter widgets were added, instantiate a new instance.
                if (typeof SelectFilter != "undefined"){
                    $(".selectfilter").each(function(index, value){
                      var namearr = value.name.split('-');
                      SelectFilter.init(value.id, namearr[namearr.length-1], false, "/static/admin/");
                    });
                    $(".selectfilterstacked").each(function(index, value){
                      var namearr = value.name.split('-');
                      SelectFilter.init(value.id, namearr[namearr.length-1], true, "/static/admin/");
                    });
                }
            }
            var initPrepopulatedFields = function(row) {
                row.find('.prepopulated_field').each(function() {
                    var field = $(this);
                    var input = field.find('input, select, textarea');
                    var dependency_list = input.data('dependency_list') || [];
                    var dependencies = [];
                    $.each(dependency_list, function(i, field_name) {
                      dependencies.push('#' + row.find(field_name).find('input, select, textarea').attr('id'));
                    });
                    if (dependencies.length) {
                        input.prepopulate(dependencies, input.attr('maxlength'));
                    }
                });
            }
            $(rows).formset({
                prefix: $(this).attr('data-prefix'),
                formCssClass: "dynamic-form",
                deleteCssClass: "inline-deletelink",
                deleteText: "Remove",
                emptyCssClass: "empty-row",
                added: (function(row) {
                    initPrepopulatedFields(row);
                    reinitDateTimeShortCuts();
                    updateSelectFilter();
                })
            });
        });
    });
})(django.jQuery);
