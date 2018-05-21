var Dashboard = {
  template : `
<v-layout justify-center column>
  <v-subheader>Groups</v-subheader>
  <v-expansion-panel popout>
    <v-expansion-panel-content v-for="(group, i) in groups()" :key="i" hide-actions>
      <v-layout slot="header" align-center row spacer>
        <v-flex xs4 sm2 md1>
          <v-avatar slot="activator" size="36px">
            <v-icon :color="group.color" large>{{ group.icon }}</v-icon>
          </v-avatar>
        </v-flex>
        <v-flex sm5 md3 hidden-xs-only>
          <strong v-html="group.name"></strong>
          <span v-if="group.total" class="grey--text">&nbsp;({{ group.total }})</span>
        </v-flex>
        <v-flex v-if="group.excerpt" class="grey--text" ellipsis hidden-sm-and-down>
          &mdash;
          {{ group.excerpt }}
        </v-flex>
      </v-layout>

      <div style="float:left;margin-left:15px;">
      <v-btn color="primary" fab small dark @click="editGroup(group)">
        <v-icon>edit</v-icon>
      </v-btn>
    </div>

      <div style="margin-left: 25px;margin-bottom:10px;margin-right: 25px;">
        <v-layout wrap justify-space-around align-center>
          <v-btn v-for="client in group.clients" :key="client.title" @click="selectedClient(client.title); return false;"
                 :color="client.color" class="white--text" round>
            {{ client.title }}
          </v-btn>
        </v-layout>
      </div>

    </v-expansion-panel-content>
  </v-expansion-panel>
</v-layout>`,
  methods: {
    groups : function() {
      return store.getters.groups();
    },
    selectedClient: function(client) {
      this.$router.push('/client');
    },
    editGroup : function(group) {
      console.log("edit group " + group);
    }
  }
};

(function() {

  $( document ).ready(function() {
    $.get( "/api/status", function( value ) {
      $("#status").html( syntaxHighlight(JSON.stringify(value, null, 2)) );
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
