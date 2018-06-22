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
          <v-btn color="green" fab small dark @click="visitMaster(master.ip)">
            <v-icon>link</v-icon>
          </v-btn>
        </div>
        <div style="float:right;margin-right:15px;">
          <v-btn color="red" fab small dark @click="deleteMaster(master._id)">
            <v-icon>delete</v-icon>
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
    editMaster: function(id) {
      this.$router.push("/master/" + id);
    },
    visitMaster: function(ip) {
      window.open("http://" + ip + ":5000",'_blank');
    },
    deleteMaster: function(id) {
      var self = this;
      $.ajax( {
        url: "/api/master/" + id,
        type: "delete",
        data: "",
        dataType: "json",
        contentType: "application/json",
        success: function(response) {
          store.commit("deleteMaster", id);
        },
        error: function(response) {
          app.$notify({
            group: "notifications",
            title: "Could not remove master...",
            text:  response.responseJSON.message,
            type:  "error",
            duration: 10000
          });
        }
      });
    }    
  }
};
