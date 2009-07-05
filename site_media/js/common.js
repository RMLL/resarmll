//<![CDATA[

function add_cart(url) {
    url = url.replace('/add/', '/addxjx/');
    jQuery.ajax({
        url: url,
        success: function(m) {
            jQuery.modal(m);
        }
    });
    return false;
}

function update_distribution(id) {
    jQuery('#'+id).addClass('modified');
    return false;
}

function reset_distribution(id) {
    jQuery('#'+id).removeClass('modified');
    return true;
}

function maximise_distribution(id) {
    jQuery('#'+id+' select').each(function (i, val) {
        jQuery(val.options[val.options.length-1]).attr("selected","selected");
    });
    return true;
}

//]]>
