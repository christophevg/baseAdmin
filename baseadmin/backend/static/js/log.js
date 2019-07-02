var Log = {
  template : `
<div>
  <h1>Logged Activity</h1>
  
  <v-expansion-panel popout>
    <v-expansion-panel-content v-for="(message, i) in messages" :key="i" hide-actions>
      <v-layout slot="header" align-left row spacer>
        <div style="float:left;width:125px; margin-right: 10px;">
          <v-btn depressed small block :color="buttonColor(message.client)" @click="gotoClient(message.client)">
            {{ message.client }}
          </v-btn>
        </div>
        <div>
          <span class="grey--text">{{ message.when | formatDate }}</span>
          <br>
          <span class="">{{ message.event }}</span>
        </div>
      </v-layout>

      <div style="margin-left: 25px;margin-bottom:10px;margin-right: 25px;"
           v-html="$options.filters.syntaxHighlight(message.info, 250)">
      </div>
    </v-expansion-panel-content> 
  </v-expansion-panel>
</div>`,
  computed: {
    messages : function() {
      return store.getters.logs();
    },
    buttonColor: function() {
      return function(client) {
        if( store.getters.group(client) ) {
          return "secondary";
        }
        if( store.getters.client(client) ) {
          return "primary";
        }
        return "white";
      }
    }
  },
  methods: {
    gotoClient: function(client) {
      if( store.getters.group(client) ) {
        return this.$router.push("/group/" + client);
      }
      if( store.getters.client(client) ) {
        return this.$router.push("/client/" + client);
      }
    }
  }
};
