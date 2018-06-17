Vue.filter('formatDate', function(value) {
  if (value) {
    return moment(String(value)).format('DD/MM/YYYY HH:mm:ss')
  }
});

var Dashboard = {
  template : `
<v-layout justify-center column>
  <v-card v-for="(master, i) in masters()" :key="i">
    <v-card-title>
      <div style="width:100%;">
        <div style="float:left;margin-right:15px;">
          <v-btn color="primary" fab small dark @click="editMaster(master._id)">
            <v-icon>edit</v-icon>
          </v-btn>
        </div>
        <span>{{ master._id }} @ {{ master.ip }}</span><br>
        <span class="grey--text">last update: {{ master.last_modified | formatDate }}</span>
      </div>
    </v-card-title>
  </v-card>
</v-layout>
`,
  methods: {
    masters : function() {
      return store.getters.masters();
    },
    editMaster: function(master) {
      this.$router.push("/master/" + master);
    }
  }
};
