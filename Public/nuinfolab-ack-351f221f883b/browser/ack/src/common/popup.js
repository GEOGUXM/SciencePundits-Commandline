var StorageTest = {

    init: function() {
        $('#storage-get').click(function(event) {
            StorageTest.testGet();
        });

        $('#storage-set').click(function(event) {
            StorageTest.testSet();
        });

        $('#storage-remove').click(function(event) {
            StorageTest.testRemove();
        });

        $('#storage-keys').click(function(event) {
            StorageTest.testKeys();
        });
    },

    testGet: function() {
        $('#storage-value').val(kango.storage.getItem($('#storage-key').val()) || 'null');
    },

    testSet: function() {
        kango.storage.setItem($('#storage-key').val(), $('#storage-value').val());
    },

    testRemove: function() {
        kango.storage.removeItem($('#storage-key').val());
        $('#storage-value').val('null');
    },

    testKeys: function() {
        $('#storage-value').val(kango.storage.getKeys().toString());
    }
};

var WindowTest = {
    
    close: function() {
        KangoAPI.closeWindow()
    },
    
    resize: function() {
        var defaultRows = 4;
        var maximizedRows = 8;
        if ($('#popup-properies').attr('rows') == defaultRows) {
            KangoAPI.resizeWindow(600, 600);
            $('#popup-properies').attr('rows', maximizedRows);
            
        }
        else { 
            $('#popup-properies').attr('rows', defaultRows);
            KangoAPI.resizeWindow(600, 520); 
        }
    }
};

var showCurrentUrl = function() {
    kango.browser.tabs.getCurrent(function(tab) {
        $('#current-url').val(tab.getUrl());
    });
};


var getContent = function() {
    kango.browser.tabs.getCurrent(function(tab) {
        var details = {
            url: 'http://localhost:5000/content?url=' + tab.getUrl(),
            method: 'GET',
            async: true,
            contentType: 'json'
        };
        kango.xhr.send(details, function(data) {
            $('#content-title').html((data.status == 200 && data.response != null) ? data.response.title : 'Error. Status=' + data.status);
            $('#content-text').html((data.status == 200 && data.response != null) ? data.response.text : '');
        });
    });
}

var getEntities = function() {
    kango.browser.tabs.getCurrent(function(tab) {
        var details = {
            url: 'http://localhost:5000/entities?url=' + tab.getUrl(),
            method: 'GET',
            async: true,
            contentType: 'json'
        };
        kango.xhr.send(details, function(data) {
            if (data.status == 200 && data.response != null) {
                $.each(data.response.entities, function(i, entity) {
                    $('#entities').append('<p><strong>' + entity.name + '</strong> (' + entity.type + ')</p>');
                });
            } else {
                $('#entities').append('<p>' + data.status + '</p>');
            }
        });
    });
}


var getStakeholders = function() {
    kango.browser.tabs.getCurrent(function(tab) {
        var details = {
            url: 'http://localhost:5000/stakeholders?url=' + tab.getUrl(),
            method: 'GET',
            async: true,
            contentType: 'json'
        };
        kango.xhr.send(details, function(data) {
            if (data.status == 200 && data.response != null) {
                $.each(data.response.stakeholders, function(i,stakeholder){
                    $('#stakeholders').append('<p><strong>' + stakeholder.name + '</strong></p><ul></ul>');
                    $.each(stakeholder.twitter_users, function(uidx, user) {
                        $('#stakeholders ul').append('<li>@' + user.screen_name + '</li>');
                    });
                });
                //$('#stakeholders').append('</ul>');
            } else {
                $('#stakeholders').append('<p>' + data.status + '</p>');
            }
        });
    });
}


KangoAPI.onReady(function() {
    $('#ready').show();
    $('#not-ready').hide();

    showCurrentUrl();

    $('#form').submit(function() {
        return false;
    });

    $('#popup-close').click(function(event) {
        WindowTest.close();
    });

    $('#popup-resize').click(function(event) {
        WindowTest.resize();
    });

    $('#get-content').click(function(event) {
        getContent();
    });

    $('#get-entities').click(function(event) {
        getEntities();
    });

    $('#get-stakeholders').click(function(event) {
        getStakeholders();
    });

    StorageTest.init();
});
