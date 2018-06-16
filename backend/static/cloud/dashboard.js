Vue.filter('formatDate', function(value) {
  if (value) {
    return moment(String(value)).format('DD/MM/YYYY HH:mm:ss')
  }
});

var Dashboard = {
  template : `
<v-layout justify-center column>
  <v-expansion-panel popout>
    <v-expansion-panel-content v-for="(master, i) in masters()" :key="i" hide-actions>
      <v-layout slot="header" align-center row spacer>

          <strong>{{ master._id }} @ {{ master.ip }}</strong> - last update: {{ master.last_modified | formatDate }}
          <span v-if="master.clients" class="grey--text">&nbsp;({{ master.clients.length }})</span>
      </v-layout>

      <div v-if="master.clients" style="margin-left: 25px;margin-bottom:10px;margin-right: 25px;">
        <v-layout wrap justify-space-around align-center>
          <v-btn v-for="client in master.clients" :key="client.title" @click="selectedClient(client.title); return false;"
                 :color="client.color" class="white--text" round>
            {{ client.name }}
          </v-btn>
        </v-layout>
      </div>

    </v-expansion-panel-content>
  </v-expansion-panel>
</v-layout>`,
  methods: {
    masters : function() {
      return store.getters.masters();
    }
  }
};
