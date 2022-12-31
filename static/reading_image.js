function displayReadingImage(destElem, reading_reference, meter_number) {
            $(destElem).html('<img src="{{ url_for('static', filename='loading.gif') }}">');
            $.get('/bo/reading_fetch_images/' + reading_reference + '/' + meter_number).done(function(response) {
                if (!response.ok){
                    $(destElem).html(response['result']);
                }
                else {
                    location.assign("{{ url_for('auth_bo_bp.bo_login', _external=True) }}");
                }
            }).fail(function() {
                $(destElem).text("{{ _('Error: Could not contact server.') }}");
            });
        }