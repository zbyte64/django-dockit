function showFragmentPopup(triggeringLink) {
    var name = triggeringLink.id.replace(/^lookup_/, '');
    name = id_to_windowname(name);
    href = triggeringLink.href
    if (href.indexOf('?') == -1) {
        href += '?_popup=1';
    } else {
        href  += '&_popup=1';
    }
    try {
    django.jQuery('#fragment_'+name).remove();
    django.jQuery(triggeringLink).after('<iframe id="fragment_'+name+'" src="'+href+'" height="50%" width="100%" style="border:none;"><p>Please Enable iframes</p></iframe>');
    } catch (exception) {
    console.log(exception)
    }
    //var win = window.open(href, name, 'height=500,width=800,resizable=yes,scrollbars=yes');
    //win.focus();
    return false;
}

function dismissFragmentPopup(win, newId, newRepr) {
    // newId and newRepr are expected to have previously been escaped by
    // django.utils.html.escape.
    newId = html_unescape(newId);
    newRepr = html_unescape(newRepr);
    var name = windowname_to_id(win.name).split('fragment_')[1];
    var elem = document.getElementById(name);
    if (elem) {
        if (elem.nodeName == 'SELECT') {
            var o = new Option(newRepr, newId);
            elem.options[elem.options.length] = o;
            o.selected = true;
        } else if (elem.nodeName == 'INPUT') {
            elem.value = newId;
        }
    } else {
        var toId = name + "_to";
        elem = document.getElementById(toId);
        var o = new Option(newRepr, newId);
        SelectBox.add_to_cache(toId, o);
        SelectBox.redisplay(toId);
    }
    var link = document.getElementById('lookup_'+name);
    if (link) {
        //update href, &fragment=newId
        if (link.href.search('fragment=') < 0) {
            link.href += '&fragment='+newId;
            django.jQuery(link).text('Edit');
            //TODO change text from add to edit
        }
    }
    django.jQuery('#fragment_'+name).remove();
}
