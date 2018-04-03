// Credits goes to https://blog.heroku.com/in_deep_with_django_channels_the_future_of_real_time_apps_in_django

$(function() {

//    // When using HTTPS, use WSS too.
//    var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
//    var chatsock = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host + "/chat");
    var chat_zone = $("#chat_zone");
//    
//    chatsock.onmessage = function(message) {
//        var data = JSON.parse(message.data);
//        chat_zone.prepend(
//            $("<p class='answer'></p>").text('Bot: ' + data.message)
//        );
//    };
//
    $("#chat_form").on("submit", function(event) {

        try {
            var message_elem = $('#message');
            var message_val = message_elem.val();

            if (message_val) {
                // Send the message
                var message = {
                    sender: "die-316182003",
                    message: message_val
                };
                
                httpPostAsync("./chat/receive",
				    JSON.stringify(message),
				    function(postResponse){
                          var responseJSON = JSON.parse(postResponse);
						  var responseStr = JSON.stringify(responseJSON)
				    	  console.log("post resonse:" + responseStr);
                          for (var i = 0;i<responseJSON.length;i++) {
                              chat_zone.prepend(
                                $("<p class='answer'></p>").text('Bot: ' + responseJSON[i])
                              );
                          }
                    },
				    function(){
				    	console.log("404 err");
				    });
                
//                chatsock.send(JSON.stringify(message));
                message_elem.val('').focus();

                // Add the message to the chat
                chat_zone.prepend(
                    $("<p class='question'></p>").text('You: ' + message_val)
                );
            }
        }
        catch(err) {
            console.error(err.message);
        }

        return false;
    });
    
    function httpPostAsync(url, params, callback,fallback) {
		var ignore404 = false;
		var xmlHttp = new XMLHttpRequest();
		xmlHttp.onreadystatechange = function() {
			if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
			{
				ignore404 = true;
				callback(xmlHttp.responseText);
			}
		}
		xmlHttp.open("POST",url, true); // true for asynchronous

		xmlHttp.setRequestHeader("Content-Type",
				"application/json;charset=UTF-8");
		xmlHttp.withCredentials = false;
		xmlHttp.send(params);
		
		
		var delayTime;	
		
		setTimeout(function(){
			if(ignore404 == false)
			{
				fallback();
			}
			else
			{
				console.log("has response,ignore 404");
				ignore404 = false;
			}	
		},delayTime);
	}
});
