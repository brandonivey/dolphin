(function($) {
    $(function() {
        // Only continue to process if this a Dolphin change form admin page.
        if ($('body').is(':not(.change-form)')) {
            return;
        }

        function DisableCheckboxes(id) {
            // Toggle this object's checkbox enable/disable state with the one passed in.
            if ($(this).is(':checked')) {
                 $("#"+id).attr({
                    'checked':false,
                    'disabled':true
                });
            } else {
                $("#"+id).attr('disabled',false);
            }
        }

        $("#id_enable_for_sites").click(function() { DisableCheckboxes.call(this, 'id_disable_for_sites'); })
        $("#id_disable_for_sites").click(function() { DisableCheckboxes.call(this, 'id_enable_for_sites'); })
 
        // Create a control to attach the slider to
        $('.percent input').after('<span class="slider" />');
        var percent_value = $('.percent input').val();
        $('.percent .slider').slider({
            range:"min",
            animate: true,
            value: percent_value,
            min: 0,
            max: 100,
            slide: function( event, ui ) {
               //Its setting the slider value to the element with id "amount"
                $( "#id_percent" ).val(  ui.value  );
            }
        });

    }); // end of onready callback
})(django.jQuery); // end of closure
