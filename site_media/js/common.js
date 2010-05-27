//<![CDATA[

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

function gen_password(length) {
    var chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890";
    var pwd = '';
    for(x=0; x<length; x++) {
        pwd += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return pwd;
}

function replace_accents(s) {
    var r = s.toLowerCase();
    r = r.replace(new RegExp("\\s", 'g'),"");
    r = r.replace(new RegExp("[àáâãäå]", 'g'),"a");
    r = r.replace(new RegExp("æ", 'g'),"ae");
    r = r.replace(new RegExp("ç", 'g'),"c");
    r = r.replace(new RegExp("[èéêë]", 'g'),"e");
    r = r.replace(new RegExp("[ìíîï]", 'g'),"i");
    r = r.replace(new RegExp("ñ", 'g'),"n");
    r = r.replace(new RegExp("[òóôõö]", 'g'),"o");
    r = r.replace(new RegExp("œ", 'g'),"oe");
    r = r.replace(new RegExp("[ùúûü]", 'g'),"u");
    r = r.replace(new RegExp("[ýÿ]", 'g'),"y");
    r = r.replace(new RegExp("\\W", 'g'),"");
    return r;
}

function createform_gen_password(id1, id2) {
    var pwd = gen_password(8);
    $('#'+id1).val(pwd);
    $('#'+id2).val(pwd);
}

function createform_gen_username(firstname,lastname,username) {
    return $('#'+username).val(replace_accents($('#'+firstname).val())+'.'+replace_accents($('#'+lastname).val()));
}

function createform_gen_email(firstname,lastname,email,domain) {
    return $('#'+email).val(replace_accents($('#'+firstname).val())+'.'+replace_accents($('#'+lastname).val())+'@'+domain);
}

//]]>
