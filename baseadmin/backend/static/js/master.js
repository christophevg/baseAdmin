var Master = {
  template : `
<div>
  <div v-if="master">
    <h1>{{ master.name }} @ {{ master.location }}</h1>
    <hr>
    <p style="margin:10px;">
      The following clients are connected to this master. You can add more by
      typing their name at the end of the list, confirming the name with
      'enter'. To disconnect a client from the master, use the X button next to
      the name of the client.
    </p>

    <div style="margin-top:15px;">
      <v-select v-model="clients" chips tags solo @input="accept">
        <template slot="selection" slot-scope="data">
         <v-chip v-if="data.item.name" :color="clientColor(data.item)" text-color="white" :selected="data.selected" close @input="release(data.item.name)">
           <strong>{{ data.item.name }}</strong>&nbsp;
         </v-chip>
        </template>
      </v-select>
    </div>

  </div>
</div>
`,
  data: function() {
    return {}
  },
  computed: {
    master: function() {
      return store.getters.client(this.$route.params.id);
    },
    clients: {
      get: function() {
        return store.getters.masterClients(this.$route.params.id);
      },
      set : function(newValue) { }
    }
  },
  methods: {
    clientColor: function(client) {
      return client.connected ? "green" : "red";
    },
    accept: function(data) {
      var client = data[data.length-1],
          master = this.$route.params.id;
      accept(client, master);
    },
    release: function(client) {
      release(client);
    }
  }
};
