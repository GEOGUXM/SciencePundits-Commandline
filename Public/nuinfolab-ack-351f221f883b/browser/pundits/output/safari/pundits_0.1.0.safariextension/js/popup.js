/* Check for Safari. It's not ideal to do browser sniffing, but Twitter
widgets seems to be broken on extensions in Safari. The result is that
pages are getting forwarded to an endpoint at syndication.twitter.com.

From: http://stackoverflow.com/a/9851769

At least Safari 3+: "[object HTMLElementConstructor]" */
var isSafari = Object.prototype.toString.call(window.HTMLElement).indexOf('Constructor') > 0;

// @callback = function(error, data.response)
function xhr_send(details, callback) {
    kango.console.log('xhr_send');
    kango.console.log(details);
    
    kango.xhr.send(details, function(data) {
        kango.console.log(data);
        if(data.status == 200 && data.response != null) {  
            callback(data.response.error, data.response || {});
        } else {
            callback(data.status || 'error');     
        } 
    });
}

// Check authorization
// @callback = function(error, response)
function authCheck(callback) {
    var info = kango.getExtensionInfo();

    kango.browser.tabs.getCurrent(function(tab) {
        var url = tab.getUrl();
        
        var details = {
            url: info.auth_url,
            method: 'GET',
            async: true,
            contentType: 'json',
            headers: { Accept: 'application/json' },
            params: {
                redirect: encodeURIComponent(url)
            }
        };
        xhr_send(details, callback);
    })
};


function getTweetHTML(t) {
    return ''
        + '<blockquote class="twitter-tweet" data-conversation="none" data-cards="hidden">'
        + '<p>'+t.text+'</p>&mdash; '+t.user.name + ' (@'+t.user.screen_name+') '
        + '<a href="https://twitter.com/twitterapi/status/'+t.id_str+'">'+t.created_at+'</a>'               
        + '</blockquote>';
}

function displayTweetList(tweets) {
    var html = '';
    
    for(var i = 0; i < tweets.length; i++) {
        html += getTweetHTML(tweets[i]);
    }
    
    $('#results').html(html);                
    if (!isSafari) {
        console.log('Not Safari -- loading Twitter widgets');
        twttr.widgets.load();        
    }
}

// @groups = [(key, [tweets]), ...]
function displayTweetGroups(groups) {
    var html = '';
    
    for(var i=0; i < groups.length; i++) {
        g = groups[i];
        
        html += '<div class="group">'
            + '<div class="group-header">'
            + '<div class="text">'+g[0]+'</div>'
            + '<div class="count">('+g[1].length+')</div>'
            + '</div>'
            + '<div class="group-body">';
        
        for(var j = 0; j < g[1].length; j++) {
            html += getTweetHTML(g[1][j]);
        }
        
        html += '</div></div>';
    }
    $('#results').html(html);  
    $('#results .group-header').click(function(event) {
        $(this).next().toggle();
    });
                  
    if (!isSafari) {
        console.log('Not Safari -- loading Twitter widgets');
        twttr.widgets.load();        
    }
}


// @callback(response)
function getContent(url, callback) {
    $('#progress_msg').html('Retrieving content...');
    
    var info = kango.getExtensionInfo();
    var details = {
        method: 'GET',
        async: true,
        contentType: 'json',
        headers: { Accept: 'application/json' },
        url: info.base_url+'content/',
        params: {url: encodeURIComponent(url)}
    };
    xhr_send(details, function(error, response) {
       if(error) {
            $('#error').html('Error getting content ('+error+')');
            $('#progress').hide();
        } else {
            callback(response);
        }
    });
}

// @callback([keywords])
function getKeywords(record, callback) {
    if('keywords' in record) {
        callback(record.keywords);
    } else {
        $('#progress_msg').html('Analyzing keywords...');

        var info = kango.getExtensionInfo();
        var details = {
            method: 'GET',
            async: true,
            contentType: 'json',
            headers: { Accept: 'application/json' },
            url: info.base_url+'keywords/'+record.id+'/'
        };
        xhr_send(details, function(error, response) {
           if(error) {
                $('#error').html('Error getting keywords ('+error+')');
                $('#progress').hide();
            } else if(!response.keywords.length) {
                $('#error').html('Error getting keywords (none found)');
                $('#progress').hide();                
            } else {
                callback(response.keywords);
            }
        });
    }
}

// @callback([categories])
function getCategories(record, callback) {
    if('categories' in record) {
        callback(record.categories);
    } else {
        $('#progress_msg').html('Analyzing category...');

        var info = kango.getExtensionInfo();
        var details = {
            method: 'GET',
            async: true,
            contentType: 'json',
            headers: { Accept: 'application/json' },
            url: info.base_url+'categories/'+record.id+'/'
        };
        xhr_send(details, function(error, response) {
           if(error) {
                $('#error').html('Error getting categories ('+error+')');
                $('#progress').hide();
            } else {
                callback(response.entities);
            }
        });
    }
}

function getTweets(url) {
    getContent(url, function(data) {
        getKeywords(data, function(keyword_list) {
            getCategories(data, function(entity_list) {
                $('#progress_msg').html('Searching for tweets...');
            
                var info = kango.getExtensionInfo();
                var details = {
                    method: 'GET',
                    async: true,
                    contentType: 'json',
                    headers: { Accept: 'application/json' },
                    url: info.base_url+'pundittweets/pundits/'+data.id+'/'
                }
                xhr_send(details, function(error, response) {
                    if(error) {
                        $('#error').html(error);
                    } else {
                        tweets = response.tweets;
                        if(tweets.length) {
                            if($.isArray(tweets[0])) {
                                displayTweetGroups(tweets);
                            } else {
                                displayTweetList(tweets);
                            }
                        } else {
                            $('#error').html('No tweets found');
                        }                    
                    }
                    $('#progress').hide();    
                });
            }); 
        });       
    });
}

function currentTabNavigate(url) {
    kango.browser.tabs.getCurrent(function(tab) {
        KangoAPI.closeWindow();
        tab.navigate(url);
    });
}

KangoAPI.onReady(function(event) {   
     // Multiple ready events are fired on FF, due to twttr.widgets.load()
    if(KangoAPI._readyFired) {
        return;
    }
        
    $('#infolab_link').click(function(event) {
        currentTabNavigate('http://infolab.northwestern.edu');
    });
    
    authCheck(function(error, response) {
        if(error) {            
            $('#error').html('Error checking authorization ('+error+'). Please try again.');
            $('#progress').hide();
        } else if(response.is_auth) {
            $('#error').html('');
            kango.browser.tabs.getCurrent(function(tab) {
                var url = tab.getUrl();
                
                if(url.match('^https?://')) {
                    getTweets(url);
                } else {
                    $('#error').html('Not available for this content');
                    $('#progress').hide();
                }
            });
        } else {
            $('#signin').show();
            $('#signin_button').click(function(event) {
                currentTabNavigate(response.auth_url);
            });
            $('#progress').hide();
        }    
    });
});
