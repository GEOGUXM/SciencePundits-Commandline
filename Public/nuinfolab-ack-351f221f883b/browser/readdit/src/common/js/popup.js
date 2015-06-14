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

function displayKeywords(keywords) {
    if(keywords.length) {
        var k = [];
        for(var i = 0; i < keywords.length; i++) {
            k.push(keywords[i].keyword);
        }    
        $('#keywords').html(k.join(', '));  
    } else {
        $('#keywords').html('No keywords found');
    }
}

function displayReddits(reddits) {
    if(reddits.length) {
        var html = '';   
        for(var i = 0; i < reddits.length; i++) {
            html += '<li><a target="_blank" href="http://www.reddit.com'+reddits[i].data.permalink+'">'
                    +reddits[i].data.title+'</a></li>';                       
        }
        $('#threads').html(html);
    } else {
        $('#threads').html('No related Reddit threads found');
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
            } else {
                callback(response.keywords);
            }
        });
    }
}

// @callback([{reddits}])
function getReddits(query, callback) {
    $('#progress_msg').html('Searching Reddit...');
    
    if(query) {  
        var info = kango.getExtensionInfo();
        var details = {
            method: 'GET',
            async: true,
            contentType: 'json',
            headers: {Accept: 'application/json'},
            url: 'http://www.reddit.com/search.json?q='+query+'&sort=relevance&t=month&limit=10'
        };
        xhr_send(details, function(error, response) {
           if(error) {
                $('#error').html('Error searching Reddit ('+error+')');
                $('#progress').hide();
            } else if(!response.data) {
                callback([]);
            } else if(!response.data.children) {
                callback([]);
            } else {
                callback(response.data.children);
            }
        });    
    } else {
        callback([]);
    }
}

function doReaddit(url) {
    getContent(url, function(data) {
        getKeywords(data, function(keyword_list) {
            displayKeywords(keyword_list);

            var k = [];
            for(var i = 0; i < Math.min(keyword_list.length, 3); i++) {
                k.push(keyword_list[i].keyword);
            }
            var q = k.join('+');
                                
            // Search by url, then by keywords
            getReddits(url, function(reddits_by_url) {            
                getReddits(q, function(reddits_by_key) {
                    // De-dupe reddits
                    for(var i = reddits_by_key.length - 1; i >= 0; i--) {
                        var r = reddits_by_key[i];
                        
                        for(var j = 0; j < reddits_by_url.length; j++) {
                            if(r.data.id == reddits_by_url[j].data.id) {
                                reddits_by_key.splice(i, 1);
                                break;
                            }
                        }
                    }
                    
                    displayReddits(reddits_by_url.concat(reddits_by_key));
                    $('#progress').hide();    
                    $('#results').show();
                });
            });
/*                   
            if(keyword_list.length) {
                $('#progress_msg').html('Searching Reddit...');

                // Use first three keywords as query
                var k = [];
                for(var i = 0; i < Math.min(keyword_list.length, 3); i++) {
                    k.push(keyword_list[i].keyword);
                }
                var q = k.join('+');
                
                // https://www.reddit.com/dev/api#GET_search
                // {data: {children: [ {data: {permalink: '', 'title': '', ...}} ] }}                               
                var info = kango.getExtensionInfo();
                var details = {
                    method: 'GET',
                    async: true,
                    contentType: 'json',
                    headers: {Accept: 'application/json'},
                    url: 'http://www.reddit.com/search.json?q='+q+'&sort=relevance&t=month&limit=10'
                };
                xhr_send(details, function(error, response) {
                    if(error) {
                        $('#error').html(error);                        
                    } else if(!response.data) {
                        $('#error').html('Expected "data" in Reddit response');                        
                    } else if(!response.data.children) {
                        $('#error').html('Expected "data.children" in Reddit response');                        
                    } else {
                        displayReddits(response.data.children);
                    }
                    
                    $('#progress').hide();    
                    $('#results').show();
                });   
            } else {
                $('#progress').hide();
                $('#results').show();
            }    
*/              
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
    
    // note: there is no authCheck for this plugin
    
    $('#error').html('');
    kango.browser.tabs.getCurrent(function(tab) {
        var url = tab.getUrl();
        
        if(url.match('^https?://')) {
            doReaddit(url);
        } else {
            $('#error').html('Not available for this content');
            $('#progress').hide();
        }
    });
});
