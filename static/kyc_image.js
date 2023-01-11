function displayImage(destElem, params, contract_number){
    // $(destElem).html('<img src="{{ url_for('static', filename='loading.gif') }}">'));
    $.get('/bo/customers_fetch_images/' + contract_number + '/' + params).done(function(response) {
    if (!response.ok){
        $(destElem).html(response['result'])
    }
    else {
        location.assign("{{ url_for('auth_bo_bp.bo_login', _external=True) }}");
    }
    }).fail(function() {
                $(destElem).text("{{ _('Error: Could not contact server.') }}");
            });
}




