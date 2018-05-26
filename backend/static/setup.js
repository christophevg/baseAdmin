var Setup = {
  template: `
  <div>
    <h1>Status</h1>
    <div v-if="status()" v-html="status()"></div>
    <div v-else>loading setup status...</div>
  </div>
`,
  methods: {
    status : function() {
      return store.getters.setupStatus();
    }
  }
};

(function() {

  $( document ).ready(function() {
    $.get( "/api/status", function( value ) {
      app.updateStatus(syntaxHighlight(JSON.stringify(value, null, 2)));
    });
  });

  function syntaxHighlight(json) {
    var json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
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
    return "<pre>" + html + "</pre>";
  }
  
})();