var Master = {
  template : `
<div>
  <div v-if="master.state == 'loading'">
    Hold on, I'm fetching this master for you...
  </div>
  <div v-else> 
    <h1>{{ master._id }} @ {{ master.ip }}</h1>
    <hr>
    <p style="margin:10px;">

      The following clients are connected to this master. You can add more by
      typing their name at the end of the list, confirming the name with
      'enter'. To disconnect a client from the master, use the X button next to
      the name of the client.

    </p>
    <div style="margin-top:15px;">
      <v-select v-model="master.clients" chips tags solo append-icon="" @input="addClient">
        <template slot="selection" slot-scope="data">
         <v-chip :selected="data.selected" close @input="removeClient(data.item)">
           <strong>{{ data.item }}</strong>&nbsp;
         </v-chip>
        </template>
      </v-select>
    </div>

  </div>
</div>
`,
  data: function() {
    return {
      clients: []
    }
  },
  computed: {
    master: function() {
      return store.getters.master(this.$route.params.id);
    }
  },
  methods: {
    addClient: function(data) {
      var client = data[data.length-1];
      var update = { 
        "master": this.$route.params.id
      };
      var self = this;
      $.ajax( {
        url: "/api/client/" + client,
        type: "post",
        data: JSON.stringify(update),
        dataType: "json",
        contentType: "application/json",
        success: function(response) {
          update["client"] = client;
          store.dispatch("connect", update);
        },
        error: function(response) {
          app.$notify({
            group: "notifications",
            title: "Could not add client...",
            text:  response.responseJSON.message,
            type:  "error",
            duration: 10000
          });
          update["client"] = client;
          store.dispatch("disconnect", update);          
        }
      });
    },
    removeClient: function(client) {
      var update = { 
        "master": ""
      };
      var self = this;
      $.ajax( {
        url: "/api/client/" + client,
        type: "post",
        data: JSON.stringify(update),
        dataType: "json",
        contentType: "application/json",
        success: function(response) {
          update["client"] = client;
          store.dispatch("connect", update);
        },
        error: function(response) {
          app.$notify({
            group: "notifications",
            title: "Could not remove client...",
            text:  response.responseJSON.message,
            type:  "error",
            duration: 10000
          });
        }
      });
    }
  }
};
