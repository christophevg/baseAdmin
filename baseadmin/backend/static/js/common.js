function syntaxHighlight(obj, height) {
  try {
    var json = JSON.stringify(obj, null, 2);
    json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    var html = json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function (match) {
      var cls = 'number';
      if (/^"/.test(match)) {
        if (/:$/.test(match)) {
          cls = 'key';
        } else {
          cls = 'string';
        }
      } else if (/true|false/.test(match)) {
        cls = 'boolean';
      } else if (/null/.test(match)) {
        cls = 'null';
      }
      return '<span class="' + cls + '">' + match + '</span>';
    });
    return "<pre style='background-color: #eee; max-height:"+height+"px; overflow:auto;'>" + html + "</pre>";
  } catch(err) {
    return json;
  }
}

Vue.filter( "syntaxHighlight", syntaxHighlight);

Vue.filter('formatDate', function(value) {
  if (value) {
    return moment(String(value)).format('DD/MM/YYYY HH:mm:ss')
  }
});

Vue.filter('formatEpoch', function(value) {
  if (value) {
    return moment(String(new Date(value * 1000).toISOString())).format('DD/MM/YYYY HH:mm:ss')
  }
});

// https://stackoverflow.com/questions/105034/create-guid-uuid-in-javascript
function uuid() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

function log(event, client, info) {
  var message = { when: new Date().toString(), event: event, client: client, info: info };
  console.log( message.when, message.event, message.client, message.info );
  store.commit("log", message);
}
