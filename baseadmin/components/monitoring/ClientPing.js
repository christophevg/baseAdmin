Vue.filter('formatEpoch', function(value) {
  if (value) {
    return moment(String(new Date(value).toISOString())).format('DD/MM/YYYY HH:mm:ss')
  }
});

Vue.component( "ClientPing", {
  template : `
<div>
  <center v-if="client">
    <span v-if="client.ping_start">
      <span><b>last</b>: {{ client.ping_start | formatEpoch }}</span><br>
    </span>
    <span v-if="client.ping_end">
      <span><b>round-trip-time</b>: {{ client.ping_end - client.ping_start }}ms</span><br>
    </span>
    <v-btn :loading="pinging" :disabled="! client.connected" @click="ping()" class="primary">Ping</v-btn>
  </center>
</div>`,
  computed: {
    client: function() {
      return store.getters.client(this.$route.params.id);
    },
    pingable: function() {
      return ! this.client.connected;
    }
  },
  methods: {
    ping: function() {
      this.pinging = true;
      ping(this.client.name);
      this.pinging = false;
    }
  },
  data: function() {
    return {
      pinging : false
    }
  }
});

app.registerClientComponent("Ping");
