Vue.component( "PingComponent", {
  template : `
<div>
  <center v-if="this.$route.params.scope == 'client' && client">
    <span v-if="client.ping_start">
      <span><b>last</b>: {{ client.ping_start | formatEpoch }}</span><br>
      <span v-if="client.ping_end">
        <span><b>round-trip-time</b>: {{ client.ping_end - client.ping_start }}ms</span><br>
      </span>
    </span>
    <v-btn :loading="pinging" :disabled="! client.connected" @click="ping()" class="primary">Ping</v-btn>
  </center>
  <center v-if="group">
    <v-btn :loading="pinging" @click="ping()" class="primary">Ping</v-btn>
    <v-data-table
      v-if="groupClients"
      :headers="headers"
      :items="groupClients"
      class="elevation-1">
      <template slot="items" slot-scope="props" v-if="props.item.ping_end">
        <td>{{ props.item.name }}</td>
        <td class="text-xs-right">{{ props.item.ping_start | formatEpoch}}</td>
        <td class="text-xs-right">{{ props.item.ping_end - props.item.ping_start }}ms</td>
      </template>
    </v-data-table>
  </center>
</div>`,
  computed: {
    client: function() {
      return store.getters.client(this.$route.params.id);
    },
    group: function() {
      return store.getters.group(this.$route.params.id);
    },
    groupClients: function() {
      return store.getters.groupClients(this.$route.params.id);
    }
  },
  methods: {
    ping: function() {
      this.pinging = true;
      ping(this.$route.params.id);
      this.pinging = false;
    }
  },
  data: function() {
    return {
      pinging : false,
      headers: [
        { text: "Client",         value: "name" },
        { text: "Start",          value: "ping_start", align: "right" },
        { text: "Roud Trip Time", value: "rtt",        align: "right"  },
     ]
    }
  }
});

app.registerClientComponent("Ping");
app.registerGroupComponent("Ping");
