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
    var standardFormat = ''
        + '<blockquote class="twitter-tweet" data-conversation="none" data-cards="hidden">'
        + '<p>'+t.text+'</p>&mdash; '+t.user.name + ' (@'+t.user.screen_name+') '
        + '<a href="https://twitter.com/twitterapi/status/'+t.id_str+'">'+t.created_at+'</a>'               
        + '</blockquote>';
    var customFormat = ''
        + '<blockquote class="tweet subject expanded h-entry" data-tweet-id="' + t.id_str + '" cite="https://twitter.com/' + t.user.screen_name + '/status/' + t.id_str + '" data-scribe="section:subject">'
        + '<div class="header">'
        + '<div class="h-card p-author with-verification" data-scribe="component:author">'
        +'<a class="u-url profile" href="https://twitter.com/' + t.user.screen_name + '" aria-label="' + t.user.name + ' (screen name: ' + t.user.screen_name + ')" data-scribe="element:user_link">'
        + '<img class="u-photo avatar" alt="" src="' + t.user.profile_image_url + '" data-scribe="element:avatar">'
        + '<span class="full-name">'
        + '<span class="p-name customisable-highlight" data-scribe="element:name">' + t.user.name + '</span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;';
    if (t.user.verified) {
        customFormat += '<span class="verified" title="Verified Account" aria-label="Verified Account" data-scribe="element:verified_badge"><b>✔</b></span>';
    }
    customFormat += '</span>'
        + '<span class="p-nickname" dir="ltr" data-scribe="element:screen_name">@<b>' + t.user.screen_name + '</b></span>'
        + '</a>'
        + '</div>'
        + '<a class="follow-button profile" href="https://twitter.com/' + t.user.screen_name + '" role="button" data-scribe="component:followbutton" title="Follow ' + t.user.name + ' on Twitter"><i class="ic-button-bird"></i>Follow</a>'
        + '</div>'
        + '<div class="content e-entry-content" data-scribe="component:tweet">'
        + '<p class="e-entry-title">' + t.text + '</p>'
        + '<div class="dateline collapsible-container">'
        + '<a class="u-url customisable-highlight long-permalink" href="https://twitter.com/' + t.user.screen_name + '/status/' + t.id_str + '" data-datetime="2014-09-28T13:43:45+0000" data-scribe="element:full_timestamp"><time pubdate="" class="dt-updated" datetime="2014-09-28T13:43:45+0000" title="Time posted: ' + t.created_at + '(UTC)">' + t.created_at + '</time></a>'
        + '</div>'
        + '</div>'
        + '<div class="footer customisable-border" data-scribe="component:footer">'
        + '<span class="stats-narrow customisable-border"><span class="stats" data-scribe="component:stats">'
        + '<a href="https://twitter.com/' + t.user.screen_name + '/status/' + t.id_str + '" title="View Tweet on Twitter" data-scribe="element:retweet_count">'
        + '<span class="stats-retweets">'
        + '<strong>' + t.retweet_count + '</strong> Retweets'
        + '</span>'
        + '</a>'
        + '<a href="https://twitter.com/' + t.user.screen_name + '/status/' + t.id_str + '" title="View Tweet on Twitter" data-scribe="element:favorite_count">'
        + '<span class="stats-favorites">'
        + '<strong>59</strong> favorites'
        + '</span>'
        + '</a>'
        + '</span>'
        + '</span>'
        + '<ul class="tweet-actions" role="menu" aria-label="Tweet actions" data-scribe="component:actions">'
        + '<li><a href="https://twitter.com/intent/tweet?in_reply_to=' + t.in_reply_to_status_id_str + '" class="reply-action web-intent" title="Reply" data-scribe="element:reply"><i class="ic-reply ic-mask"></i><b>Reply</b></a></li>'
        + '<li><a href="https://twitter.com/intent/retweet?tweet_id=' + t.id_str + '" class="retweet-action web-intent" title="Retweet" data-scribe="element:retweet"><i class="ic-retweet ic-mask"></i><b>Retweet</b></a></li>'
        + '<li><a href="https://twitter.com/intent/favorite?tweet_id=' + t.id_str + '" class="favorite-action web-intent" title="Favorite" data-scribe="element:favorite"><i class="ic-fav ic-mask"></i><b>Favorite</b></a></li>'
        + '</ul>'
        + '</div>'
        + '</blockquote>'
    return standardFormat;
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

function getTweets(url) {
    var info = kango.getExtensionInfo();    
    var details = {
        url: info.search_url,
        method: 'GET',
        async: true,
        contentType: 'json',
        headers: { Accept: 'application/json' },
        params: {
            url: encodeURIComponent(url)
        }
    };
    xhr_send(details, function(error, response) {
        if(error) {
            $('#error').html('Error executing search ('+error+')');
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
            $('#error').html('Error checking authorization ('+error+')');
            $('#progress').hide();
        } else if(response.is_auth) {
            $('#error').html('');
            kango.browser.tabs.getCurrent(function(tab) {
                var url = tab.getUrl();
                
                if(url.match('^https?://')) {
                    getTweets(url);
                } else {
                    $('#error').html('Not available for this content');
                }
                $('#progress').hide();
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
