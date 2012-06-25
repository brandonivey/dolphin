flipper = new Object();
flipper.active_flags = {{active_flags|safe}}.active_flags;
flipper.is_active = function(key) {
    for (var i = 0; i < flipper.active_flags.length; i++) {
        if ( flipper.active_flags[i] == key ) return true;
    }
    return false;
}
